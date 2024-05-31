import os
import logging
import argparse
from app.config import config
from agents.chat_agent import chat_response
from agents.web_search_agent import web_search_response
from agents.wikipedia_agent import wikipedia_response
from interfaces.gradio import GradioInterface
from interfaces.streamlit import StreamlitInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def main():
    parser = argparse.ArgumentParser(description="Run Llama-cpp-agent.")
    parser.add_argument("--mode", choices=["chat", "web_search", "wikipedia"], required=True, help="Mode to run the application in")
    parser.add_argument("--interface", choices=["gradio", "streamlit", "custom"], required=True, help="Interface to run the application with")
    args = parser.parse_args()

    if args.mode == "chat":
        response_function = chat_response
        system_message = f"{config.persona_system_message} {config.persona_prompt_message}"
        is_wikipedia = False
    elif args.mode == "web_search":
        response_function = web_search_response
        system_message = "You are an advanced AI assistant, trained by SolidRusT Networks."
        is_wikipedia = False
    elif args.mode == "wikipedia":
        response_function = wikipedia_response
        system_message = "You are an advanced AI assistant, trained by SolidRusT Networks."
        is_wikipedia = True

    if args.interface == "gradio":
        logging.info("Setting up Gradio interface.")
        ui_provider = GradioInterface(response_function=response_function, system_message=system_message, is_wikipedia=is_wikipedia)
    elif args.interface == "streamlit":
        logging.info("Setting up Streamlit interface.")
        ui_provider = StreamlitInterface(response_function=response_function, system_message=system_message, is_wikipedia=is_wikipedia)
    elif args.interface == "custom":
        logging.info("Custom interface is not implemented yet.")
        print("Custom interface is not implemented yet.")
        return

    ui_provider.setup_ui()
    ui_provider.start_ui_provider(args)

if __name__ == "__main__":
    main()
