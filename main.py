# Defaults
import datetime
import logging
import gradio as gr

# Locals
from config import config
from messages import MessageHandler
from content import css, PLACEHOLDER
from utils import CitingSources

# Agents
from llama_cpp_agent.providers import (
    LlamaCppServerProvider,
    LlamaCppPythonProvider,
    VLLMServerProvider,
    TGIServerProvider,
    LlamaCppPythonProvider,
)
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import (
    LlmStructuredOutputSettings,
    LlmStructuredOutputType,
)

# Tools
from llama_cpp_agent.tools import WebSearchTool
from llama_cpp_agent.prompt_templates import (
    web_search_system_prompt,
    research_system_prompt,
)

# Load UI Service settings from config module
server_name = config.server_name
server_port = config.server_port
# load Persona settings from config module
persona_app_title = config.app_title
persona_name = config.persona_name
persona_full_name = config.persona_full_name
persona_description = config.description
persona_avatar_image = config.persona_avatar_image
persona_ui_theme = config.ui_theme
persona_topic_examples = config.topic_examples
persona_system_message = config.system_message
persona_prompt_message = config.persona
persona_temperature = config.temperature
persona_preferences = config.preferences

# Ensure configurations are loaded before accessing them in global scope
# Configure providers

## CPP Server provider
# provider = LlamaCppServerProvider("http://hades.hq.solidrust.net:8084")
# provider = LlamaCppServerProvider(llm_url)

## vLLM Server provider
#llm_url = "http://thanatos.hq.solidrust.net:8082/v1"
llm_url = "http://thanatos:8081/v1"
model = "solidrust/Mistral-7B-instruct-v0.3-AWQ"
llm_model_type = "Mistral"          # config.current_settings[0]["model_type"]
llm_max_tokens = 16384 

provider = VLLMServerProvider(
    base_url=llm_url,
    model=model,
    huggingface_model=model,
)
## vLLM Server provider for summary
#llm_summary_url = "http://zelus.hq.solidrust.net:8083/v1"
llm_summary_url = "http://zelus:8081/v1"
model_summary = "solidrust/Mistral-7B-instruct-v0.3-AWQ"
llm_model_summary_type = "Llama3"
llm_summary_max_tokens = 8182
tokens_per_summary = 2048
tokens_search_results = 8192
number_of_search_results = 3

provider_summary = VLLMServerProvider(
    base_url=llm_summary_url,
    model=model_summary,
    huggingface_model=model_summary,
)
## vLLM Embeddings Server provider
llm_embeddings_url = ""

## CPP Python provider
#llm = Llama(
#        model_path=f"models/{model_filename}",
#        flash_attn=True,
#        n_threads=40,
#        n_gpu_layers=81,
#        n_batch=1024,
#        n_ctx=llm_max_tokens,
#    )
#provider = LlamaCppPythonProvider(llm)

provider_identifier = provider.get_provider_identifier()
identifier_str = str(provider_identifier).split(".")[-1]

# Log startup information
logging.info(
    f"""
    server: {server_name}:{server_port},
    model: {model},
    model type: {llm_model_type},
    model summary type: {llm_model_summary_type},
    max tokens: {llm_max_tokens}, 
    provider: {provider_identifier},
    Loaded chat examples: {persona_topic_examples},
    """
)


## Run inference
def respond(
    message,
    history: list[tuple[str, str]],
    system_message,
    max_tokens,
    temperature,
    top_p,
    top_k,
    repetition_penalty,
    model,
):
    chat_template = MessageHandler.get_messages_formatter_type(llm_model_type)
    chat_template_summary = MessageHandler.get_messages_formatter_type(llm_model_summary_type)

    logging.info(f"Loaded chat examples: {chat_template}")
    search_tool = WebSearchTool(
        llm_provider=provider,
        message_formatter_type=chat_template,
        model_max_context_tokens=llm_max_tokens,
        max_tokens_search_results=tokens_search_results,
        max_tokens_per_summary=tokens_per_summary,
        number_of_search_results=number_of_search_results,
    )

    web_search_agent = LlamaCppAgent(
        provider=provider,
        system_prompt=web_search_system_prompt,
        predefined_messages_formatter_type=chat_template,
        debug_output=False,
    )

    answer_agent = LlamaCppAgent(
        provider=provider,
        system_prompt=system_message,
        predefined_messages_formatter_type=chat_template,
        debug_output=True,
    )

    settings = provider.get_provider_default_settings()
    settings.stream = False
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p

    if "llama_cpp_server" in identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "llama_cpp_python" in identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "tgi_server" in identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    elif "vllm_server" in identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    else:
        return "unsupported llama-cpp-agent provider:", identifier_str

    output_settings = LlmStructuredOutputSettings.from_functions(
        [search_tool.get_tool()]
    )

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
        f"Write a detailed and complete research document that fulfills the following user request: '{message}', based on the information from the web below.\n\n"
        + result[0]["return_value"],
        role=Roles.tool,
        llm_sampling_settings=settings,
        chat_history=messages,
        returns_streaming_generator=True,
        print_output=False,
    )

    for text in response_text:
        outputs += text
        yield outputs

    output_settings = LlmStructuredOutputSettings.from_pydantic_models(
        [CitingSources], LlmStructuredOutputType.object_instance
    )

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


# Begin Gradio UI
main = gr.ChatInterface(
    respond,
    additional_inputs=[
        gr.Textbox(
            value=research_system_prompt,
            label="System message",
            interactive=True,
        ),
        gr.Slider(minimum=1, maximum=4096, value=2048, step=1, label="Max tokens"),
        gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
        gr.Slider(
            minimum=0.1,
            maximum=1.0,
            value=0.95,
            step=0.05,
            label="Top-p",
        ),
        gr.Slider(
            minimum=0,
            maximum=100,
            value=40,
            step=1,
            label="Top-k",
        ),
        gr.Slider(
            minimum=0.0,
            maximum=2.0,
            value=1.1,
            step=0.1,
            label="Repetition penalty",
        ),
    ],
    theme=gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="amber",
        neutral_hue="gray",
        font=[gr.themes.GoogleFont("Exo"), "ui-sans-serif", "system-ui", "sans-serif"],
    ).set(
        body_background_fill_dark="#0c0505",
        block_background_fill_dark="#0c0505",
        block_border_width="1px",
        block_title_background_fill_dark="#1b0f0f",
        input_background_fill_dark="#140b0b",
        button_secondary_background_fill_dark="#140b0b",
        border_color_accent_dark="#1b0f0f",
        border_color_primary_dark="#1b0f0f",
        background_fill_secondary_dark="#0c0505",
        color_accent_soft_dark="transparent",
        code_background_fill_dark="#140b0b"
    ),
    css=css,
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
    submit_btn="Send",
    examples=persona_topic_examples,
    analytics_enabled=False,
    description="Llama-cpp-agent: Chat Web Search Agent",
    chatbot=gr.Chatbot(
        scale=1,
        placeholder=PLACEHOLDER,
        likeable=False,
        show_copy_button=True
    ),
)

if __name__ == "__main__":
    main.launch(server_name=server_name, server_port=server_port)
