import asyncio
import re
from app.config import config

class CLIInterface:
    def __init__(self, response_function, system_message, is_wikipedia):
        self.response_function = response_function
        self.system_message = system_message
        self.is_wikipedia = is_wikipedia

    def setup_ui(self):
        print("CLI Interface is ready.")

    def start_ui_provider(self, args):
        asyncio.run(self.run_cli())

    async def run_cli(self):
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting CLI Interface.")
                    break

                if self.is_wikipedia:
                    inputs = user_input.split('\n', 1)
                    page_title = inputs[0]
                    query = inputs[1] if len(inputs) > 1 else ""
                    
                    response_args = {
                        "system_message": self.system_message,
                        "message": query,
                        "history": [],
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "repetition_penalty": 1.1,
                        "model": config.default_llm_huggingface,
                        "page_title": page_title
                    }
                else:
                    response_args = {
                        "system_message": self.system_message,
                        "message": user_input,
                        "history": [],
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "repetition_penalty": 1.1,
                        "model": config.default_llm_huggingface
                    }

                full_response = ""
                async for response in self.response_function(**response_args):
                    full_response += response
                    # Only print complete sentences or significant chunks
                    if re.search(r"[.!?]\s|\n", full_response):
                        print(f"AI: {full_response.strip()}")
                        full_response = ""
                    await asyncio.sleep(0.1)  # Short delay to allow streaming

                if full_response:
                    print(f"AI: {full_response.strip()}")

            except Exception as e:
                print(f"Error: {e}")
                break
