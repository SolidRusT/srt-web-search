from llama_cpp_agent import MessagesFormatterType


class MessageHandler:
    @staticmethod
    def get_messages_formatter_type(model_name):
        if "Llama3" in model_name:
            return MessagesFormatterType.LLAMA_3
        elif "Llama2" in model_name:
            return MessagesFormatterType.LLAMA_2
        elif "Mistral" in model_name:
            return MessagesFormatterType.MISTRAL
        elif "ChatML" in model_name:
            return MessagesFormatterType.CHATML
        elif "Phi" in model_name:
            return MessagesFormatterType.PHI_3
        elif "Vicuna" in model_name:
            return MessagesFormatterType.VICUNA
        elif "Alpaca" in model_name:
            return MessagesFormatterType.ALPACA
        elif "Synthia" in model_name:
            return MessagesFormatterType.SYNTHIA
        elif "Solar" in model_name:
            return MessagesFormatterType.SOLAR
        else:
            return MessagesFormatterType.CHATML

    @staticmethod
    def write_message_to_user():
        """
        Let you write a message to the user.
        """
        return "Please write the message to the user."

    @staticmethod
    def send_message_to_user(message: str):
        """
        Send a message to user.
        Args:
            message (str): Message to send.
        """
        print(message)
