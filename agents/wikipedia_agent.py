import datetime
import logging
from app.utils import CitingSources
from app.config import config
from app.messages import MessageHandler
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import LlmStructuredOutputSettings, LlmStructuredOutputType
from llama_cpp_agent.prompt_templates import web_search_system_prompt
from ragatouille.utils import get_wikipedia_page
from llama_cpp_agent.messages_formatter import MessagesFormatterType
from llama_cpp_agent.rag.rag_colbert_reranker import RAGColbertReranker
from llama_cpp_agent.text_utils import RecursiveCharacterTextSplitter


def wikipedia_response(message, history, system_message, max_tokens, temperature, top_p, top_k, repetition_penalty, model):
    page = get_wikipedia_page(message)
    vector_store = RAGColbertReranker(persistent=False)
    length_function = len
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=512,
        chunk_overlap=0,
        length_function=length_function,
        keep_separator=True
    )
    splits = splitter.split_text(page)
    
    for split in splits:
        vector_store.add_document(split)

    default_chat_template = MessageHandler.get_messages_formatter_type(config.default_llm_type)
    summary_chat_template = MessageHandler.get_messages_formatter_type(config.summary_llm_type)
    default_agent_provider = config.default_llm_agent_provider
    
    logging.info(f"Loaded chat template: {default_chat_template}")

    agent_without_rag_information = LlamaCppAgent(
        provider=config.summary_provider,
        system_prompt=web_search_system_prompt,
        predefined_messages_formatter_type=summary_chat_template,
        debug_output=False,
    )

    answer_agent = LlamaCppAgent(
        provider=config.default_provider,
        system_prompt=system_message,
        predefined_messages_formatter_type=default_chat_template,
        debug_output=False,
    )

    settings = config.default_provider.get_provider_default_settings()
    settings.stream = False
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
    else:
        return "unsupported llama-cpp-agent provider:", default_agent_provider

    output_settings = LlmStructuredOutputSettings.from_functions([search_tool.get_tool()])
    messages = BasicChatHistory()
    for msn in history:
        user = {"role": Roles.user, "content": msn[0]}
        assistant = {"role": Roles.assistant, "content": msn[1]}
        messages.add_message(user)
        messages.add_message(assistant)

    result = web_search_agent.get_chat_response(
        f"Current Date and Time(d/m/y, h:m:s): {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n\nUser Query: " + message,
        llm_sampling_settings=settings,
        structured_output_settings=output_settings,
        add_message_to_chat_history=False,
        add_response_to_chat_history=False,
        print_output=False,
    )

    outputs = ""
    settings.stream = True
    response_text = answer_agent.get_chat_response(
        f"Write a detailed and complete research document that fulfills the following user request: '{message}', based on the information from the web below.\n\n" + result[0]["return_value"],
        role=Roles.tool,
        llm_sampling_settings=settings,
        chat_history=messages,
        returns_streaming_generator=True,
        print_output=False,
    )

    for text in response_text:
        outputs += text
        yield outputs

    output_settings = LlmStructuredOutputSettings.from_pydantic_models([CitingSources], LlmStructuredOutputType.object_instance)
    citing_sources = answer_agent.get_chat_response(
        "Cite the sources you used in your response.",
        role=Roles.tool,
        llm_sampling_settings=settings,
        chat_history=messages,
        returns_streaming_generator=False,
        structured_output_settings=output_settings,
        print_output=False,
    )

    outputs += "\n\nSources:\n"
    outputs += "\n".join(citing_sources.sources)
    yield outputs
