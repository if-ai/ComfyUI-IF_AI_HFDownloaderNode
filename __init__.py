import os
import importlib.util
import glob
import shutil
from .IFHFDownloadNode import IFHFDownload 
from .IFDisplayTextNode import IFDisplayText

NODE_CLASS_MAPPINGS = {
    "IF_HFDownloadNode": IFHFDownload,
    "IF_DisplayTextNode": IFDisplayText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IF_HFDownloadNode": "Hugging Face Download🤗",
    "IF_DisplayTextNode": "IF Display Text📟",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
