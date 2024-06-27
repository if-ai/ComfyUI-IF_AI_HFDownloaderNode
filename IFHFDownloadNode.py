import os
import math
from huggingface_hub import hf_hub_download, snapshot_download, HfApi
from server import PromptServer
from aiohttp import web
import asyncio
from tqdm import tqdm

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

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": ("STRING", {"multiline": False}),
                "file_paths": ("STRING", {"multiline": True, "default": "comma-separated list of files or leave empty for all"}),
                "folder_path": ("STRING", {"multiline": False, "default": "/path/to/download/folder"}),
                "exclude_files": ("STRING", {"multiline": True, "default": "comma-separated list to exclude"}),
                "hf_token": ("STRING", {"multiline": False, "default": "your Hugging Face token"}),
            },
            "optional": {
                "mode": ("BOOLEAN", {"default": False, "label_on": "All Repo/Space", "label_off": "Individual Files"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "download_hf"
    CATEGORY = "ImpactFrames💥🎞️"

    def download_hf(self, mode, repo_id, file_paths, folder_path, exclude_files, hf_token):
        exclude_list = [f.strip() for f in exclude_files.split(",") if f.strip()]
        rename_me_folder = os.path.join(folder_path, "rename_me")
        os.makedirs(rename_me_folder, exist_ok=True)

        if '/' in repo_id:
            # This could be a space or a regular repo
            parts = repo_id.split('/')
            if len(parts) > 2:
                # This is likely a space path
                space_id = '/'.join(parts[:2])
                subpath = '/'.join(parts[2:])
                self.download_from_space(space_id, subpath, file_paths, rename_me_folder, exclude_list, hf_token, mode)
            else:
                # This is a regular repo
                self.download_repo_or_files(repo_id, file_paths, rename_me_folder, exclude_list, hf_token, mode)
        else:
            # This is a regular repo
            self.download_repo_or_files(repo_id, file_paths, rename_me_folder, exclude_list, hf_token, mode)

        return (self.output,)

    def download_from_space(self, space_id, subpath, file_paths, rename_me_folder, exclude_list, hf_token, download_all):
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
                            local_dir=rename_me_folder,
                            token=hf_token
                        )
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error downloading {file}: {str(e)}")

        self.output = f"Downloaded files from Space: {space_id}/{subpath} to {rename_me_folder}"

    def download_repo_or_files(self, repo_id, file_paths, rename_me_folder, exclude_list, hf_token, download_all):
        if download_all:
            self.download_repo_sync(repo_id, rename_me_folder, exclude_list, hf_token)
        else:
            self.download_files_sync(repo_id, file_paths, rename_me_folder, hf_token)

    def download_repo_sync(self, repo_id, rename_me_folder, exclude_list, hf_token):
        snapshot_download(
            repo_id=repo_id,
            local_dir=rename_me_folder,
            token=hf_token,
            max_workers=1,
            tqdm_class=CustomProgress
        )
        
        for root, dirs, files in os.walk(rename_me_folder):
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), rename_me_folder)
                if file_path in exclude_list:
                    os.remove(os.path.join(root, file))
        self.output = f"Downloaded repo: {repo_id} to {rename_me_folder}"

    def download_files_sync(self, repo_id, file_paths, rename_me_folder, hf_token):
        downloaded_files = []
        file_paths_list = [f.strip() for f in file_paths.split(",") if f.strip()]
        total_files = len(file_paths_list)
        
        with CustomProgress(total=total_files, desc="Downloading files") as pbar:
            for file_path in file_paths_list:
                try:
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=file_path,
                        local_dir=rename_me_folder,
                        token=hf_token
                    )
                    downloaded_files.append(file_path)
                    pbar.update(1)
                except Exception as e:
                    print(f"Error downloading {file_path}: {str(e)}")
        
        self.output = f"Downloaded files: {', '.join(downloaded_files)} from {repo_id} to {rename_me_folder}"

NODE_CLASS_MAPPINGS = {"IF_HFDownload": IFHFDownload}
NODE_DISPLAY_NAME_MAPPINGS = {"IF_HFDownload": "Hugging Face Download🤗"}