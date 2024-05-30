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
        components = [
            gr.Textbox(label="Your message", interactive=True),
        ]
        
        if self.is_wikipedia:
            components.append(gr.Textbox(label="Wikipedia Page Title", interactive=True))
        
        components += [
            gr.Textbox(value=self.system_message, label="System message", interactive=True, visible=False),
            gr.Slider(minimum=1, maximum=4096, value=2048, step=1, label="Max tokens"),
            gr.Slider(minimum=0.1, maximum=4.0, value=0.7, step=0.1, label="Temperature"),
            gr.Slider(minimum=0.1, maximum=1.0, value=0.95, step=0.05, label="Top-p"),
            gr.Slider(minimum=0, maximum=100, value=40, step=1, label="Top-k"),
            gr.Slider(
                minimum=0.0,
                maximum=2.0,
                value=1.1,
                step=0.1,
                label="Repetition penalty",
            ),
        ]

        async def response_fn_wrapper(*args):
            try:
                inputs = list(args)
                params = {
                    "message": inputs.pop(0),
                    "history": [],  # Empty history
                    "system_message": inputs.pop(-6),  # System message
                    "max_tokens": inputs.pop(-5),
                    "temperature": inputs.pop(-4),
                    "top_p": inputs.pop(-3),
                    "top_k": inputs.pop(-2),
                    "repetition_penalty": inputs.pop(-1),
                    "model": config.default_llm_huggingface,
                }

                if self.is_wikipedia:
                    params["page_title"] = inputs.pop(0)
                
                response_gen = self.response_function(**params)
                response_text = ""
                async for response in response_gen:
                    response_text += response
                    yield response_text
            except Exception as e:
                logging.error(f"Error occurred during response generation: {e}", exc_info=True)
                yield "An error occurred while processing your request. Please try again later."

        return gr.ChatInterface(
            response_fn_wrapper,
            additional_inputs=components,
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
            retry_btn="Retry",
            undo_btn="Undo",
            clear_btn="Clear",
            submit_btn="Send",
            examples=config.persona_topic_examples,
            analytics_enabled=False,
            description="Llama-cpp-agent Interface",
            chatbot=gr.Chatbot(
                scale=1, placeholder=PLACEHOLDER, likeable=False, show_copy_button=True
            ),
        )

