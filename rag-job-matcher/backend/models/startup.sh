#!/bin/bash
python3 /models/download_model.py
/server --model $MODEL --host 0.0.0.0 --port 8000


