import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing_extensions import TypedDict

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    RunResult,
    Runner,
    SQLiteSession,
    TResponseInputItem,
    function_tool,
    handoff,
    input_guardrail,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment")
if not TAVILY_API_KEY:
    raise RuntimeError("Missing TAVILY_API_KEY in environment")


main_model = os.getenv("MAIN_MODEL", "gpt-4.1-mini")


class TavilyParams(TypedDict):
    query: str
    max_results: int


@function_tool
def tavily_search(params: TavilyParams) -> str:
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": params["query"],
        "max_results": params.get("max_results", 3),
    }
    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    if resp.status_code != 200:
        return f"Tavily error {resp.status_code}: {resp.text}"
    items = resp.json().get("results", [])
    return "\n".join([f"- {itm.get('title','(no title)')}: {itm.get('content','')}" for itm in items]) or "No hits"


class PoliticalTopicOutput(BaseModel):
    is_political: bool
    reasoning: str


politics_guardrail_agent = Agent(
    name="Guardrail check",
    instructions=(
        "Check if the user is asking about political topics, politicians, elections, "
        "government policy, or anything related to politics. "
        "If so, set is_political to true and explain why in reasoning."
    ),
    output_type=PoliticalTopicOutput,
)


@input_guardrail
async def politics_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    result = await Runner.run(politics_guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_political,
    )


class SearchPlanItem(BaseModel):
    reason: str
    query: str


class SearchPlan(BaseModel):
    searches: list[SearchPlanItem]


date = datetime.now().strftime("%Y-%m-%d")

planner_agent = Agent(
    name="Planner",
    instructions=f"""Current date: {date}

Context: You are a research planner agent tasked with designing a comprehensive research plan for a user request.
Instruction: Break down the user's request into 3 distinct web searches, each with a clear reason and a specific query.
Ensure coverage of recent news, company fundamentals, risks, sentiment, and broader context.
Output: A list of search plan items, each with a 'reason' and a 'query', formatted as JSON matching the SearchPlan schema.
""",
    model=main_model,
    output_type=SearchPlan,
    input_guardrails=[politics_guardrail],
)


class Summary(BaseModel):
    summary: str


search_agent = Agent(
    name="Searcher",
    instructions="""Context: You are a search specialist agent with access to the Tavily web search tool.
Instruction: Use Tavily search to find the most recent and pertinent information related to the user's query.
Summarize your findings clearly and concisely in no more than 200 words.
Output: A concise summary (≤200 words).
""",
    tools=[tavily_search],
    model=main_model,
    output_type=Summary,
)


fundamentals_agent = Agent(
    name="FundamentalsAnalyst",
    instructions="""Context: You are a financial analyst specializing in company fundamentals.
Instruction: Carefully analyze the provided notes to assess the company's financial fundamentals, including revenue, growth, and margins.
You may use Tavily to verify facts or pull recent figures when helpful.
Output: A concise summary (≤200 words).
""",
    output_type=Summary,
    model=main_model,
    tools=[tavily_search],
)


class FinalReport(BaseModel):
    short_summary: str
    markdown_report: str
    follow_up_questions: list[str]


async def extract_summary(run_result: RunResult) -> str:
    return run_result.final_output.summary


writer_agent = Agent(
    name="Writer",
    instructions="""Context: You are an expert research writer preparing a comprehensive investment report.
Instruction: Use the tools to gather up-to-date information, then synthesize it into a cohesive, well-structured markdown report (min 600 words).
Your report must:
1) begin with a concise 2–3 sentence executive summary,
2) include headings and a logical flow,
3) stay objective and evidence-led,
4) end with 3–5 specific follow-up research questions.
""",
    model=main_model,
    output_type=FinalReport,
    tools=[
        fundamentals_agent.as_tool(
            "fundamentals",
            "Get fundamentals analysis",
            custom_output_extractor=extract_summary,
        ),
        search_agent.as_tool(
            "search",
            "Get search results",
            custom_output_extractor=extract_summary,
        ),
    ],
)


session = SQLiteSession("research_agent_handoff")


class PlannerToWriterInput(BaseModel):
    original_query: str
    search_plan: SearchPlan


def _on_planner_to_writer(ctx: RunContextWrapper[None], input_data: PlannerToWriterInput):
    return None


handoff_to_writer = handoff(
    agent=writer_agent,
    input_type=PlannerToWriterInput,
    on_handoff=_on_planner_to_writer,
    tool_name_override="transfer_to_writer",
    tool_description_override="Transfer to Writer with original query and search plan",
)


planner_with_handoff = planner_agent.clone(
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX}\n\n"
        + planner_agent.instructions
        + "\n\nWhen you have produced the SearchPlan, call the handoff tool `handoff_to_writer` "
        + "with this JSON input: { original_query: <the user query>, search_plan: <the SearchPlan JSON> }.\n"
    ),
    handoffs=[handoff_to_writer],
)


async def run_handoffs_demo(user_query: str) -> str:
    """
    Runs the Planner→Writer handoff and returns a Markdown report for UI display.
    """
    run_res = await Runner.run(planner_with_handoff, user_query, session=session)
    report: FinalReport = run_res.final_output

    followups = "\n".join([f"- {q}" for q in report.follow_up_questions]) if report.follow_up_questions else ""

    return "\n\n".join(
        [
            "## Executive Summary",
            report.short_summary.strip(),
            "## Full Report",
            report.markdown_report.strip(),
            "## Follow-up Questions",
            followups,
        ]
    ).strip()

