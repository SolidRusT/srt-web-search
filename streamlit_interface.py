import os

import streamlit as st
import logging
from app.config import config
from ui_provider_base import UIProvider


class StreamlitInterface(UIProvider):

    def __init__(self, response_function, system_message, is_wikipedia=False):
        self.response_function = response_function
        self.system_message = system_message
        self.is_wikipedia = is_wikipedia

    def setup_ui(self):
        try:
            logging.info("Setting up Streamlit interface components.")
            st.title("Llama-cpp-agent Interface")
            st.write(self.system_message)

            page_title = None
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
                params = {
                    "system_message": self.system_message,
                    "message": user_input,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "repetition_penalty": repetition_penalty,
                    "model": config.default_llm_huggingface,
                    "history": history,
                }

                if self.is_wikipedia:
                    params["page_title"] = page_title

                try:
                    response_gen = self.response_function(**params)
                    response_text = ""
                    for response in self._handle_async_generator(response_gen):
                        response_text += response
                        st.write(response_text)
                except Exception as e:
                    logging.error(f"Error occurred during response generation: {e}", exc_info=True)
                    st.error("An error occurred while processing your request. Please try again later.")
        except Exception as e:
            logging.error(f"Error during Streamlit setup: {e}", exc_info=True)
            st.error("An error occurred while setting up the interface. Please check the logs for more details.")

    async def _handle_async_generator(self, async_gen):
        try:
            async for item in async_gen:
                yield item
        except Exception as e:
            logging.error(f"Error in async generator handling: {e}", exc_info=True)
            yield "An error occurred while processing the response."

    def start_ui_provider(self, args):
        os.system(f"streamlit run streamlit_main.py --server.port {config.server_port} -- --mode {args.mode}")
