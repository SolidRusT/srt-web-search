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

## Running the Application

### Running Web Search UI

```bash
# Activate virtual environment
source ~/venv-vllm/bin/activate

# Run the main script with web search mode and Gradio interface
python main.py --mode web_search --interface gradio

# Deactivate the virtual environment
deactivate
```

### Running Chat UI

```bash
# Activate virtual environment
source ~/venv-vllm/bin/activate

# Run the main script with chat mode and Gradio interface
python main.py --mode chat --interface gradio

# Deactivate the virtual environment
deactivate
```

### Running Wikipedia UI

```bash
# Activate virtual environment
source ~/venv-vllm/bin/activate

# Run the main script with Wikipedia mode and Gradio interface
python main.py --mode wikipedia --interface gradio

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

## Testing

Detailed test cases for each agent can be found in the `tests/README.md` file. Ensure to follow the steps and expected results outlined for effective testing.

## Starting all agents at once

```bash
sudo apt update && sudo apt install screen

python -m venv ~/venv-srt-web-search

cd ~/repos/srt-web-search
```

```bash
screen -S gradio-chat
source ~/venv-srt-web-search/bin/activate
pip install -U -r requirements.txt --no-cache-dir
export PORT=8651 && export PERSONA=Veronica && python main.py --mode chat --interface gradio
screen -d
```

```bash
screen -S gradio-web_search
source ~/venv-srt-web-search/bin/activate
pip install -U -r requirements.txt --no-cache-dir
export PORT=8652 && export PERSONA=Default && python main.py --mode web_search --interface gradio
screen -d
```

```bash
screen -S gradio-wikipedia
source ~/venv-srt-web-search/bin/activate
pip install -U -r requirements.txt --no-cache-dir
export PORT=8653 && export PERSONA=Default && python main.py --mode wikipedia --interface gradio
screen -d
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
