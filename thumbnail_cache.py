import os
import hashlib
import shutil

from PIL import Image
from PyQt6.QtWidgets import QMessageBox

CACHE_DIR = os.path.expanduser("～/.image_previewer_cache")
THUMB_SIZE = (180, 180)  # 固定的缩略图尺寸

def get_cache_path(image_path: str, size=(180, 180)):
    os.makedirs(CACHE_DIR, exist_ok=True)
    key = f"{image_path}_{size[0]}x{size[1]}"
    hash_key = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{hash_key}.jpg")

def generate_thumbnail(image_path: str, size=(180, 180)):
    cache_path = get_cache_path(image_path, size)
    if os.path.exists(cache_path):
        return cache_path
    try:
        with Image.open(image_path) as img:
            # 计算缩放比例
            ratio = min(THUMB_SIZE[0] / img.width, THUMB_SIZE[1] / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))

            # 缩放图片
            img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 创建白色背景的新图像
            thumb = Image.new("RGB", THUMB_SIZE, (255, 255, 255))

            # 计算并应用偏移量，使图片居中
            offset = ((THUMB_SIZE[0] - new_size[0]) // 2, (THUMB_SIZE[1] - new_size[1]) // 2)
            thumb.paste(img, offset)

            # 保存缩略图
            thumb.save(cache_path, "JPEG", quality=85)

            # img.thumbnail(size, Image.Resampling.LANCZOS)
            # if img.mode in ("RGBA", "P"):
            #     img = img.convert("RGB")
            # img.save(cache_path, "JPEG", quality=85)
        return cache_path
    except Exception as e:
        print(f"Thumbnail error: {e}")
        return None
