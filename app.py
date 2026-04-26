# import gradio as gr
# import asyncio
# from script import run_handoffs_demo_stream


# def run_query(query):
#     """
#     Bridges the async generator to a sync generator for Gradio.
#     """
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)

#     agen = run_handoffs_demo_stream(query)

#     try:
#         while True:
#             try:
#                 chunk = loop.run_until_complete(agen.__anext__())
#                 yield chunk
#             except StopAsyncIteration:
#                 break
#     finally:
#         loop.close()


# interface = gr.Interface(
#     fn=run_query,
#     inputs=gr.Textbox(lines=3, placeholder="Enter your research query..."),
#     outputs=gr.Markdown(),
#     title="AI Research Agent With Guardrail & Handoff",
#     description="Multi-agent system for news & fundamental analysis",
#     flagging_mode="never",
# )

# if __name__ == "__main__":
#     interface.launch()


import gradio as gr
import asyncio
from script import run_handoffs_demo_stream


def run_query(query):
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


custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg-deep:    #0a0c10;
    --bg-panel:   #10141c;
    --bg-card:    #151b26;
    --border:     #1e2840;
    --accent:     #e8854a;
    --accent-dim: #c46a35;
    --accent-glow:rgba(232,133,74,0.18);
    --gold:       #d4a853;
    --text-pri:   #e8eaf0;
    --text-sec:   #8892a4;
    --text-dim:   #4a5568;
    --success:    #4ade80;
    --info:       #60a5fa;
}

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container {
    background: var(--bg-deep) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-pri) !important;
    min-height: 100vh;
}

/* ── Atmospheric background ── */
.gradio-container::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(232,133,74,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(96,165,250,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Main wrapper ── */
.main { position: relative; z-index: 1; }

/* ── Header block ── */
#header-block {
    text-align: center;
    padding: 56px 24px 40px;
    position: relative;
}

#header-block::after {
    content: '';
    display: block;
    width: 120px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 28px auto 0;
}

/* ── Title ── */
.app-title {
    font-family: 'Playfair Display', serif !important;
    font-size: clamp(28px, 5vw, 48px) !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    line-height: 1.15 !important;
    color: var(--text-pri) !important;
    margin: 0 0 12px !important;
}

.app-title span {
    color: var(--accent);
}

.app-subtitle {
    font-size: 14px !important;
    color: var(--text-sec) !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    font-weight: 400 !important;
    margin: 0 !important;
}

/* ── Status pills row ── */
.status-row {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin: 0 0 8px;
}

.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    border: 1px solid;
}

.pill-green  { background: rgba(74,222,128,0.06); border-color: rgba(74,222,128,0.25); color: var(--success); }
.pill-blue   { background: rgba(96,165,250,0.06); border-color: rgba(96,165,250,0.25); color: var(--info); }
.pill-gold   { background: rgba(212,168,83,0.06);  border-color: rgba(212,168,83,0.25);  color: var(--gold); }
.pill-dot    { width: 6px; height: 6px; border-radius: 50%; background: currentColor; animation: pulse 2s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Input panel ── */
#input-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 4px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(232,133,74,0.04);
    transition: box-shadow 0.3s;
    position: relative;
    overflow: hidden;
}

#input-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0.6;
}

#input-panel:focus-within {
    box-shadow: 0 4px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(232,133,74,0.12), 0 0 30px var(--accent-glow);
}

/* ── Label ── */
.input-label {
    font-size: 10px !important;
    font-weight: 500 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--accent) !important;
    margin-bottom: 10px !important;
    display: block;
}

/* ── Textbox ── */
textarea, .gr-textbox textarea {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-pri) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.65 !important;
    padding: 16px 18px !important;
    resize: vertical !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    min-height: 110px !important;
}

textarea:focus, .gr-textbox textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}

textarea::placeholder, .gr-textbox textarea::placeholder {
    color: var(--text-dim) !important;
    font-style: italic;
}

/* ── Buttons ── */
.gr-button, button.gr-button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    height: 46px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
}

/* Submit / primary */
.gr-button-primary, button[value="Submit"], .gr-button.primary {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dim) 100%) !important;
    color: #fff !important;
    box-shadow: 0 2px 16px rgba(232,133,74,0.35) !important;
}

.gr-button-primary:hover, button[value="Submit"]:hover, .gr-button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 24px rgba(232,133,74,0.5) !important;
}

/* Clear / secondary */
.gr-button-secondary, button[value="Clear"], .gr-button.secondary {
    background: var(--bg-panel) !important;
    color: var(--text-sec) !important;
    border-color: var(--border) !important;
}

.gr-button-secondary:hover, button[value="Clear"]:hover, .gr-button.secondary:hover {
    background: var(--bg-card) !important;
    color: var(--text-pri) !important;
    border-color: var(--text-dim) !important;
}

/* ── Output / result panel ── */
/* gr.Column with elem_id renders as: <div id="output-panel"><div class="gap ..."> */
#output-panel > .gap,
#output-panel > div > .gap,
#output-panel > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 40px rgba(0,0,0,0.35) !important;
    padding: 0 !important;
    gap: 0 !important;
}

/* The outer wrapper itself should be transparent */
#output-panel {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.output-header {
    padding: 14px 22px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.015);
}

.output-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}

.output-title-text {
    font-size: 11px !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-sec) !important;
    font-weight: 500;
}

/* Markdown output styling */
.output-markdown,
.output-markdown > .prose,
#output-panel .gr-markdown {
    padding: 24px 28px !important;
    color: var(--text-pri) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.75 !important;
}

.gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text-pri) !important;
    font-weight: 600 !important;
}

.gr-markdown h2 {
    font-size: 22px !important;
    margin-top: 32px !important;
    margin-bottom: 14px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid var(--border) !important;
}

.gr-markdown h3 {
    font-size: 16px !important;
    color: var(--accent) !important;
    letter-spacing: 0.5px !important;
    margin-top: 24px !important;
}

.gr-markdown p { color: var(--text-sec) !important; }

.gr-markdown strong { color: var(--text-pri) !important; font-weight: 600 !important; }

.gr-markdown code {
    font-family: 'DM Mono', monospace !important;
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    color: var(--gold) !important;
    padding: 2px 7px !important;
    border-radius: 4px !important;
    font-size: 13px !important;
}

.gr-markdown pre {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 18px 20px !important;
}

.gr-markdown ul, .gr-markdown ol {
    color: var(--text-sec) !important;
    padding-left: 22px !important;
}

.gr-markdown li { margin-bottom: 6px !important; }

.gr-markdown blockquote {
    border-left: 3px solid var(--accent) !important;
    padding-left: 16px !important;
    color: var(--text-dim) !important;
    font-style: italic;
    margin: 16px 0 !important;
}

/* ── Footer ── */
footer, .gr-footer {
    text-align: center;
    padding: 24px 0 32px;
    font-size: 12px;
    color: var(--text-dim) !important;
    letter-spacing: 0.5px;
}

footer a { color: var(--text-dim); text-decoration: none; }
footer a:hover { color: var(--accent); }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }

/* ── Gradio chrome cleanup ── */
.gr-form, .gr-panel { background: transparent !important; border: none !important; }
.gr-block { background: transparent !important; }
.label-wrap label span { display: none !important; }  /* hide default label */
.gap, .gr-gap { gap: 20px !important; }

/* ── Loader bar ── */
.progress-bar-wrap { display: none !important; }  /* hide ugly default */
"""


with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:

    # ── Header ──────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="header-block">
        <p class="app-subtitle">Powered by multi-agent AI</p>
        <h1 class="app-title">Research <span>Intelligence</span> Agent</h1>
        <div class="status-row">
            <span class="pill pill-green"><span class="pill-dot"></span>Live</span>
            <span class="pill pill-blue">News & Fundamentals</span>
            <span class="pill pill-gold">Guardrail Protected</span>
        </div>
    </div>
    """)

    # ── Input panel ─────────────────────────────────────────────────────────
    with gr.Column(elem_id="input-panel"):
        gr.HTML('<span class="input-label">Research Query</span>')
        query_input = gr.Textbox(
            lines=4,
            placeholder="e.g. Analyze Apple's growth outlook and recent earnings performance...",
            show_label=False,
            container=False,
        )
        with gr.Row():
            clear_btn  = gr.ClearButton(components=[query_input], value="Clear")
            submit_btn = gr.Button("Run Analysis →", variant="primary")

    # ── Output panel ────────────────────────────────────────────────────────
    with gr.Column(elem_id="output-panel"):
        gr.HTML("""
        <div class="output-header">
            <span class="output-dot"></span>
            <span class="output-title-text">Analysis Report</span>
        </div>
        """)
        output_md = gr.Markdown(
            value="*Your report will appear here once you submit a query above.*",
            elem_classes=["output-markdown"],
        )

    # ── Wire up ─────────────────────────────────────────────────────────────
    submit_btn.click(fn=run_query, inputs=query_input, outputs=output_md)
    query_input.submit(fn=run_query, inputs=query_input, outputs=output_md)


if __name__ == "__main__":
    demo.launch()