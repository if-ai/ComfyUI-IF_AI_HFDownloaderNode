# IFHFDownloadNode.py
import os
import math
import re
from huggingface_hub import hf_hub_download, snapshot_download, HfApi
from server import PromptServer
from aiohttp import web
import asyncio
from comfy.utils import ProgressBar
from dotenv import load_dotenv
from tqdm import tqdm

class ComfyProgress:
    def __init__(self, total):
        self.progress = ProgressBar(total)
        self.total_size = total
        
    def update(self, n=1):
        self.progress.update(n)
        current = self.progress.current
        size_info = f"{self.format_bytes(current)}/{self.format_bytes(self.total_size)}"
        PromptServer.instance.send_sync("progress", {
            "value": current,
            "max": self.total_size,
            "text": f"Downloading: {size_info}"
        })

    @staticmethod
    def format_bytes(size):
        if size <= 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size, 1024)))
        p = math.pow(1024, i)
        s = round(size / p, 2)
        return f"{s} {size_name[i]}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class SnapshotProgress(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_update = 0
        self.current_file = ""
        self.downloaded_size = 0
        self.total_size = 0

    def update(self, n=1):
        super().update(n)
        current_progress = self.n / self.total if self.total else 0
        
        # Only update UI when progress changes significantly or completes
        if current_progress - self.last_update > 0.01 or current_progress >= 1:
            self.last_update = current_progress
            
            # Format the progress message
            if hasattr(self, 'desc') and self.desc:
                status = f"{self.desc}: "
            else:
                status = ""
                
            status += f"File {self.n}/{self.total}"
            
            if hasattr(self, 'current_file') and self.current_file:
                status += f" ({self.current_file})"
                
            PromptServer.instance.send_sync("progress", {
                "value": current_progress,
                "max": 1,
                "text": status
            })

    def set_current_file(self, filename):
        self.current_file = filename
        self.refresh()

    def set_file_progress(self, downloaded, total):
        self.downloaded_size = downloaded
        self.total_size = total
        self.refresh()

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
                "comfy_paths": (["none", "animatediff_models", "animatediff_motion_lora", "animatediff_video_formats", "blip", "checkpoints", "clip", "clip_vision", "CogVideo", "configs", "controlnet", "diffusers", "diffusion_models", "embeddings", "gligen", "hypernetworks", "insightface", "Joy_caption", "layerstyle", "liveportrait", "LLM", "loras", "photomaker", "style_models", "unet", "upscale_models", "vae", "vae_approx", "xlabs"], {"default": "none"}),
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

        with ComfyProgress(len(files)) as pbar:
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
        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=repo_download_folder,
                token=hf_token,
                max_workers=1,
                tqdm_class=SnapshotProgress
            )
            
            # Clean up excluded files after download
            for root, dirs, files in os.walk(repo_download_folder):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), repo_download_folder)
                    if file_path in exclude_list:
                        os.remove(os.path.join(root, file))
                        
            self.output = f"Downloaded repo: {repo_id} to {repo_download_folder}"
        except Exception as e:
            self.output = f"Error downloading repo: {str(e)}"
            print(f"Download error: {str(e)}")

    def download_files_sync(self, repo_id, file_paths, repo_download_folder, hf_token):
        downloaded_files = []
        file_paths_list = [f.strip() for f in file_paths.split(",") if f.strip()]
        total_files = len(file_paths_list)
        
        with ComfyProgress(total_files) as pbar:
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