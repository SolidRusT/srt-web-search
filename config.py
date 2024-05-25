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
tgi_urls = os.environ.get("TGI_URLS", "tgi_default_urls")
vllm_urls = os.environ.get("VLLM_URLS", "vllm_default_urls")

# From the config.yml

tgi_default_url = random.choice(config["tgi_default_urls"])
tgi_selected_url = tgi_default_url["url"]

vllm_default_url = random.choice(config["vllm_default_urls"])
vllm_selected_url = vllm_default_url["url"]
vllm_selected_model = vllm_default_url["model"]
vllm_max_tokens = vllm_default_url["max_tokens"]

llm_model = vllm_selected_model
llm_url = vllm_selected_url
llm_max_tokens = vllm_max_tokens

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

examples = [["Latest uplifting news"],
    ["Latest news site:bloomberg.com"],
    ["Where I can find best hotel in Galapagos, Ecuador intitle:hotel"],
    ["file type:pdf book title:python"]]

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