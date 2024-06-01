import asyncio
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

                # Handling input for Wikipedia mode
                if self.is_wikipedia:
                    inputs = user_input.split('\n')
                    page_title = inputs[0]
                    query = inputs[1] if len(inputs) > 1 else ""
                else:
                    page_title = None
                    query = user_input

                # Construct the necessary arguments as a dictionary
                response_args = {
                    "system_message": self.system_message,
                    "message": query,
                    "history": [],  # Assuming empty history for simplicity
                    "max_tokens": 100,  # Adjust as needed
                    "temperature": 0.7,  # Adjust as needed
                    "top_p": 0.9,  # Adjust as needed
                    "top_k": 50,  # Adjust as needed
                    "repetition_penalty": 1.0,  # Adjust as needed
                    "model": config.default_llm_name,  # Assuming default model
                    "page_title": page_title  # Adding page_title for Wikipedia mode
                }

                async for response in self.response_function(**response_args):
                    print(f"AI: {response}")
            except Exception as e:
                print(f"Error: {e}")
                break
