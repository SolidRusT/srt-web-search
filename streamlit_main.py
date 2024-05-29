import argparse
import streamlit as st
from app.config import config
from agents.chat_agent import chat_response
from agents.web_search_agent import web_search_response
from llama_cpp_agent.prompt_templates import research_system_prompt

def setup_streamlit_interface(response_function, system_message):
    st.title("Llama-cpp-agent Interface")
    st.write(system_message)

    user_input = st.text_input("Your message:", "")
    max_tokens = st.slider("Max tokens", 1, 4096, 2048)
    temperature = st.slider("Temperature", 0.1, 4.0, 0.7)
    top_p = st.slider("Top-p", 0.1, 1.0, 0.95)
    top_k = st.slider("Top-k", 0, 100, 40)
    repetition_penalty = st.slider("Repetition penalty", 0.0, 2.0, 1.1)

    if st.button("Send"):
        history = []
        output = response_function(
            message=user_input,
            history=history,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            model=config.default_llm_huggingface
        )
        for text in output:
            st.write(text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Streamlit interface for Llama-cpp-agent.")
    parser.add_argument(
        "--mode",
        choices=["chat", "web_search"],
        required=True,
        help="Mode to run the application in",
    )
    args = parser.parse_args()

    if args.mode == "chat":
        response_function = chat_response
        system_message = f"{config.persona_system_message} {config.persona_prompt_message}"
    elif args.mode == "web_search":
        response_function = web_search_response
        system_message = research_system_prompt

    setup_streamlit_interface(response_function, system_message)
