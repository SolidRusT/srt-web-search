## App defaults
import logging
import gradio as gr
from app.config import config
from app.content import css, PLACEHOLDER
from chat_agent import chat_response
from web_search_agent import web_search_response
from llama_cpp_agent.prompt_templates import research_system_prompt

## Log startup information
logging.info(
    f"""
    server: {config.server_name}:{config.server_port},
    model: {config.default_llm_huggingface}, {config.default_llm_huggingface},
    model type: {config.default_llm_type}, {config.summary_llm_type},
    max tokens: {config.default_llm_max_tokens}, {config.summary_llm_max_tokens}, 
    providers: {config.default_provider.get_provider_identifier()}, {config.summary_provider.get_provider_identifier()},
    Loaded chat examples: {config.persona_topic_examples},
    """
)

## Gradio UI setup
def setup_gradio_interface(response_function, system_message):
    return gr.ChatInterface(
        response_function,
        additional_inputs=[
            gr.Textbox(value=system_message, label="System message", interactive=True),
            gr.Slider(minimum=1, maximum=4096, value=2048, step=1, label="Max tokens"),
            gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
            gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p"),
            gr.Slider(minimum=0, maximum=100, value=40, step=1, label="Top-k"),
            gr.Slider(minimum=0.0, maximum=2.0, value=1.1, step=0.1, label="Repetition penalty"),
        ],
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="amber",
            neutral_hue="gray",
            font=[gr.themes.GoogleFont("Exo"), "ui-sans-serif", "system-ui", "sans-serif"]
        ).set(
            body_background_fill_dark="#0c0505",
            block_background_fill_dark="#0c0505",
            block_border_width="1px",
            block_title_background_fill_dark="#1b0f0f",
            input_background_fill_dark="#140b0b",
            button_secondary_background_fill_dark="#140b0b",
            border_color_accent_dark="#1b0f0f",
            border_color_primary_dark="#1b0f0f",
            background_fill_secondary_dark="#0c0505",
            color_accent_soft_dark="transparent",
            code_background_fill_dark="#140b0b",
        ),
        css=css,
        retry_btn="Retry",
        undo_btn="Undo",
        clear_btn="Clear",
        submit_btn="Send",
        examples=config.persona_topic_examples,
        analytics_enabled=False,
        description="Llama-cpp-agent Interface",
        chatbot=gr.Chatbot(scale=1, placeholder=PLACEHOLDER, likeable=False, show_copy_button=True),
    )

## Self execute when running from a CLI
if __name__ == "__main__":
    mode = input("Choose mode (chat/web_search): ").strip().lower()
    port = config.server_port

    if mode == "chat":
        gradio_interface = setup_gradio_interface(chat_response, f"{config.persona_system_message} {config.persona_prompt_message}")
    elif mode == "web_search":
        gradio_interface = setup_gradio_interface(web_search_response, research_system_prompt)
    else:
        raise ValueError("Invalid mode selected. Choose either 'chat' or 'web_search'.")

    gradio_interface.launch(server_name=config.server_name, server_port=port)
