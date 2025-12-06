import gradio as gr
from agent_logic import research_agent_hybrid
from utils import apply_feedback

def format_output(topic):
    """
    Wrapper to run the agent and format the dictionary response into Markdown.
    """
    response = research_agent_hybrid(topic)

    if isinstance(response, str):
        return f"**Status:** {response}"

    output_md = f"# 🧠 Research Summary: {response['topic'].title()}\n"
    output_md += f"*(Source: {response['method']})*\n\n"
    output_md += f"{response['summary']}\n\n"
    output_md += "---\n"
    output_md += "### 📚 References\n"

    for source in response['sources']:
        output_md += f"* 🔗 [{source['title']}]({source['url']}) - _{source['credibility']}_\n"

    return output_md

def handle_feedback(feedback_type):
    """Wrapper to trigger the reinforcement learning memory update."""
    apply_feedback(feedback_type)
    return f"Memory updated: Preference set to '{feedback_type}'."

# --- UI LAYOUT ---
# UPDATED: Removed 'theme=' argument to prevent crashes on older Gradio versions
with gr.Blocks() as demo:
    gr.Markdown("# 🤖 AI Research Agent (Hybrid)")
    
    with gr.Row():
        topic_input = gr.Textbox(label="Research Topic", placeholder="Enter topic...", scale=4)
        submit_btn = gr.Button("Research", variant="primary", scale=1)
    
    output_display = gr.Markdown(label="Results")
    
    with gr.Row():
        gr.Markdown("### 📢 Provide Feedback to Improve Future Summaries")
        btn_short = gr.Button("Too Long (Shorten Future)")
        btn_good = gr.Button("Good Length")
        btn_long = gr.Button("Too Short (Lengthen Future)")
    
    feedback_status = gr.Markdown()

    # Event Handlers
    submit_btn.click(fn=format_output, inputs=topic_input, outputs=output_display)
    topic_input.submit(fn=format_output, inputs=topic_input, outputs=output_display)
    
    # RL Feedback Handlers
    btn_short.click(fn=lambda: handle_feedback("too long"), outputs=feedback_status)
    btn_good.click(fn=lambda: handle_feedback("good"), outputs=feedback_status)
    btn_long.click(fn=lambda: handle_feedback("too short"), outputs=feedback_status)

if __name__ == "__main__":
    # server_name="0.0.0.0" allows external connections (fixes Docker/WSL issues)
    # share=True creates a public link (fixes firewall/port issues)
    demo.launch(server_name="0.0.0.0", share=True)
 
