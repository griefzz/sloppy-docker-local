# runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV HF_TOKEN=""

WORKDIR /app

# Install system dependencies including SSH and Jupyter for RunPod
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    openssh-server \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install comfy, model downloading deps, and JupyterLab for RunPod
RUN pip install --no-cache-dir huggingface_hub[hf_transfer] hf_transfer tqdm jupyterlab sageattention

# Last remaining comfy deps
RUN pip install xformers apex

# Install PyTorch with CUDA 12.8 support
#RUN pip install --no-cache-dir \
#    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install nunchaku
#RUN pip install https://github.com/nunchaku-tech/nunchaku/releases/download/v0.3.1/nunchaku-0.3.1+torch2.8-cp311-cp311-linux_x86_64.whl
RUN pip install https://github.com/nunchaku-tech/nunchaku/releases/download/v0.3.2/nunchaku-0.3.2+torch2.8-cp311-cp311-linux_x86_64.whl

# Clone ComfyUI at build time
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI --depth=1

# Install ComfyUI requirements
WORKDIR /app/ComfyUI
RUN pip install --no-cache-dir -r requirements.txt

# Go back to app directory and copy scripts
WORKDIR /app
COPY scripts/ /app/scripts/
COPY config/ /app/config/

RUN chmod +x /app/scripts/*.sh

# Configure SSH
RUN mkdir -p /var/run/sshd && \
    echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && \
    echo 'PasswordAuthentication no' >> /etc/ssh/sshd_config && \
    echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config

EXPOSE 8188 22

CMD ["/app/scripts/start.sh"]