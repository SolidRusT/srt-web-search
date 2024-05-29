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
export CLIENT_MODE="web_search"
# Available client_modes: chat, web_search
# The 'web_search' mode will ignore persona system prompts
docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --env "PERSONA=${PERSONA}" \
  --env "RUN_COMMAND=${RUN_COMMAND}" \
  -p ${LOCAL_SERVICE_PORT}:8650 \
  --ipc=host \
  ${DOCKER_IMAGE} python3 main.py --mode ${CLIENT_MODE}
```
