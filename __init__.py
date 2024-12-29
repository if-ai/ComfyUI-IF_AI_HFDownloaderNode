import os
import importlib.util
import glob
import shutil
from .IFHFDownloadNode import IFHFDownload 

NODE_CLASS_MAPPINGS = {
    "IF_HFDownloadNode": IFHFDownload,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IF_HFDownloadNode": "Hugging Face Download🤗",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
