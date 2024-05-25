# srt-web-search

Web Search using llama-cpp-agent

example: "How many NBA championship wins do the Chicago Bulls hold?"

## Inference Examples

### llama-cpp-server

```bash
pip install huggingface-hub
huggingface-cli login --token $HF_TOKEN
huggingface-cli download bartowski/Mistral-7B-Instruct-v0.3-GGUF
./server -m mistral-7b-instruct-v0.3.Q4_K_M.gguf -c 16384 -ngl 33 -b 1024 -t 6 --host 0.0.0.0 --port 8080 -np 2
```

### TGI NVIDIA

```bash
#!/bin/bash
# mosaicml/mpt-7b-instruct
# bigscience/bloomz-7b1
# tiiuae/falcon-7b-instruct
# h2oai/h2ogpt-gm-oasst1-en-2048-falcon-7b-v3
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
