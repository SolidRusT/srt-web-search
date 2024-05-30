import logging
from app.config import config
from app.messages import MessageHandler
from llama_cpp_agent import LlamaCppAgent
from ragatouille.utils import get_wikipedia_page
from llama_cpp_agent.rag.rag_colbert_reranker import RAGColbertReranker
from llama_cpp_agent.text_utils import RecursiveCharacterTextSplitter

async def wikipedia_response(message, history, system_message, max_tokens, temperature, top_p, top_k, repetition_penalty, model):
    page = get_wikipedia_page("Synthetic_diamond")
    # Synthetic_diamond  What is a BARS apparatus?
    system_message = "You are an advanced AI assistant, trained by SolidRusT Networks."
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
    default_agent_provider = config.default_llm_agent_provider
    
    logging.info(f"Loaded chat template: {default_chat_template}")

    agent_with_rag_information = LlamaCppAgent(
        provider=config.default_provider,
        system_prompt=system_message,
        predefined_messages_formatter_type=default_chat_template,
        debug_output=False,
    )

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
    else:
        return "unsupported llama-cpp-agent provider:", default_agent_provider

    # Retrieve relevant document chunks based on the query
    documents = vector_store.retrieve_documents(message, k=3)

    prompt = "Consider the following context:\n==========Context===========\n"
    for doc in documents:
        prompt += doc["content"] + "\n\n"
    prompt += "\n======================\nQuestion: " + message

    # Use the agent with RAG information to generate a response
    response_text = agent_with_rag_information.get_chat_response(
        prompt,
        llm_sampling_settings=settings,
        add_message_to_chat_history=True,
        add_response_to_chat_history=True,
        print_output=False,
    )

    outputs = ""
    for text in response_text:
        outputs += text
        yield outputs
