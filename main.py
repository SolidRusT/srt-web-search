# Defaults
import logging
import gradio as gr
# Locals
from config import config
from llama_cpp_agent.providers import LlamaCppServerProvider, VLLMServerProvider
from messages import MessageHandler
from content import css, PLACEHOLDER
from utils import CitingSources
# Agents
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import (
    LlmStructuredOutputSettings,
    LlmStructuredOutputType,
)
# Tools
from llama_cpp_agent.tools import WebSearchTool
from llama_cpp_agent.prompt_templates import web_search_system_prompt, research_system_prompt

# Ensure configurations are loaded before accessing them in global scope
model="solidrust/Mistral-7B-instruct-v0.3-AWQ"
#provider = config.current_settings[1]
#provider = VLLMServerProvider(
#    base_url="http://thanatos:8000/v1", model=model, huggingface_model=model,
#  )
# provider = LlamaCppServerProvider("http://hades:8084")
provider = LlamaCppServerProvider("http://hades.hq.solidrust.net:8084")
print("Current provider:", provider)
provider_identifier = provider.get_provider_identifier()
# provider.get_provider_identifier()
#    llama_cpp_server = "llama_cpp_server"
#    llama_cpp_python = "llama_cpp_python"
#    tgi_server = "text_generation_inference"
#    vllm_server = "vllm"

llm_model_type = config.current_settings[0]["model_type"]
server_name = config.server_name
server_port = config.server_port
llm_max_tokens = config.current_settings[0]["max_tokens"]
chat_examples = config.chat_examples

# Log startup information
logging.info(
    f"""
    server: {server_name}:{server_port},
    model: {model},
    model type: {llm_model_type},
    max tokens: {llm_max_tokens}, 
    provider: {provider_identifier},
    Loaded chat examples: {chat_examples},
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

    logging.info(f"Loaded chat examples: {chat_template}")
    search_tool = WebSearchTool(
        llm_provider=provider,
        message_formatter_type=chat_template,
        max_tokens_search_results=12000,
        max_tokens_per_summary=2048,
    )

    web_search_agent = LlamaCppAgent(
        provider,
        system_prompt=web_search_system_prompt,
        predefined_messages_formatter_type=chat_template,
        debug_output=True,
    )

    answer_agent = LlamaCppAgent(
        provider,
        system_prompt=research_system_prompt,
        predefined_messages_formatter_type=chat_template,
        debug_output=True,
    )

    settings = provider.get_provider_default_settings()
    settings.stream = False
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p
    ## vLLM Provider Settings
    #settings.max_tokens = max_tokens
    #settings.repetition_penalty = repetition_penalty
    ## CPPServer Settings
    settings.n_predict = max_tokens
    settings.repeat_penalty = repetition_penalty

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
        message,
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
            value=web_search_system_prompt,
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
        primary_hue="violet",
        secondary_hue="violet",
        neutral_hue="gray",
        font=[gr.themes.GoogleFont("Exo"), "ui-sans-serif", "system-ui", "sans-serif"],
    ).set(
        body_background_fill_dark="#111111",
        block_background_fill_dark="#111111",
        block_border_width="1px",
        block_title_background_fill_dark="#1e1c26",
        input_background_fill_dark="#292733",
        button_secondary_background_fill_dark="#24212b",
        border_color_primary_dark="#343140",
        background_fill_secondary_dark="#111111",
        color_accent_soft_dark="transparent",
    ),
    css=css,
    retry_btn="Retry",
    undo_btn="Undo",
    clear_btn="Clear",
    submit_btn="Send",
    examples=(chat_examples),
    analytics_enabled=False,
    description="Llama-cpp-agent: Chat Web Search Agent",
    chatbot=gr.Chatbot(scale=1, placeholder=PLACEHOLDER),
)

if __name__ == "__main__":
    main.launch(server_name=server_name, server_port=server_port)
