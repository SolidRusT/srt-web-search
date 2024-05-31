import os
import yaml
import logging


class Config:
    def __init__(self):
        # Load configuration from yaml file
        with open("config.yaml", "r") as stream:
            self.config = yaml.safe_load(stream)

        # Check for 'debugging' variable in yaml
        self.debug = self.config.get("debug", False)

        # From environment variables
        self.persona_name = os.environ.get("PERSONA", "Default")
        self.server_port = int(os.environ.get("PORT", 8650))
        self.server_name = os.environ.get("SERVER_NAME", "0.0.0.0")

        # Load provider configuration
        self.default_llm_name = self.get_first_existing_value(
            ["llm_default", "llms.default"], "default"
        )
        self.summary_llm_name = self.get_first_existing_value(
            ["llm_summary", "llms.summary"], "summary"
        )
        self.chat_llm_name = self.get_first_existing_value(
            ["llm_chat", "llms.chat"], "default"
        )
        self.load_provider_settings()

        # Load Agent Tools
        self.load_tools_config()
        self.load_rag_pipeline()

        # Load persona specific settings
        self.load_persona_settings()

        # Setup logging
        self.setup_logging()

    def get_first_existing_value(self, keys, default_value):
        for key in keys:
            parts = key.split(".")
            value = self.config
            try:
                for part in parts:
                    value = value[part]
                return value
            except KeyError:
                continue
        return default_value

    def load_llm_settings(self, llm_name):
        llm_config = self.config["llms"][llm_name]
        return {
            "type": llm_config["type"],
            "filename": llm_config["filename"],
            "huggingface": llm_config["huggingface"],
            "url": llm_config["url"],
            "agent_provider": llm_config["agent_provider"],
            "server_name": llm_config["server"],
            "max_tokens": llm_config["max_tokens"],
        }

    def set_llm_attributes(self, llm_prefix, llm_settings):
        setattr(self, f"{llm_prefix}_llm_type", llm_settings["type"])
        setattr(self, f"{llm_prefix}_llm_filename", llm_settings["filename"])
        setattr(self, f"{llm_prefix}_llm_huggingface", llm_settings["huggingface"])
        setattr(self, f"{llm_prefix}_llm_url", llm_settings["url"])
        setattr(self, f"{llm_prefix}_llm_agent_provider", llm_settings["agent_provider"])
        setattr(self, f"{llm_prefix}_llm_server_name", llm_settings["server_name"])
        setattr(self, f"{llm_prefix}_llm_max_tokens", llm_settings["max_tokens"])

    def load_provider_settings(self):
        self.default_llm_settings = self.load_llm_settings(self.default_llm_name)
        self.summary_llm_settings = self.load_llm_settings(self.summary_llm_name)
        self.chat_llm_settings = self.load_llm_settings(self.chat_llm_name)

        self.set_llm_attributes('default', self.default_llm_settings)
        self.set_llm_attributes('summary', self.summary_llm_settings)
        self.set_llm_attributes('chat', self.chat_llm_settings)

        # Provider specific settings for default LLM
        if "llama_cpp_server" in self.default_llm_settings["agent_provider"]:
            from llama_cpp_agent.providers import LlamaCppServerProvider
            self.default_provider = LlamaCppServerProvider(self.default_llm_settings["url"])
            self.default_summary = LlamaCppServerProvider(self.summary_llm_settings["url"])
            self.default_chat = LlamaCppServerProvider(self.chat_llm_settings["url"])
        elif "llama_cpp_python" in self.default_llm_settings["agent_provider"]:
            from llama_cpp import Llama
            from llama_cpp_agent.providers import LlamaCppPythonProvider
            python_cpp_llm = Llama(
                model_path=f"models/{self.default_llm_settings['filename']}",
                flash_attn=True,
                n_threads=40,
                n_gpu_layers=81,
                n_batch=1024,
                n_ctx=self.default_llm_settings["max_tokens"],
            )
            self.default_provider = LlamaCppPythonProvider(python_cpp_llm)
            self.summary_provider = LlamaCppPythonProvider(python_cpp_llm)
            self.chat_provider = LlamaCppPythonProvider(python_cpp_llm)
        elif "tgi_server" in self.default_llm_settings["agent_provider"]:
            from llama_cpp_agent.providers import TGIServerProvider
            self.default_provider = TGIServerProvider(server_address=self.default_llm_settings["url"])
            self.summary_provider = TGIServerProvider(server_address=self.summary_llm_settings["url"])
            self.chat_provider = TGIServerProvider(server_address=self.chat_llm_settings["url"])
        elif "vllm_server" in self.default_llm_settings["agent_provider"]:
            from llama_cpp_agent.providers import VLLMServerProvider
            self.default_provider = VLLMServerProvider(
                base_url=self.default_llm_settings["url"],
                model=self.default_llm_settings["huggingface"],
                huggingface_model=self.default_llm_settings["huggingface"],
            )
            self.summary_provider = VLLMServerProvider(
                base_url=self.summary_llm_settings["url"],
                model=self.summary_llm_settings["huggingface"],
                huggingface_model=self.summary_llm_settings["huggingface"],
            )
            self.chat_provider = VLLMServerProvider(
                base_url=self.chat_llm_settings["url"],
                model=self.chat_llm_settings["huggingface"],
                huggingface_model=self.chat_llm_settings["huggingface"],
            )
        else:
            return (
                "unsupported llama-cpp-agent provider:",
                self.default_llm_settings["agent_provider"],
                self.summary_llm_settings["agent_provider"],
                self.chat_llm_settings["agent_provider"],
            )

    def load_rag_pipeline(self):
        self.embeddings_llm = self.get_first_existing_value(
            ["llm_embeddings", "llms.embeddings"], "BAAI/bge-small-en-v1.5"
        )
        self.embedding_model = self.config["llm_embeddings"]

    def load_tools_config(self):
        self.tokens_per_summary = self.config["tokens_per_summary"]
        self.tokens_search_results = self.config["tokens_search_results"]
        self.number_of_search_results = self.config["number_of_search_results"]

    def load_persona_settings(self):
        persona = self.config["personas"][self.persona_name]
        self.persona_ui_theme = persona["theme"]
        self.persona_full_name = persona["name"]
        self.persona_app_title = persona["title"]
        self.persona_avatar_image = f"images/{persona['avatar']}"
        self.persona_description = persona["description"]
        self.persona_system_message = persona["system_message"]
        self.persona_prompt_message = persona["persona"]
        self.persona_topic_examples = persona["topic_examples"]
        self.persona_temperature = persona["temperature"]
        self.persona_preferences = persona["preferences"]

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
