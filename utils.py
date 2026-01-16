# utils.py
import os
from pathlib import Path
from thumbnail_cache import CACHE_DIR  # 确保你已定义这个常量

SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

def get_image_paths(folder_path: str):
    """递归获取文件夹下所有支持的图片路径"""
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                image_paths.append(os.path.join(root, file))
    return sorted(image_paths)