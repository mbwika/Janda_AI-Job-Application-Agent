#!/bin/bash

MODEL_DIR="./models"
MODEL_FILE="mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/$MODEL_FILE"

# Create model directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model file exists
if [ -f "$MODEL_PATH" ]; then
    echo "✅ Model file already exists: $MODEL_PATH"
else
    echo "⬇️ Downloading model from Hugging Face..."
    wget -O "$MODEL_PATH" "$MODEL_URL"

    if [ $? -eq 0 ]; then
        echo "✅ Model downloaded successfully to $MODEL_PATH"
    else
        echo "❌ Failed to download the model. Check the URL or your internet connection."
        exit 1
    fi
fi
