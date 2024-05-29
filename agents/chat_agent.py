import datetime
import logging
from config import config
from app.messages import MessageHandler
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles

async def chat_response(message, history, system_message, max_tokens, temperature, top_p, top_k, repetition_penalty, model):
    chat_template = MessageHandler.get_messages_formatter_type(config.default_llm_type)
    model = config.default_llm_huggingface
    system_message = f"{config.persona_system_message} {config.persona_prompt_message}"
    
    chat_agent = LlamaCppAgent(
        provider=config.default_provider,
        system_prompt=system_message,
        predefined_messages_formatter_type=chat_template,
        debug_output=False,
    )
    default_agent_provider = config.default_llm_agent_provider
    logging.info(f"Loaded chat template: {chat_template}")
    
    settings = config.default_provider.get_provider_default_settings()
    settings.stream = True
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p

    if "llama_cpp_server" in default_agent_provider:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "llama_cpp_python" in default_agent_provider:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "tgi_server" in default_agent_provider:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    elif "vllm_server" in default_agent_provider:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    
    messages = BasicChatHistory()
    for msn in history:
        user = {"role": Roles.user, "content": msn[0]}
        assistant = {"role": Roles.assistant, "content": msn[1]}
        messages.add_message(user)
        messages.add_message(assistant)

    result = chat_agent.get_chat_response(
        f"Current Date and Time(d/m/y, h:m:s): {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n\nUser Query: " + message,
        llm_sampling_settings=settings,
        add_message_to_chat_history=True,
        add_response_to_chat_history=True,
        print_output=False,
    )

    outputs = ""
    for text in result:
        outputs += text
        yield outputs