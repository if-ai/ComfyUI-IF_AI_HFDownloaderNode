# IFHFDownloadNode.py
"""
Hugging Face Download Node

Copyright 2023 impactframes

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
import math
import re
from huggingface_hub import hf_hub_download, snapshot_download, HfApi
from server import PromptServer
from aiohttp import web
import asyncio
from tqdm import tqdm
from dotenv import load_dotenv

class CustomProgress(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_update = 0
        self.total_size = kwargs.get('total', 0)

    def update(self, n=1):
        super().update(n)
        current_progress = self.n / self.total if self.total else 0
        if current_progress - self.last_update > 0.01 or self.n == self.total:
            size_info = f"{self.format_bytes(self.n)}/{self.format_bytes(self.total_size)}"
            PromptServer.instance.send_sync("progress", {
                "value": current_progress,
                "max": 1,
                "text": f"Downloading: {size_info}"
            })
            self.last_update = current_progress

    @staticmethod
    def format_bytes(size):
        if size <= 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return f"{s} {size_name[i]}"

class IFHFDownload:
    def __init__(self):
        self.output = None
        self.comfy_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.download_dir = os.path.join(self.comfy_dir, "models")
        load_dotenv(os.path.join(self.comfy_dir, '.env'))

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": ("STRING", {"multiline": False}),
                "file_paths": ("STRING", {"multiline": True, "default": "comma-separated list of files or leave empty for all"}),
                "folder_path": ("STRING", {"multiline": False, "default": "/path/to/download/folder"}),
                "comfy_paths": (["none", "LLM", "checkpoints", "clip", "clip_vision", "controlnet", "diffusers", "embeddings", "loras", "upscale_models", "vae"], {"default": "none"}),
                "exclude_files": ("STRING", {"multiline": True, "default": "comma-separated list to exclude"}),
            },
            "optional": {
                "mode": ("BOOLEAN", {"default": False, "label_on": "All Repo/Space", "label_off": "Individual Files"}),
                "provided_token": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "download_hf"
    CATEGORY = "ImpactFrames💥🎞️"

    def get_hf_token(self, provided_token = None):
        if provided_token is not None and provided_token != "":
            return provided_token
        elif os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY"):
            return os.getenv("HF_TOKEN") or os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
        else:
            raise ValueError("HF_TOKEN not found. Please set it in your .env file, as an environment variable, or provide it in the node input.")

    def get_safe_folder_name(self, repo_id):
        # Extract the last part of the repo_id
        folder_name = repo_id.split('/')[-1]
        # Replace any characters that might be problematic for file systems
        safe_name = re.sub(r'[^\w\-_\. ]', '_', folder_name)
        return safe_name
    
    def download_hf(self, mode, repo_id, file_paths, comfy_paths, folder_path, exclude_files, provided_token = None):
        try:
            hf_token = self.get_hf_token(provided_token)
        except ValueError as e:
            self.output = str(e)
            return (self.output,)

        exclude_list = [f.strip() for f in exclude_files.split(",") if f.strip()]
        
        
        if folder_path and folder_path != "/path/to/download/folder" and os.path.isdir(folder_path):
            download_folder = folder_path
        elif comfy_paths != "none":
            download_folder = os.path.join(self.download_dir, comfy_paths)
        else:
            download_folder = os.path.join(self.download_dir, "IF_AI")
            print(f"Download folder: {download_folder}")
            
            
        repo_folder_name = self.get_safe_folder_name(repo_id)
        repo_download_folder = os.path.join(download_folder, repo_folder_name)
        os.makedirs(repo_download_folder, exist_ok=True)

        if '/' in repo_id:
            parts = repo_id.split('/')
            if len(parts) > 2:
                space_id = '/'.join(parts[:2])
                subpath = '/'.join(parts[2:])
                self.download_from_space(space_id, subpath, file_paths, repo_download_folder, exclude_list, hf_token, mode)
            else:
                self.download_repo_or_files(repo_id, file_paths, repo_download_folder, exclude_list, hf_token, mode)
        else:
            self.download_repo_or_files(repo_id, file_paths, repo_download_folder, exclude_list, hf_token, mode)

        return (self.output,)

    def download_from_space(self, space_id, subpath, file_paths, repo_download_folder, exclude_list, hf_token, download_all):
        
        api = HfApi(token=hf_token)

        if download_all:
            all_files = api.list_repo_files(repo_id=space_id, repo_type="space")
            files = [f for f in all_files if f.startswith(subpath)]
        else:
            files = [os.path.join(subpath, file.strip()) for file in file_paths.split(',') if file.strip()]

        with CustomProgress(total=len(files), desc="Downloading files from space") as pbar:
            for file in files:
                if file not in exclude_list:
                    try:
                        hf_hub_download(
                            repo_id=space_id,
                            filename=file,
                            repo_type="space",
                            local_dir=repo_download_folder,
                            token=hf_token
                        )
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error downloading {file}: {str(e)}")

        self.output = f"Downloaded files from Space: {space_id}/{subpath} to {repo_download_folder}"

    def download_repo_or_files(self, repo_id, file_paths, repo_download_folder, exclude_list, hf_token, download_all):
        if download_all:
            self.download_repo_sync(repo_id, repo_download_folder, exclude_list, hf_token)
        else:
            self.download_files_sync(repo_id, file_paths, repo_download_folder, hf_token)

    def download_repo_sync(self, repo_id, repo_download_folder, exclude_list, hf_token):
        snapshot_download(
            repo_id=repo_id,
            local_dir=repo_download_folder,
            token=hf_token,
            max_workers=1,
            tqdm_class=CustomProgress
        )
        
        for root, dirs, files in os.walk(repo_download_folder):
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), repo_download_folder)
                if file_path in exclude_list:
                    os.remove(os.path.join(root, file))
        self.output = f"Downloaded repo: {repo_id} to {repo_download_folder}"

    def download_files_sync(self, repo_id, file_paths, repo_download_folder, hf_token):
        downloaded_files = []
        file_paths_list = [f.strip() for f in file_paths.split(",") if f.strip()]
        total_files = len(file_paths_list)
        
        with CustomProgress(total=total_files, desc="Downloading files") as pbar:
            for file_path in file_paths_list:
                try:
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=file_path,
                        local_dir=repo_download_folder,
                        token=hf_token
                    )
                    downloaded_files.append(file_path)
                    pbar.update(1)
                except Exception as e:
                    print(f"Error downloading {file_path}: {str(e)}")
        
        self.output = f"Downloaded files: {', '.join(downloaded_files)} from {repo_id} to {repo_download_folder}"

NODE_CLASS_MAPPINGS = {"IF_HFDownload": IFHFDownload}
NODE_DISPLAY_NAME_MAPPINGS = {"IF_HFDownload": "Hugging Face Download🤗"}