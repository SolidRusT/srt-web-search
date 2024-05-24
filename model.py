model_selected = "Mistral-7B-Instruct-v0.3-Q6_K.gguf"

def get_context_by_model(model_name):
    model_context_limits = {
        "Mistral-7B-Instruct-v0.3-Q6_K.gguf": 32768,
        "Meta-Llama-3-8B-Instruct-Q6_K.gguf": 8192
    }
    return model_context_limits.get(model_name, None)