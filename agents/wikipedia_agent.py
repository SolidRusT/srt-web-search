import logging
from app.config import config
from app.messages import MessageHandler
from llama_cpp_agent import LlamaCppAgent
from ragatouille.utils import get_wikipedia_page
from data.chromadb import RAGColbertReranker
from llama_cpp_agent.text_utils import RecursiveCharacterTextSplitter

async def wikipedia_response(
    message,
    history,
    system_message,
    max_tokens,
    temperature,
    top_p,
    top_k,
    repetition_penalty,
    model,
    page_title,
):
    try:
        page = get_wikipedia_page(page_title)
        if page is None:
            raise ValueError(f"No content found for the Wikipedia page title: {page_title}")
    except Exception as e:
        logging.error(f"Error fetching Wikipedia page for title '{page_title}': {e}", exc_info=True)
        yield f"Could not fetch Wikipedia page for title '{page_title}'. Error: {e}"
        return

    try:
        vector_store = RAGColbertReranker(persistent=False)
        length_function = len
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=512,
            chunk_overlap=0,
            length_function=length_function,
            keep_separator=True,
        )
        splits = splitter.split_text(page)

        for split in splits:
            vector_store.add_document(split)

        default_chat_template = MessageHandler.get_messages_formatter_type(
            config.default_llm_type
        )
        default_agent_provider = config.default_llm_agent_provider

        logging.info(f"Loaded chat template: {default_chat_template}, Wiki page: {page_title}")

        agent_with_rag_information = LlamaCppAgent(
            provider=config.default_provider,
            system_prompt=system_message,
            predefined_messages_formatter_type=default_chat_template,
            debug_output=config.debug,
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
            logging.error(f"Unsupported llama-cpp-agent provider: {default_agent_provider}")
            yield "Unsupported llama-cpp-agent provider: " + default_agent_provider
            return

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
            if text.endswith((' ', '\n', '.')):
                yield outputs
                outputs = ""

        page_url = f"\nPage title: https://en.wikipedia.org/wiki/{page_title}\n"
        for text in page_url:
            outputs += text
            yield outputs

    except Exception as e:
        logging.error(f"Error occurred during Wikipedia response generation: {e}", exc_info=True)
        yield "An error occurred while processing your request. Please try again later."
