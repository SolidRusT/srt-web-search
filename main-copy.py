## App defaults
import datetime
import logging
import gradio as gr

## Local imports
from app.config import config
from app.messages import MessageHandler
from app.content import css, PLACEHOLDER
from app.utils import CitingSources

## Agent Configuration
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import (
    LlmStructuredOutputSettings,
    LlmStructuredOutputType,
)

## Agent Tools
from llama_cpp_agent.tools import WebSearchTool
from llama_cpp_agent.prompt_templates import (
    web_search_system_prompt,
    research_system_prompt,
)

# Load parameters from the agent provider
default_provider_identifier = config.default_provider.get_provider_identifier()
summary_provider_identifier = config.summary_provider.get_provider_identifier()

default_identifier_str = str(default_provider_identifier).split(".")[-1]
#summary_identifier_str = str(summary_provider_identifier).split(".")[-1]  # unused

## Log startup information
logging.info(
    f"""
    server: {config.server_name}:{config.server_port},
    model: {config.default_llm_huggingface}, {config.default_llm_huggingface},
    model type: {config.default_llm_type}, {config.summary_llm_type},
    max tokens: {config.default_llm_max_tokens}, {config.summary_llm_max_tokens}, 
    providers: {default_provider_identifier}, {summary_provider_identifier},
    Loaded chat examples: {config.persona_topic_examples},
    """
)


## Run inference
def chat_response(
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
    chat_template = MessageHandler.get_messages_formatter_type(
        config.default_llm_type
    )
    model = config.default_llm_huggingface
    system_message = f"{config.persona_system_message} {config.persona_prompt_message}"
    
    chat_agent = LlamaCppAgent(
        provider=config.default_provider,  # provider, summary_provider
        system_prompt=f"{system_message}",
        predefined_messages_formatter_type=chat_template,  # chat_template, summary_chat_template
        debug_output=False,
    )
    
    logging.info(f"Loaded chat template: {chat_template}")
    
    settings = config.default_provider.get_provider_default_settings()
    settings.stream = True
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p

    if "llama_cpp_server" in default_identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "llama_cpp_python" in default_identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "tgi_server" in default_identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    elif "vllm_server" in default_identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    else:
        return "unsupported llama-cpp-agent provider:", default_identifier_str
    
    
    messages = BasicChatHistory()

    for msn in history:
        user = {"role": Roles.user, "content": msn[0]}
        assistant = {"role": Roles.assistant, "content": msn[1]}
        messages.add_message(user)
        messages.add_message(assistant)

    result = chat_agent.get_chat_response(
        f"Current Date and Time(d/m/y, h:m:s): {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n\nUser Query: "
        + message,
        llm_sampling_settings=settings,
        add_message_to_chat_history=True,
        add_response_to_chat_history=True,
        print_output=False,
    )

    outputs = ""
    for text in result:
        outputs += text
        yield outputs

def web_search_response(
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
    default_chat_template = MessageHandler.get_messages_formatter_type(
        config.default_llm_type
    )
    summary_chat_template = MessageHandler.get_messages_formatter_type(
        config.summary_llm_type
    )

    logging.info(f"Loaded chat template: {default_chat_template}")
    search_tool = WebSearchTool(
        llm_provider=config.default_provider,
        message_formatter_type=default_chat_template,
        model_max_context_tokens=config.default_llm_max_tokens,
        max_tokens_search_results=config.tokens_search_results,
        max_tokens_per_summary=config.tokens_per_summary,
        number_of_search_results=config.number_of_search_results,
    )

    web_search_agent = LlamaCppAgent(
        provider=config.summary_provider,  # provider, summary_provider
        system_prompt=web_search_system_prompt,
        predefined_messages_formatter_type=summary_chat_template,  # chat_template, summary_chat_template
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

    if "llama_cpp_server" in default_identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "llama_cpp_python" in default_identifier_str:
        settings.n_predict = max_tokens
        settings.repeat_penalty = repetition_penalty
    elif "tgi_server" in default_identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    elif "vllm_server" in default_identifier_str:
        settings.max_tokens = max_tokens
        settings.repetition_penalty = repetition_penalty
    else:
        return "unsupported llama-cpp-agent provider:", default_identifier_str

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
        f"Current Date and Time(d/m/y, h:m:s): {datetime.datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}\n\nUser Query: "
        + message,
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


## Begin Gradio UI
gradio_chat = gr.ChatInterface(
    chat_response,
    additional_inputs=[
        gr.Textbox(
            value=f"{config.persona_system_message} {config.persona_prompt_message}",
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
    # TODO: gradio theme toggle: https://github.com/SolidRusT/srt-web-search/commit/c5147aefbed1a5111ae61a8341819b28b683e10e
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
        code_background_fill_dark="#140b0b",
    ),
    css=css,
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
    submit_btn="Send",
    examples=config.persona_topic_examples,
    analytics_enabled=False,
    description="Llama-cpp-agent: Chat Agent",
    chatbot=gr.Chatbot(
        scale=1, placeholder=PLACEHOLDER, likeable=False, show_copy_button=True
    ),
)

gradio_search = gr.ChatInterface(
    web_search_response,
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
    # TODO: gradio theme toggle: https://github.com/SolidRusT/srt-web-search/commit/c5147aefbed1a5111ae61a8341819b28b683e10e
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
        code_background_fill_dark="#140b0b",
    ),
    css=css,
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
    submit_btn="Send",
    examples=config.persona_topic_examples,
    analytics_enabled=False,
    description="Llama-cpp-agent: Chat Web Search Agent",
    chatbot=gr.Chatbot(
        scale=1, placeholder=PLACEHOLDER, likeable=False, show_copy_button=True
    ),
)

## Self execute when running from a CLI
if __name__ == "__main__":
    search_port = config.server_port
    chat_port = config.server_port + 1
    
    gradio_search.launch(server_name=config.server_name, server_port=search_port)
    #gradio_chat.launch(server_name=config.server_name, server_port=chat_port)
