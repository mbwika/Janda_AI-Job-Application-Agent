import os
from huggingface_hub import hf_hub_download

model_path = "/project/rag-job-matcher/backend/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

if not os.path.exists(model_path):
    print("Model not found, downloading from Hugging Face...")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    hf_hub_download(
        repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        filename="mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        local_dir=os.path.dirname(model_path),
        local_dir_use_symlinks=False
    )
else:
    print("Model already exists, skipping download.")
