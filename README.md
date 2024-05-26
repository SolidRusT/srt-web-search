# srt-web-search

Web Search using llama-cpp-agent

example: "How many NBA championship wins do the Chicago Bulls hold?"

## Inference Examples

### llama-cpp-server

```bash
#!/bin/bash
model_file="Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"
model_repo="bartowski/Mistral-7B-Instruct-v0.3-GGUF"
# Download the model
pip install -U "huggingface_hub[cli]"
huggingface-cli login --token $HF_TOKEN
huggingface-cli whoami
huggingface-cli download $model_repo $model_file
# Run the llama CPP Server
# not this one "pip install llama-cpp-python[server]"
./server -m $model_file -c 16384 -ngl 33 -b 1024 -t 6 --host 0.0.0.0 --port 8080 -np 2
# ./server -m Mistral-7B-Instruct-v0.3.Q6_K.gguf -c 128000 -ngl 33 -b 1024 -t 10 -fa --grp-attn-n 4 --grp-attn-w 16384 --port 8084 --host 0.0.0.0
```

### TGI NVIDIA

```bash
#!/bin/bash
# model="solidrust/Mistral-7B-instruct-v0.3-AWQ"
model=${MODEL}
num_shard=${NUM_SHARD}
volume="${HOME}/${HOSTNAME}-AI/text-generation" # share a volume
service_version=${SERVICE_VERSION}
service_port=${SERVICE_PORT}
max_input_length=${MAX_INPUT_LENGTH}
max_total_tokens=${MAX_TOTAL_TOKENS}
max_batch_prefill_tokens=${MAX_PREFILL_TOKENS}
gpus=${GPUS}
image_uri=${IMAGE_URI}
token=${HUGGING_FACE_HUB_TOKEN}

# test
#docker run --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
# --gpus '"device=0,2"'

# update the cache
docker pull $image_uri:$service_version

# run
docker run --gpus "device=$gpus" --shm-size 4g -p $service_port:80 \
  -e HUGGING_FACE_HUB_TOKEN=$token \
  -v $volume:/data $image_uri:$service_version \
  --model-id $model --num-shard $num_shard \
  --trust-remote-code \
  --max-concurrent-requests 128 \
  --max-best-of 2 \
  --max-stop-sequences 4 \
  --max-input-length $max_input_length \
  --max-total-tokens $max_total_tokens \
  --max-batch-prefill-tokens $max_batch_prefill_tokens \
  --quantize awq
```

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
    --device auto \
    --engine-use-ray \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.90 \
    --quantization awq \
    --max-model-len 32768
```

## Thanatos inference vLLM

```bash
docker run --runtime nvidia --gpus all     -v ~/.cache/huggingface:/root/.cache/huggingface     --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}"     -p 8081:8000     --ipc=host     vllm/vllm-openai:latest     --model solidrust/Mistral-7B-instruct-v0.3-AWQ --tokenizer solidrust/Mistral-7B-instruct-v0.3-AWQ --trust-remote-code --dtype auto --device auto --gpu-memory-utilization 0.98 --quantization awq  --max-model-len 28350 --enforce-eager
```

```bash
curl -f -X POST http://thanatos:8081/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "solidrust/Mistral-7B-instruct-v0.3-AWQ",
    "prompt": "Role: You are a creative and imaginative storywriter.\nInstruction: Write a simple and engaging poem about who kicked my dog.\nInput:",
    "max_tokens": 512,
    "temperature": 5
  }'
```

## Zelus inference vLLM

```bash
docker run --runtime nvidia --gpus all     -v ~/.cache/huggingface:/root/.cache/huggingface     --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}"     -p 8081:8000     --ipc=host     vllm/vllm-openai:latest     --model solidrust/Meta-Llama-3-8B-Instruct-AWQ --tokenizer solidrust/Meta-Llama-3-8B-Instruct-AWQ --trust-remote-code --dtype auto --device auto --gpu-memory-utilization 0.98 --quantization awq --max-model-len 8192 --enforce-eager
```

```bash
curl -f -X POST http://zelus:8081/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "solidrust/Meta-Llama-3-8B-Instruct-AWQ",
    "prompt": "Role: You are a creative and imaginative storywriter.\nInstruction: Write a simple and engaging poem about who kicked my dog.\nInput:",
    "max_tokens": 512,
    "temperature": 5
  }'
```

## Docker build

```bash
docker build -t solidrust/srt-web-search -f Dockerfile .
docker run \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=${HF_TOKEN}" \
  --env "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  -p 8650:8650 \
  --ipc=host \
  solidrust/srt-web-search
```
