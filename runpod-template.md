# RunPod Template Configuration

## Container Settings
- **Container Image**: Build from this repository
- **Container Disk**: 20GB minimum (50GB+ recommended for multiple models)
- **Expose HTTP Ports**: 8188 (ComfyUI), 22 (SSH)
- **Environment Variables**:
  - `HF_HUB_ENABLE_HF_TRANSFER=1`
  - `HF_TOKEN=your_huggingface_token_here` (required for gated models like Flux)
  - `PUBLIC_KEY=your_ssh_public_key_here` (optional, enables SSH access)

## Volume Mounts (Optional but Recommended)
- `/app/config` - Mount your configuration files
- `/app/ComfyUI/models` - Persistent model storage
- `/app/ComfyUI/output` - Persistent output storage

## Usage
1. Copy your configuration files to the config volume
2. Start the pod
3. Access ComfyUI at `http://your-runpod-url:8188`

## Configuration Files
Create these files in your `/app/config` volume:
- `models.json` - Define models to download
- `nodes.json` - Define custom nodes to install