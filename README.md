# srt-web-search

Web Search using llama-cpp-agent

## Requirements

- Python 3.11
- Python Virtualenv

## Installation

```bash
python -m venv ~/venv-vllm
source ~/venv-vllm/bin/activate

pip install wheel setuptools
pip install -U -r requirements.txt

deactivate
```

## Upgrading

```bash
python -m venv ~/venv-vllm
source ~/venv-vllm/bin/activate

pip uninstall llama_cpp_agent -y
pip install -U -r requirements.txt --no-cache-dir

deactivate
```

## Configuration

Copy the `config-example.yaml` to `config.yaml`, and update it with your own parameter values.

Set your CPP Agent provider and model in `main.py`.

```python
from llama_cpp_agent.providers import VLLMServerProvider

model = "solidrust/Mistral-7B-instruct-v0.3-AWQ"
llm_model_type = "Mistral"  # config.current_settings[0]["model_type"]
llm_max_tokens = 16384  # config.current_settings[0]["max_tokens"]
tokens_per_summary = 2048
tokens_search_results = 8192

provider = VLLMServerProvider(
    base_url="http://localhost:8000/v1",
    model=model,
    huggingface_model=model,
)
```

## Running Web Search UI

```bash
python -m venv ~/venv-vllm
source ~/venv-vllm/bin/activate

python main.py

deactivate
```

## Using the Docker build

Configure the app, then make a docker image of it.

```bash
#export HF_TOKEN=<your_huggingface_token>
#export OPENAI_API_KEY=<your_local_openai_compatible_key>
docker build -t solidrust/srt-web-search -f Dockerfile .
```

Run the new image.

```bash
docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  -p 8650:8650 \
  --ipc=host \
  solidrust/srt-web-search
```
