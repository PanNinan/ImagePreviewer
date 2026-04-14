# GitHub Actions 配置说明

本项目通过 GitHub Actions 实现自动化 CI/CD 流程。

---

## 工作流文件概览

| 文件 | 触发条件 | 作用 |
|------|----------|------|
| `.github/workflows/ci.yml` | push / PR | 代码语法检查、Flake8 风格检查、Pylint 静态分析 |
| `.github/workflows/build-release.yml` | 推送 `v*.*.*` tag 或手动触发 | PyInstaller 打包 Windows EXE，创建 GitHub Release |

---

## 权限配置

**重要**：`build-release.yml` 已内置 `permissions: contents: write`，用于创建 Release。

如果仍遇到 403 权限错误，请检查仓库设置：

1. 进入仓库 → **Settings** → **Actions** → **General**
2. 滚动到 **"Workflow permissions"**
3. 选择 **"Read and write permissions"**
4. 点击 **Save**

---

## 发布新版本的步骤

```bash
# 1. 确认代码已提交并推送
git add .
git commit -m "feat: 新增某某功能"
git push origin main

# 2. 打标签（遵循语义化版本）
git tag v1.0.0
git push origin v1.0.0
```

推送 tag 后，GitHub Actions 将自动：
1. 在 Windows 环境安装 Python 3.11 和依赖
2. 使用 PyInstaller 打包为单文件 EXE
3. 在 GitHub Releases 页面发布，附带 EXE 文件

---

## 手动触发构建

在 GitHub 仓库页面：
1. 点击 **Actions** 标签
2. 选择 **Build & Release** 工作流
3. 点击 **Run workflow** 按钮
4. 可选择输入版本号（如 `v1.0.0-beta`），留空则使用 git tag

---

## CI 检查说明

### 语法检查（py_compile）

验证所有 `.py` 文件无语法错误，失败会阻断整个 CI。

### Flake8 风格检查

代码风格不规范会报错（允许行长 120 字符）。

### Pylint 静态分析

评分低于阈值时仅警告，不阻断 CI（`continue-on-error: true`）。

---

## 打包产物说明

每次 tag 触发的构建会在 GitHub Actions Artifacts 中保留 30 天，Release 页面永久保存：

```
ImagePreviewer.exe   # Windows 单文件可执行程序（无需安装 Python）
```

---

## 常见问题

### Q: Release 创建失败，提示 403
A: 检查仓库的 Workflow permissions 是否设置为 "Read and write permissions"。

### Q: 打包后的 EXE 无法运行
A: 检查 `main.py` 中是否有硬编码的本地路径，或依赖项是否都在 `requirements.txt` 中声明。

### Q: 如何测试 CI 而不发布 Release
A: 直接 push 到 main 分支会触发 CI 检查，但不会触发 Release。
