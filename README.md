# srt-web-search

Web Search using llama-cpp-agent

example: "How many NBA championship wins do the Chicago Bulls hold?"

## Inference Examples

### llama-cpp-server

### TGI NVIDIA

### vLLM NVIDIA

```bash
# https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
#model="mistralai/Mistral-7B-instruct-v0.3"
model="solidrust/Mistral-7B-instruct-v0.3-AWQ"
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
    -p 8081:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model $model --tokenizer $model \
    --trust-remote-code \
    --dtype auto \
    --quantization awq \
    --max-model-len 18000
```
