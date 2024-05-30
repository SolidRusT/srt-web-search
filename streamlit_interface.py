import streamlit as st
import asyncio
import logging
from app.config import config

class StreamlitInterface:
    def __init__(self, response_function, system_message, is_wikipedia=False):
        self.response_function = response_function
        self.system_message = system_message
        self.is_wikipedia = is_wikipedia

    def run(self):
        st.title("Llama-cpp-agent Interface")
        st.write(self.system_message)

        page_title = ""
        if self.is_wikipedia:
            page_title = st.text_input("Wikipedia Page Title:", "")
        user_input = st.text_input("Your message:", "")
        max_tokens = st.slider("Max tokens", 1, 4096, 2048)
        temperature = st.slider("Temperature", 0.1, 4.0, 0.7)
        top_p = st.slider("Top-p", 0.1, 1.0, 0.95)
        top_k = st.slider("Top-k", 0, 100, 40)
        repetition_penalty = st.slider("Repetition penalty", 0.0, 2.0, 1.1)

        if st.button("Send"):
            history = []
            response_text = ""

            async def fetch_response():
                try:
                    async for response in self.response_function(
                        message=user_input,
                        history=history,
                        system_message=self.system_message,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        top_k=top_k,
                        repetition_penalty=repetition_penalty,
                        model=config.default_llm_huggingface,
                        page_title=page_title if self.is_wikipedia else None
                    ):
                        nonlocal response_text
                        response_text += response
                        st.write(response_text)
                except Exception as e:
                    logging.error(f"Error occurred during response generation: {e}")
                    st.write("An error occurred while processing your request. Please try again later.")

            asyncio.run(fetch_response())
