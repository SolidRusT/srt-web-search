import os
import gradio as gr
from utils import CitingSources
from content import css, PLACEHOLDER
from messages import get_messages_formatter_type, write_message_to_user
from search import search_web
from llama_cpp_agent import LlamaCppAgent
from llama_cpp_agent.providers import TGIServerProvider, LlamaCppServerProvider, VLLMServerProvider

# for VLLMServerProvider depends:
from openai import OpenAI

from llama_cpp_agent.chat_history import BasicChatHistory
from llama_cpp_agent.chat_history.messages import Roles
from llama_cpp_agent.llm_output_settings import (
    LlmStructuredOutputSettings,
    LlmStructuredOutputType,
)

server_port = int(os.environ.get("PORT", 8650))
server_name = os.environ.get("SERVER_NAME", "0.0.0.0")
llm = "solidrust/Mistral-7B-instruct-v0.3-AWQ"

def respond(
    message,
    history: list[tuple[str, str]],
    system_message,
    max_tokens,
    temperature,
    top_p,
    top_k,
    repeat_penalty,
    model,
):
    template = "Mistral"

    # provider = LlamaCppServerProvider("http://hades.hq.solidrust.net:8084")
    # provider = TGIServerProvider("http://thanatos.hq.solidrust.net:8082")
    #provider = TGIServerProvider("http://thanatos:8081")  # SRT HQ Internal
    provider = VLLMServerProvider("http://thanatos:8082/v1",model=llm)  # SRT HQ Internal

    chat_template = get_messages_formatter_type(template)

    agent = LlamaCppAgent(
        provider,
        system_prompt=f"{system_message}",
        predefined_messages_formatter_type=chat_template,
        debug_output=True,
    )

    settings = provider.get_provider_default_settings()
    settings.stream = False
    settings.temperature = temperature
    settings.top_k = top_k
    settings.top_p = top_p
    settings.max_tokens = 1024
    settings.repetition_penalty = repeat_penalty
    output_settings = LlmStructuredOutputSettings.from_functions(
        [search_web, write_message_to_user]
    )
    messages = BasicChatHistory()

    for msn in history:
        user = {"role": Roles.user, "content": msn[0]}
        assistant = {"role": Roles.assistant, "content": msn[1]}
        messages.add_message(user)
        messages.add_message(assistant)
    result = agent.get_chat_response(
        message,
        llm_sampling_settings=settings,
        structured_output_settings=output_settings,
        chat_history=messages,
        print_output=False,
    )
    while True:
        print(result)
        if result[0]["function"] == "write_message_to_user":
            break
        else:
            result = agent.get_chat_response(
                result[0]["return_value"],
                role=Roles.tool,
                llm_sampling_settings=settings,
                chat_history=messages,
                structured_output_settings=output_settings,
                print_output=False,
            )

    stream = agent.get_chat_response(
        result[0]["return_value"],
        role=Roles.tool,
        llm_sampling_settings=settings,
        chat_history=messages,
        returns_streaming_generator=False,
        print_output=False,
    )
    outputs = ""
    outputs += stream
    yield outputs
 
    output_settings = LlmStructuredOutputSettings.from_pydantic_models(
        [CitingSources], LlmStructuredOutputType.object_instance
    )
    
    citing_sources = agent.get_chat_response(
        "Please cite the sources you used in your response.",
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


main = gr.ChatInterface(
    respond,
    additional_inputs=[
        gr.Textbox(
            value="You are a helpful assistant. Use additional available information you have access to when giving a response. Always give detailed and long responses. Format your response, well structured in markdown format.",
            label="System message",
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
    description="Llama-cpp-agent: Chat Web Search DDG Agent",
    chatbot=gr.Chatbot(scale=1, placeholder=PLACEHOLDER),
)

if __name__ == "__main__":
    main.launch(server_name=server_name, server_port=server_port)
