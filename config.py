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
        self.default_llm_name = "default"
        self.summary_llm_name = "summary"
        self.load_provider_settings()
        self.load_tools_config()

        # Load persona specific settings
        self.load_persona_settings()

        # Setup logging
        self.setup_logging()

    def load_provider_settings(self):
        # Load default LLM from yaml config
        default_llm = self.config["llms"][self.default_llm_name]
        self.default_llm_type = default_llm["type"]
        self.default_llm_filename = default_llm["filename"]
        self.default_llm_huggingface = default_llm["huggingface"]
        self.default_llm_url = default_llm["url"]
        self.default_llm_agent_provider = default_llm["agent_provider"]
        self.default_llm_server_name = default_llm["server"]
        self.default_llm_max_tokens = default_llm["max_tokens"]
        # Load summary LLM from yaml config
        summary_llm = self.config["llms"][self.summary_llm_name]
        self.summary_llm_type = summary_llm["type"]
        self.summary_llm_filename = summary_llm["filename"]
        self.summary_llm_huggingface = summary_llm["huggingface"]
        self.summary_llm_url = summary_llm["url"]
        self.summary_llm_agent_provider = summary_llm["agent_provider"]
        self.summary_llm_server_name = summary_llm["server"]
        self.summary_llm_max_tokens = summary_llm["max_tokens"]

        # Provider specific settings
        if "llama_cpp_server" in self.summary_llm_agent_provider:
            from llama_cpp_agent.providers import LlamaCppServerProvider

            self.default_provider = LlamaCppServerProvider(self.default_llm_url)
            self.summary_provider = LlamaCppServerProvider(self.summary_llm_url)
        elif "llama_cpp_python" in self.summary_llm_agent_provider:
            from llama_cpp import Llama
            from llama_cpp_agent.providers import LlamaCppPythonProvider

            # TODO: add HF download logic here
            # hf download {huggingface} {filename}
            python_cpp_llm = Llama(
                model_path=f"models/{self.summary_llm_filename}",
                flash_attn=True,
                n_threads=40,
                n_gpu_layers=81,
                n_batch=1024,
                n_ctx=self.default_llm_max_tokens,
            )
            self.default_provider = LlamaCppPythonProvider(python_cpp_llm)
            self.summary_provider = LlamaCppPythonProvider(python_cpp_llm)
        elif "tgi_server" in self.summary_llm_agent_provider:
            from llama_cpp_agent.providers import TGIServerProvider

            self.default_provider = TGIServerProvider(self.default_llm_url)
            self.summary_provider = TGIServerProvider(self.summary_llm_url)
        elif "vllm_server" in self.summary_llm_agent_provider:
            from llama_cpp_agent.providers import VLLMServerProvider

            self.default_provider = VLLMServerProvider(
                base_url=self.default_llm_url,
                model=self.default_llm_huggingface,
                huggingface_model=self.default_llm_huggingface,
                # api_key
            )
            self.summary_provider = VLLMServerProvider(
                base_url=self.summary_llm_url,
                model=self.summary_llm_huggingface,
                huggingface_model=self.summary_llm_huggingface,
                # api_key
            )
        else:
            self.default_provider = "unsupported"
            self.summary_provider = "unsupported"
            return (
                "unsupported llama-cpp-agent provider:",
                self.default_llm_agent_provider,
                self.summary_llm_agent_provider,
            )

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
