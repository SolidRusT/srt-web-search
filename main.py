## App defaults
import os
import logging
import argparse
from app.config import config
from agents.chat_agent import chat_response
from agents.web_search_agent import web_search_response
from agents.wikipedia_agent import wikipedia_response
from llama_cpp_agent.prompt_templates import research_system_prompt
from gradio_interface import GradioInterface
from streamlit_interface import StreamlitInterface

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
        system_message = "You are an advanced AI assistant, trained by SolidRusT Networks."

    if args.interface == "gradio":
        gradio_interface = GradioInterface(response_function, system_message, is_wikipedia)
        interface = gradio_interface.setup()
        interface.launch(server_name=config.server_name, server_port=port)
    elif args.interface == "streamlit":
        streamlit_interface = StreamlitInterface(response_function, system_message, is_wikipedia)
        streamlit_interface.run()
    elif args.interface == "custom":
        # Implement your custom interface logic here
        print("Custom interface is not implemented yet.")
