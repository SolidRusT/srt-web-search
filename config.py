import os
import yaml
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

        # Load provider configuration
        self.default_llm_name = "Default"
        self.summary_llm_name = "Summary"
        self.load_provider_settings()

        # Load persona specific settings
        self.load_persona_settings()

        # Setup logging
        self.setup_logging()

    def load_provider_settings(self):
        # Load default LLM from yaml config
        default_llm = self.config["llms"][self.default_llm_name]
        self.default_llm_url = default_llm["url"]
        self.default_llm_type = default_llm["type"]
        self.default_llm_model = default_llm["model"]
        self.default_llm_max_tokens = default_llm["max_tokens"]
        # Load summary LLM from yaml config
        summary_llm = self.config["llms"][self.summary_llm_name]
        self.summary_llm_url = summary_llm["url"]
        self.summary_llm_type = summary_llm["type"]
        self.summary_llm_model = summary_llm["model"]
        self.summary_llm_max_tokens = summary_llm["max_tokens"]


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
