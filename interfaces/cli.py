class CLIInterface:
    def __init__(self, response_function, system_message, is_wikipedia):
        self.response_function = response_function
        self.system_message = system_message
        self.is_wikipedia = is_wikipedia

    def setup_ui(self):
        print("CLI Interface is ready.")

    def start_ui_provider(self, args):
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting CLI Interface.")
                    break
                response = self.response_function(user_input)
                print(f"AI: {response}")
            except Exception as e:
                print(f"Error: {e}")
                break
