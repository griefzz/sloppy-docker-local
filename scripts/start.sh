#!/bin/bash
set -e

echo "🚀 Starting ComfyUI container..."

# Setup SSH for RunPod if PUBLIC_KEY is provided
if [ ! -z "$PUBLIC_KEY" ]; then
    echo "🔐 Setting up SSH access..."
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "$PUBLIC_KEY" >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    service ssh start
    echo "✅ SSH server started"
fi

# Download models if config exists
if [ -f "/app/config/models.json" ]; then
    echo "📥 Downloading models..."
    python /app/scripts/download_models.py
fi

# Install custom nodes if config exists
if [ -f "/app/config/nodes.json" ]; then
    echo "🔧 Installing custom nodes..."
    python /app/scripts/install_nodes.py
fi

# Start ComfyUI
echo "🎨 Starting ComfyUI on port 8188..."
cd /app/ComfyUI
python main.py --listen 0.0.0.0 --port 8188