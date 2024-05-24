from llama_cpp_agent import MessagesFormatterType

def get_messages_formatter_type(model_name):
    if "Meta" in model_name or "aya" in model_name:
        return MessagesFormatterType.LLAMA_3
    elif "Mistral" in model_name:
        return MessagesFormatterType.MISTRAL
    elif "Einstein-v6-7B" in model_name or "dolphin" in model_name:
        return MessagesFormatterType.CHATML
    elif "Phi" in model_name:
        return MessagesFormatterType.PHI_3
    else:
        return MessagesFormatterType.CHATML


def write_message_to_user():
    """
    Let you write a message to the user.
    """
    return "Please write the message to the user."