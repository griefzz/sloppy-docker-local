#!/usr/bin/env python3
import json
import os
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download, login
from tqdm import tqdm


def download_model(model_config):
    """Download a single model file using hf-transfer for maximum speed"""
    repo_id = model_config["repo_id"]
    filename = model_config["filename"]  # Required field now
    subfolder = model_config.get("subfolder", "")
    model_type = model_config.get("type", "checkpoints")
    rename_to = model_config.get("rename_to")  # Optional rename

    # Determine target directory based on model type
    base_path = Path("/app/ComfyUI/models")
    if model_type == "checkpoints":
        target_dir = base_path / "checkpoints"
    elif model_type == "vae":
        target_dir = base_path / "vae"
    elif model_type == "loras":
        target_dir = base_path / "loras"
    elif model_type == "controlnet":
        target_dir = base_path / "controlnet"
    elif model_type == "embeddings":
        target_dir = base_path / "embeddings"
    else:
        target_dir = base_path / model_type

    target_dir.mkdir(parents=True, exist_ok=True)

    # Determine final file path and check if it already exists
    final_filename = rename_to if rename_to else filename
    final_path = target_dir / final_filename
    
    if final_path.exists():
        print(f"⏭️ Model {final_filename} already exists, skipping download")
        return True

    print(f"📥 Downloading {filename} from {repo_id}")

    try:
        if subfolder:
            # Download to cache first to avoid subfolder structure
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=subfolder,
                local_dir=target_dir,
            )

            # Determine final filename
            final_filename = rename_to if rename_to else filename
            final_path = target_dir / final_filename

            # Move file to target location (avoiding subfolder structure)
            shutil.move(downloaded_path, final_path)
        else:
            # Download directly to target directory
            final_filename = rename_to if rename_to else filename
            downloaded_path = hf_hub_download(
                repo_id=repo_id, filename=filename, local_dir=target_dir
            )

            # Handle renaming if needed
            if rename_to and Path(downloaded_path).name != final_filename:
                final_path = target_dir / final_filename
                Path(downloaded_path).rename(final_path)

        if rename_to:
            print(f"✅ Downloaded and renamed {filename} → {rename_to}")
        else:
            print(f"✅ Downloaded {filename}")

        return True

    except Exception as e:
        print(f"❌ Failed to download {filename}: {str(e)}")
        return False


def main():
    # Login to HuggingFace if token is provided
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print("🔐 Logging in to HuggingFace...")
        try:
            login(token=hf_token)
            print("✅ Successfully authenticated with HuggingFace")
        except Exception as e:
            print(f"⚠️ Failed to authenticate with HuggingFace: {str(e)}")
    else:
        print("ℹ️ No HF_TOKEN provided - using anonymous access")

    config_path = "/app/config/models.json"

    if not os.path.exists(config_path):
        print("No models.json found, skipping model downloads")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    models = config.get("models", [])

    if not models:
        print("No models specified in config")
        return

    print(f"🚀 Starting download of {len(models)} models...")

    # Download models sequentially with progress bar
    failed_downloads = []
    with tqdm(total=len(models), desc="Downloading models", unit="file") as pbar:
        for i, model in enumerate(models, 1):
            filename = model.get("filename", "unknown")
            pbar.set_description(f"📥 {filename}")

            success = download_model(model)
            if not success:
                failed_downloads.append(filename)

            pbar.update(1)
            pbar.set_postfix({"Failed": len(failed_downloads)})

    # Summary
    successful = len(models) - len(failed_downloads)
    print(f"🎉 Download complete! {successful}/{len(models)} successful")

    if failed_downloads:
        print(f"⚠️ Failed downloads: {', '.join(failed_downloads)}")


if __name__ == "__main__":
    main()
