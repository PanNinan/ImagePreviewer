# ImagePreviewer - 本地图片预览器

[![CI](https://github.com/PanNinan/ImagePreviewer/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![Build & Release](https://github.com/PanNinan/ImagePreviewer/actions/workflows/build-release.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build-release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 一个简洁高效的本地图片预览工具，支持缩略图浏览和大图预览。

![预览](screenshots/preview.png)

---

## ✨ 功能特性

- 📁 **文件夹浏览** - 选择任意文件夹，自动扫描并显示图片
- 🔍 **缩略图预览** - 左侧栏显示所有图片的缩略图，支持异步加载
- 🖼️ **大图浏览** - 点击缩略图查看大图，支持键盘左右切换
- 💾 **智能缓存** - 缩略图自动缓存到本地，下次打开秒速加载
- 🎯 **格式支持** - JPG、JPEG、PNG、BMP、WebP
- ⌨️ **快捷键支持** - ← → 方向键快速切换图片
- 🧹 **缓存管理** - 一键清除缩略图缓存

---

## 📥 下载与安装

### 方式一：直接下载可执行文件（推荐）

访问 [Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases) 页面，下载最新版本的 `ImagePreviewer.exe`：

| 版本 | 说明 |
|------|------|
| `ImagePreviewer.exe` | 单文件便携版，无需安装 Python |

下载后双击即可运行，无需额外配置。

### 方式二：从源码运行

需要 Python 3.8+

```bash
# 克隆仓库
git clone https://github.com/PanNinan/ImagePreviewer.git
cd ImagePreviewer

# 创建虚拟环境
python -m venv .venv

# 激活环境（Windows）
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

---

## 🚀 使用方法

1. **启动程序** - 双击 `ImagePreviewer.exe` 或运行 `python main.py`
2. **选择文件夹** - 点击"选择文件夹"按钮，选择包含图片的目录
3. **浏览图片** - 点击左侧缩略图查看大图，或使用 ← → 方向键切换
4. **清除缓存** - 菜单栏「工具」→「清除缩略图缓存」

### 缩略图缓存位置

- **Windows**: `%USERPROFILE%\.image_previewer_cache`
- **macOS/Linux**: `~/.image_previewer_cache`

---

## 🏗️ 项目架构

```
ImagePreviewer/
├── main.py              # 主程序入口，GUI 界面实现
├── thumbnail_cache.py   # 缩略图生成与缓存管理
├── utils.py             # 工具函数（图片路径扫描等）
├── favicon.ico          # 程序图标
├── requirements.txt     # Python 依赖
└── .github/
    └── workflows/       # GitHub Actions CI/CD
```

### 技术栈

| 组件 | 用途 |
|------|------|
| PyQt6 | GUI 框架 |
| Pillow (PIL) | 图像处理与缩略图生成 |
| Python 3.8+ | 运行环境 |
| PyInstaller | 打包为可执行文件 |

---

## 🔧 开发构建

### 打包为单文件 EXE

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（单文件）
pyinstaller --onefile --windowed --name="ImagePreviewer" --icon="favicon.ico" main.py

# 打包（单目录，启动更快）
pyinstaller --onedir --windowed --name="ImagePreviewer" --icon="favicon.ico" main.py
```

打包完成后，可执行文件位于 `dist/ImagePreviewer.exe`。

---

## 📝 版本发布

本项目使用 [语义化版本](https://semver.org/lang/zh-CN/)（SemVer）：

```bash
# 1. 提交更改
git add .
git commit -m "feat: 新增某某功能"
git push origin main

# 2. 打标签
git tag v1.0.0
git push origin v1.0.0
```

推送标签后，GitHub Actions 会自动构建并发布 Release。

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

[MIT License](LICENSE) © 2026 ninan

---

## 🐛 已知问题

1. **大图片加载较慢** - 首次打开大图较多的文件夹时，缩略图生成需要一些时间
2. **WebP 动图** - 不支持 WebP 动画，仅显示第一帧

---

> 如果这个项目对你有帮助，请给个 ⭐️ 支持一下！