# srt-web-search

Web UI implementation using the `llama-cpp-agent` framework from [Maximilian-Winter/llama-cpp-agent](https://github.com/Maximilian-Winter/llama-cpp-agent).

## Features

- Docker image support
- Multiple llama-cpp-agent modes:
  - Chat Agent
  - WebSearch Agent
  - Wikipedia Agent
- Multiple web interfaces
  - gradio
  - streamlit
  - custom

## Requirements

- Python 3.11
- Python Virtualenv
- Inference endpoint (vLLM, TGI, LamaCPPServer, LlamaCPPPython)

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

Set your CPP Agent provider and model in `config.yaml`.

## Running Web Search UI

```bash
python -m venv ~/venv-vllm
source ~/venv-vllm/bin/activate

python main.py

deactivate
```

## Using the Docker build

Configure a `config.yaml` file, then make a docker image with it.

```bash
docker build --progress=plain -t solidrust/srt-web-search -f Dockerfile .
```

Run the new image.

```bash
export HF_TOKEN=${HF_TOKEN}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export LOCAL_SERVICE_PORT=8650
export DOCKER_IMAGE="solidrust/srt-web-search:latest"
export PERSONA=Default
# Available modes: chat, web_search
export AGENT_MODE="web_search"
# Available interfaces: gradio, streamlit, custom
export INTERFACE="gradio"

docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --env "PERSONA=${PERSONA}" \
  -p ${LOCAL_SERVICE_PORT}:8650 \
  --ipc=host \
  ${DOCKER_IMAGE} python3 main.py --mode ${AGENT_MODE} --interface ${INTERFACE}
```
