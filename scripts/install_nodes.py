#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

def install_node(node_config):
    """Install a custom node"""
    node_type = node_config.get("type", "git")
    name = node_config.get("name", "Unknown")
    
    try:
        if node_type == "git":
            repo_url = node_config["repo_url"]
            custom_nodes_dir = Path("/app/ComfyUI/custom_nodes")
            custom_nodes_dir.mkdir(exist_ok=True)
            
            # Get the expected directory name
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            node_dir = custom_nodes_dir / repo_name
            
            # Check if node already exists
            if node_dir.exists():
                print(f"⏭️ Custom node {name} already exists, skipping installation")
                return True
            
            print(f"🔧 Installing custom node: {name}")
            
            # Clone the repository
            result = subprocess.run([
                "git", "clone", repo_url
            ], cwd=custom_nodes_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ Failed to clone {repo_url}: {result.stderr}")
                return False
            
            # Install requirements if they exist
            requirements_file = node_dir / "requirements.txt"
            if requirements_file.exists():
                print(f"📦 Installing requirements for {name}")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], capture_output=True, text=True, timeout=600)
                
                if result.returncode != 0:
                    print(f"⚠️ Warning: Failed to install requirements for {name}: {result.stderr}")
        
        elif node_type == "pip":
            package_name = node_config["package_name"]
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package_name
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ Failed to install pip package {package_name}: {result.stderr}")
                return False
                
        else:
            print(f"❌ Unknown node type: {node_type}")
            return False
            
        print(f"✅ Successfully installed {name}")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout installing {name}")
        return False
    except Exception as e:
        print(f"❌ Error installing {name}: {str(e)}")
        return False

def main():
    config_path = "/app/config/nodes.json"
    
    if not os.path.exists(config_path):
        print("No nodes.json found, skipping custom node installation")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    nodes = config.get("nodes", [])
    
    if not nodes:
        print("No custom nodes specified in config")
        return
    
    print(f"🚀 Installing {len(nodes)} custom nodes...")
    
    success_count = 0
    for node in nodes:
        if install_node(node):
            success_count += 1
    
    print(f"🎉 Custom node installation completed! {success_count}/{len(nodes)} nodes installed successfully")

if __name__ == "__main__":
    main()