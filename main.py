## App defaults
import os
import logging
import argparse
from app.config import config
from app.content import css, PLACEHOLDER
from agents.chat_agent import chat_response
from agents.web_search_agent import web_search_response
from agents.wikipedia_agent import wikipedia_response
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
def setup_gradio_interface(response_function, system_message, is_wikipedia=False):
    import gradio as gr
    
    if is_wikipedia:
        page_title = ""
        additional_inputs.insert(0, gr.Textbox(value=page_title, label="Wikipedia Page Title", interactive=True))
    additional_inputs = [
        gr.Textbox(value=system_message, label="System message", interactive=True),
        gr.Slider(minimum=1, maximum=4096, value=2048, step=1, label="Max tokens"),
        gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
        gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p"),
        gr.Slider(minimum=0, maximum=100, value=40, step=1, label="Top-k"),
        gr.Slider(
            minimum=0.0,
            maximum=2.0,
            value=1.1,
            step=0.1,
            label="Repetition penalty",
        ),
    ]

    async def response_fn_wrapper(*inputs):
        response_gen = response_function(*inputs, model=config.default_llm_huggingface)
        response_text = ""
        async for response in response_gen:
            response_text += response
            yield response_text

    return gr.ChatInterface(
        response_fn_wrapper,
        additional_inputs=additional_inputs,
        theme=gr.themes.Soft(
            primary_hue="orange",
            secondary_hue="amber",
            neutral_hue="gray",
            font=[
                gr.themes.GoogleFont("Exo"),
                "ui-sans-serif",
                "system-ui",
                "sans-serif",
            ],
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
        chatbot=gr.Chatbot(
            scale=1, placeholder=PLACEHOLDER, likeable=False, show_copy_button=True
        ),
    )

def setup_streamlit_interface(response_function, system_message, is_wikipedia=False):
    import streamlit as st
    import asyncio
    st.title("Llama-cpp-agent Interface")
    st.write(system_message)

    page_title = ""
    if is_wikipedia:
        page_title = st.text_input("Wikipedia Page Title:", "")
    user_input = st.text_input("Your message:", "")
    max_tokens = st.slider("Max tokens", 1, 4096, 2048)
    temperature = st.slider("Temperature", 0.1, 4.0, 0.7)
    top_p = st.slider("Top-p", 0.1, 1.0, 0.95)
    top_k = st.slider("Top-k", 0, 100, 40)
    repetition_penalty = st.slider("Repetition penalty", 0.0, 2.0, 1.1)

    if st.button("Send"):
        history = []
        response_text = ""

        async def fetch_response():
            async for response in response_function(
                message=user_input,
                history=history,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                model=config.default_llm_huggingface,
                page_title=page_title if is_wikipedia else None
            ):
                nonlocal response_text
                response_text += response
                st.write(response_text)

        asyncio.run(fetch_response())

def setup_custom_interface(response_function, system_message):
    # Implement your custom interface logic here
    print("Custom interface is not implemented yet.")

## Self execute when running from a CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Llama-cpp-agent.")
    parser.add_argument(
        "--mode",
        choices=["chat", "web_search", "wikipedia"],
        required=True,
        help="Mode to run the application in",
    )
    parser.add_argument(
        "--interface",
        choices=["gradio", "streamlit", "custom"],
        required=True,
        help="Interface to run the application with",
    )
    args = parser.parse_args()

    port = config.server_port

    is_wikipedia = args.mode == "wikipedia"
    if args.mode == "chat":
        response_function = chat_response
        system_message = f"{config.persona_system_message} {config.persona_prompt_message}"
    elif args.mode == "web_search":
        response_function = web_search_response
        system_message = research_system_prompt
    elif args.mode == "wikipedia":
        response_function = wikipedia_response
        system_message = research_system_prompt

    if args.interface == "gradio":
        gradio_interface = setup_gradio_interface(response_function=response_function, system_message=system_message, is_wikipedia=is_wikipedia)
        gradio_interface.launch(server_name=config.server_name, server_port=port)
    elif args.interface == "streamlit":
        os.system(f"streamlit run streamlit_main.py --server.port {config.server_port} -- --mode {args.mode}")
    elif args.interface == "custom":
        setup_custom_interface(response_function=response_function, system_message=system_message)
