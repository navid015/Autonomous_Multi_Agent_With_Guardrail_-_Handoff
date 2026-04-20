import gradio as gr
import asyncio
from script import run_handoffs_demo

def run_query(query):
    try:
        return asyncio.run(run_handoffs_demo(query))
    except RuntimeError:
        # Fallback if an event loop is already running (env-dependent).
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(run_handoffs_demo(query))
        finally:
            loop.close()

interface = gr.Interface(
    fn=run_query,
    inputs=gr.Textbox(lines=3, placeholder="Enter your research query..."),
    outputs=gr.Markdown(),
    title="AI Research Agent",
    description="Multi-agent system for news + fundamental analysis"
)

if __name__ == "__main__":
    interface.launch()