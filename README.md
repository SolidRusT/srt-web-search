# srt-web-search

Web UI implementation using the `llama-cpp-agent` framework from [Maximilian-Winter/llama-cpp-agent](https://github.com/Maximilian-Winter/llama-cpp-agent).

## Features

- Docker image support
- Multiple llama-cpp-agent modes:
  - Chat Agent
  - Web Search Agent
  - Wikipedia Agent
- Multiple web interfaces:
  - Gradio
  - Streamlit
  - Custom

## Requirements

- Python 3.11
- Python Virtualenv
- Inference endpoint (vLLM, TGI, LlamaCppServer, LlamaCppPython)

## Installation

```bash
# Create and activate virtual environment
python -m venv ~/venv-vllm
source ~/venv-vllm/bin/activate

# Install necessary packages
pip install wheel setuptools
pip install -U -r requirements.txt

# Deactivate the virtual environment
deactivate
```

## Upgrading

```bash
# Activate virtual environment
source ~/venv-vllm/bin/activate

# Upgrade packages
pip uninstall llama_cpp_agent -y
pip install -U -r requirements.txt --no-cache-dir

# Deactivate the virtual environment
deactivate
```

## Configuration

1. Copy the `config-example.yaml` to `config.yaml`.
2. Update `config.yaml` with your own parameter values.
3. Set your CPP Agent provider and model in `config.yaml`.

## Running Web Search UI

```bash
# Create and activate virtual environment
source ~/venv-vllm/bin/activate

# Run the main script
python main.py --mode web_search --interface gradio

# Deactivate the virtual environment
deactivate
```

## Using the Docker Build

### Build the Docker Image

```bash
# Build the Docker image
docker build --progress=plain -t solidrust/srt-web-search -f Dockerfile .
```

### Run the Docker Image

```bash
# Set environment variables
export HF_TOKEN=${HF_TOKEN}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export LOCAL_SERVICE_PORT=8650
export DOCKER_IMAGE="solidrust/srt-web-search:latest"
export PERSONA=Default
# Available modes: chat, web_search, wikipedia
export AGENT_MODE="web_search"
# Available interfaces: gradio, streamlit, custom
export INTERFACE="gradio"

# Run the Docker container
docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --env "PERSONA=${PERSONA}" \
  -p ${LOCAL_SERVICE_PORT}:8650 \
  --ipc=host \
  ${DOCKER_IMAGE} python3 main.py --mode ${AGENT_MODE} --interface ${INTERFACE}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
