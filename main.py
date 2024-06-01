import os
import logging
import argparse
from app.config import config
from agents.chat_agent import chat_response
from agents.web_search_agent import web_search_response
from agents.wikipedia_agent import wikipedia_response
from interfaces.gradio import GradioInterface
from interfaces.streamlit import StreamlitInterface
from interfaces.cli import CLIInterface

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def main():
    try:
        parser = argparse.ArgumentParser(description="Run Llama-cpp-agent.")
        parser.add_argument(
            "--mode",
            choices=["chat", "web_search", "wikipedia"],
            required=True,
            help="Mode to run the application in",
        )
        parser.add_argument(
            "--interface",
            choices=["gradio", "streamlit", "cli", "custom"],
            required=True,
            help="Interface to run the application with",
        )
        args = parser.parse_args()

        response_function, system_message, is_wikipedia = select_mode(args.mode)
        ui_provider = select_interface(
            args.interface, response_function, system_message, is_wikipedia
        )

        ui_provider.setup_ui()
        ui_provider.start_ui_provider(args)
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)


def select_mode(mode):
    if mode == "chat":
        response_function = chat_response
        system_message = (
            f"{config.persona_system_message} {config.persona_prompt_message}"
        )
        is_wikipedia = False
    elif mode == "web_search":
        response_function = web_search_response
        system_message = (
            "You are an advanced AI assistant, trained by SolidRusT Networks."
        )
        is_wikipedia = False
    elif mode == "wikipedia":
        response_function = wikipedia_response
        system_message = (
            "You are an advanced AI assistant, trained by SolidRusT Networks."
        )
        is_wikipedia = True
    else:
        raise ValueError(f"Unsupported mode: {mode}")
    return response_function, system_message, is_wikipedia


def select_interface(interface, response_function, system_message, is_wikipedia):
    if interface == "gradio":
        logging.info("Setting up Gradio interface.")
        return GradioInterface(
            response_function=response_function,
            system_message=system_message,
            is_wikipedia=is_wikipedia,
        )
    elif interface == "streamlit":
        logging.info("Setting up Streamlit interface.")
        return StreamlitInterface(
            response_function=response_function,
            system_message=system_message,
            is_wikipedia=is_wikipedia,
        )
    elif interface == "cli":
        logging.info("Setting up CLI interface.")
        return CLIInterface(
            response_function=response_function,
            system_message=system_message,
            is_wikipedia=is_wikipedia,
        )
    elif interface == "custom":
        logging.info("Custom interface is not implemented yet.")
        print("Custom interface is not implemented yet.")
        raise NotImplementedError("Custom interface is not implemented yet.")
    else:
        raise ValueError(f"Unsupported interface: {interface}")


if __name__ == "__main__":
    main()
