import os
import yaml
import random
import logging

# Load configuration
with open("config.yaml", "r") as stream:
    config = yaml.safe_load(stream)

debug = False

# From the environment variables
persona_name = os.environ.get("PERSONA", "Default")
server_port = int(os.environ.get("PORT", 8650))
server_name = os.environ.get("SERVER_NAME", "0.0.0.0")
backend_config = os.environ.get("BACKEND_CONFIG", "vllm")

# From the config.yml
tgi_default_url = random.choice(config["tgi_default_urls"])
tgi_selected_url = tgi_default_url["url"]
tgi_selected_model = tgi_default_url["model"]
tgi_selected_model_type = tgi_default_url["type"]
tgi_max_tokens = tgi_default_url["max_tokens"]

vllm_default_url = random.choice(config["vllm_default_urls"])
vllm_selected_url = vllm_default_url["url"]
vllm_selected_model = vllm_default_url["model"]
vllm_selected_model_type = vllm_default_url["type"]
vllm_max_tokens = vllm_default_url["max_tokens"]

llama_cpp_server_default_url = random.choice(config["llama_cpp_server_default_urls"])
llama_cpp_server_selected_url = llama_cpp_server_default_url["url"]
llama_cpp_server_selected_model = llama_cpp_server_default_url["model"]
llama_cpp_server_selected_model_type = llama_cpp_server_default_url["type"]
llama_cpp_server_max_tokens = llama_cpp_server_default_url["max_tokens"]

tgi_settings = {
    'model': tgi_selected_model,
    'model_type': tgi_selected_model_type,
    'url': tgi_selected_url,
    'max_tokens': tgi_max_tokens
}

vllm_settings = {
    'model': vllm_selected_model,
    'model_type': vllm_selected_model_type,
    'url': vllm_selected_url,
    'max_tokens': vllm_max_tokens
}
#
llama_cpp_server_settings = {
    'model': llama_cpp_server_selected_model,
    'model_type': llama_cpp_server_selected_model_type,
    'url': llama_cpp_server_selected_url,
    'max_tokens': llama_cpp_server_max_tokens
}

# Toggle between the backends
if backend_config == "tgi":
    current_settings = tgi_settings
    from llama_cpp_agent.providers import TGIServerProvider
    provider = TGIServerProvider(server_address=current_settings['url'])
elif backend_config == "vllm":
    current_settings = vllm_settings
    from llama_cpp_agent.providers import VLLMServerProvider
    provider = VLLMServerProvider(base_url=current_settings['url'], model=current_settings['model'])
elif backend_config == "llama_cpp_server":
    current_settings = llama_cpp_server_settings
    from llama_cpp_agent.providers import LlamaCppServerProvider
    provider = LlamaCppServerProvider(base_url=current_settings['url'], model=current_settings['model'])
else:
    raise ValueError("Invalid backend_config. It should be either 'tgi' or 'vllm' or 'llama_cpp_server'.")

# Use the YAML settings
llm_model = current_settings['model']
llm_model_type = current_settings['model_type']
llm_url = current_settings['url']
llm_max_tokens = current_settings['max_tokens']

ui_theme = config["personas"][persona_name]["theme"]
persona_full_name = config["personas"][persona_name]["name"]
app_title = config["personas"][persona_name]["title"]
persona_avatar_image = f"images/{config['personas'][persona_name]['avatar']}"
description = config["personas"][persona_name]["description"]
system_message = config["personas"][persona_name]["system_message"]
persona = config["personas"][persona_name]["persona"]
chat_examples = config["personas"][persona_name]["topic_examples"]
temperature = config["personas"][persona_name]["temperature"]
preferences = config["personas"][persona_name]["preferences"]

# Logging configuration
log_level = logging.DEBUG if debug else logging.INFO
logs_path = config["logs_path"]
if not os.path.exists(logs_path):
    os.makedirs(logs_path)
logging.basicConfig(
    filename=logs_path + "/client-chat-" + persona_full_name + ".log",
    level=log_level,
    format="%(asctime)s:%(levelname)s:%(message)s",
)
