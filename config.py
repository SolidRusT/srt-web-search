import os
import yaml
import random
import logging


class Config:
    def __init__(self):
        self.debug = False

        # Load configuration from yaml file
        with open("config.yaml", "r") as stream:
            self.config = yaml.safe_load(stream)

        # From environment variables
        self.persona_name = os.environ.get("PERSONA", "Default")
        self.server_port = int(os.environ.get("PORT", 8650))
        self.server_name = os.environ.get("SERVER_NAME", "0.0.0.0")
        #self.backend_config = os.environ.get("BACKEND_CONFIG", "vllm")

        # From the config.yaml
        #self.tgi_default_url = random.choice(self.config["tgi_default_urls"])
        #self.vllm_default_url = random.choice(self.config["vllm_default_urls"])
        #self.llama_cpp_server_default_url = random.choice(
        #    self.config["llama_cpp_server_default_urls"]
        #)

        # Settings based on the selected backend
        #self.tgi_settings = self.get_settings(self.tgi_default_url)
        #self.vllm_settings = self.get_settings(self.vllm_default_url)
        #self.llama_cpp_server_settings = self.get_settings(
        #    self.llama_cpp_server_default_url
        #)

        self.current_settings = self.get_current_settings()

        # Load persona specific settings
        self.load_persona_settings()

        # Setup logging
        self.setup_logging()

    #def get_settings(self, default_url):
    #    return {
    #        "model": default_url["model"],
    #        "model_type": default_url["type"],
    #        "url": default_url["url"],
    #        "max_tokens": default_url["max_tokens"],
    #    }

    def get_current_settings(self):
        if self.backend_config == "tgi":
            from llama_cpp_agent.providers import TGIServerProvider

            return self.tgi_settings, TGIServerProvider(
                server_address=self.tgi_settings["url"]
            )
        elif self.backend_config == "vllm":
            from llama_cpp_agent.providers import VLLMServerProvider

            return self.vllm_settings, VLLMServerProvider(
                base_url=self.vllm_settings["url"], model=self.vllm_settings["model"], huggingface_model=self.vllm_settings["model"]
            )
        elif self.backend_config == "llama_cpp_server":
            from llama_cpp_agent.providers import LlamaCppServerProvider

            return self.llama_cpp_server_settings, LlamaCppServerProvider(
                server_address=self.llama_cpp_server_settings["url"],
                llama_cpp_python_server=self.llama_cpp_server_settings[True],
            )
        else:
            raise ValueError(
                "Invalid backend_config. It should be either 'tgi' or 'vllm' or 'llama_cpp_server'."
            )

    def load_persona_settings(self):
        persona = self.config["personas"][self.persona_name]
        self.ui_theme = persona["theme"]
        self.persona_full_name = persona["name"]
        self.app_title = persona["title"]
        self.persona_avatar_image = f"images/{persona['avatar']}"
        self.description = persona["description"]
        self.system_message = persona["system_message"]
        self.persona = persona["persona"]
        self.topic_examples = persona["topic_examples"]
        self.temperature = persona["temperature"]
        self.preferences = persona["preferences"]

    def setup_logging(self):
        log_level = logging.DEBUG if self.debug else logging.INFO
        logs_path = self.config["logs_path"]
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
        logging.basicConfig(
            filename=f"{logs_path}/client-chat-{self.persona_full_name}.log",
            level=log_level,
            format="%(asctime)s:%(levelname)s:%(message)s",
        )


config = Config()
