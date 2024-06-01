import argparse
import logging
from interfaces.streamlit import StreamlitInterface
from agents.chat import chat_response
from agents.web_search import web_search_response
from agents.wikipedia import wikipedia_response
from app.config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Streamlit interface for Llama-cpp-agent.")
    parser.add_argument("--mode", choices=["chat", "web_search", "wikipedia"], required=True, help="Mode to run the application in")
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

    try:
        logging.info("Setting up Streamlit interface.")
        interface = StreamlitInterface(response_function, system_message, is_wikipedia)
        interface.setup()
    except Exception as e:
        logging.error(f"Error during Streamlit setup: {e}", exc_info=True)
