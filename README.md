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

Configure the app, then make a docker image of it.

```bash
docker build -t solidrust/srt-web-search -f Dockerfile .
```

Run the new image.

```bash
export HF_TOKEN=<your_huggingface_token>
export OPENAI_API_KEY=<your_local_openai_compatible_key>
export SERVICE_PORT=8650

docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  -p ${SERVICE_PORT}:8650 \
  --ipc=host \
  solidrust/srt-web-search:latest
```
