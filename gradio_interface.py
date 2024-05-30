import gradio as gr
import logging
from app.config import config
from web.theme_content import css, PLACEHOLDER

class GradioInterface:
    def __init__(self, response_function, system_message, is_wikipedia=False):
        self.response_function = response_function
        self.system_message = system_message
        self.is_wikipedia = is_wikipedia

    def setup(self):
        try:
            logging.info("Setting up Gradio interface components.")
            inputs = [
                gr.Textbox(value=self.system_message, label="System message", interactive=True, visible=False),
                gr.Textbox(label="Your message", interactive=True)
            ]
            if self.is_wikipedia:
                inputs.insert(1, gr.Textbox(label="Wikipedia Page Title", interactive=True))

            async def response_fn_wrapper(system_message, message, page_title=None):
                try:
                    params = {
                        "system_message": system_message,
                        "message": message,
                        "history": [],
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "top_p": 0.95,
                        "top_k": 40,
                        "repetition_penalty": 1.1,
                        "model": config.default_llm_huggingface,
                    }
                    if self.is_wikipedia:
                        params["page_title"] = page_title

                    response_gen = self.response_function(**params)
                    response_text = ""
                    async for response in response_gen:
                        response_text += response
                        yield response_text
                except Exception as e:
                    logging.error(f"Error occurred during response generation: {e}", exc_info=True)
                    yield "An error occurred while processing your request. Please try again later."

            logging.info("Creating Gradio Interface.")
            return gr.Interface(
                fn=response_fn_wrapper,
                inputs=inputs,
                outputs=gr.Textbox(),
                theme=gr.themes.Soft(
                    primary_hue="orange",
                    secondary_hue="amber",
                    neutral_hue="gray",
                    font=[
                        gr.themes.GoogleFont("Exo"),
                        "ui-sans-serif",
                        "system-ui",
                        "sans-serif",
                    ],
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
                examples=config.persona_topic_examples,
                analytics_enabled=False,
                description="Llama-cpp-agent Interface",
            )
        except Exception as e:
            logging.error(f"Error during Gradio setup: {e}", exc_info=True)
            raise
