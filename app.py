import gradio as gr
import asyncio
from script import run_handoffs_demo_stream


def run_query(query):
    """
    Bridges the async generator to a sync generator for Gradio.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    agen = run_handoffs_demo_stream(query)

    try:
        while True:
            try:
                chunk = loop.run_until_complete(agen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()


interface = gr.Interface(
    fn=run_query,
    inputs=gr.Textbox(lines=3, placeholder="Enter your research query..."),
    outputs=gr.Markdown(),
    title="AI Research Agent With Guardrail & Handoff",
    description="Multi-agent system for news & fundamental analysis",
    flagging_mode="never",
)

if __name__ == "__main__":
    interface.launch()