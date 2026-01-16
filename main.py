# main.py
import os
import shutil
import sys
import threading

from PyQt6.QtCore import Qt, QSize, QSettings, Q_ARG, QMetaObject, pyqtSlot
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem,
    QLabel, QMessageBox, QStatusBar
)

from thumbnail_cache import CACHE_DIR, generate_thumbnail, get_cache_path
from utils import get_image_paths


class ImagePreviewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("本地图片预览器")
        self.resize(1200, 750)
        self.image_paths = []
        self.current_index = -1

        # 设置配置存储
        self.settings = QSettings("ImagePreviewer", "App")

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # 左侧：缩略图列表
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setIconSize(QSize(180, 180))
        self.thumbnail_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumbnail_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumbnail_list.setSpacing(8)
        self.thumbnail_list.setMovement(QListWidget.Movement.Static)
        self.thumbnail_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.thumbnail_list.itemClicked.connect(self.on_thumbnail_clicked)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        num_columns = 1
        fixed_width = 190 * num_columns + 8 * 2 + 20
        self.thumbnail_list.setFixedWidth(fixed_width)
        layout.addWidget(self.thumbnail_list, 0)

        # 右侧：大图预览 + 控制按钮
        right_layout = QVBoxLayout()

        self.image_label = QLabel("请选择图片文件夹")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: #f8f8f8; border: 1px solid #ddd; }")
        self.image_label.setMinimumSize(400, 400)
        right_layout.addWidget(self.image_label, 1)

        # 控制按钮
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀ 上一张")
        self.next_btn = QPushButton("下一张 ▶")
        self.select_btn = QPushButton("选择文件夹")

        self.prev_btn.clicked.connect(self.show_prev)
        self.next_btn.clicked.connect(self.show_next)
        self.select_btn.clicked.connect(self.select_folder)

        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.next_btn)
        right_layout.addLayout(btn_layout)

        layout.addLayout(right_layout, 2)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 尝试自动加载上次路径
        last_folder = self.settings.value("last_folder", "")
        if last_folder and os.path.isdir(last_folder):
            self.load_images(last_folder)
        else:
            self.select_btn.setEnabled(True)

        menubar = self.menuBar()
        tool_menu = menubar.addMenu("工具(&T)")

        clear_cache_action = tool_menu.addAction("清除缩略图缓存(&C)")
        clear_cache_action.triggered.connect(self.clear_thumbnail_cache)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            self.settings.setValue("last_folder", folder)
            self.load_images(folder)

    def load_images(self, folder):
        self.thumbnail_list.clear()
        self.image_paths = get_image_paths(folder)
        if not self.image_paths:
            QMessageBox.information(self, "提示", "该文件夹中未找到支持的图片。")
            return

        count = len(self.image_paths)
        self.status_bar.showMessage(f"共找到 {count} 张图片")

        # 预检：是否所有缩略图都已缓存？
        all_cached = True
        for path in self.image_paths:
            cache_path = get_cache_path(path)
            if not os.path.exists(cache_path):
                all_cached = False
                break

        if all_cached:
            # 直接同步加载（无需线程）
            for i, path in enumerate(self.image_paths):
                thumb_path = get_cache_path(path)
                item = QListWidgetItem()
                item.setIcon(QIcon(thumb_path))
                item.setToolTip(os.path.basename(path))
                item.setSizeHint(QSize(190, 190))
                self.thumbnail_list.addItem(item)
            self.status_bar.showMessage(f"就绪：共 {count} 张图片（缓存）")
            self.select_btn.setEnabled(True)
        else:
            # 走异步线程流程
            self.status_bar.showMessage(f"共找到 {count} 张图片，正在加载缩略图...")
            for i in range(count):
                item = QListWidgetItem()
                item.setSizeHint(QSize(190, 190))
                self.thumbnail_list.addItem(item)
            threading.Thread(target=self._load_thumbnails_async, args=(folder,), daemon=True).start()

    def _load_thumbnails_async(self, folder):
        total = len(self.image_paths)
        for i, path in enumerate(self.image_paths):
            thumb_path = generate_thumbnail(path)
            if thumb_path:
                QMetaObject.invokeMethod(
                    self,
                    "_update_thumbnail_item",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(int, i),
                    Q_ARG(str, thumb_path)
                )
            # 微小延迟避免阻塞
            if i % 50 == 0:
                self.status_bar.showMessage(f"已处理 {i}/{len(self.image_paths)} 张...")

        # 全部完成后通知
        QMetaObject.invokeMethod(
            self,
            "_on_thumbnails_loaded",
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(int, total)
        )

    @pyqtSlot(int, str)
    def _update_thumbnail_item(self, index: int, thumb_path: str):
        if 0 <= index < self.thumbnail_list.count():
            item = self.thumbnail_list.item(index)
            if item:
                item.setIcon(QIcon(thumb_path))
                # 不设置文字！用 tooltip 显示文件名
                item.setToolTip(os.path.basename(self.image_paths[index]))

    @pyqtSlot(int)
    def _on_thumbnails_loaded(self, total: int):
        self.status_bar.showMessage(f"缩略图加载完成，共 {total} 张图片")
        self.select_btn.setEnabled(True)  # 允许再次选择文件夹

    def on_thumbnail_clicked(self, item):
        row = self.thumbnail_list.row(item)
        self.show_image_at(row)

    def show_image_at(self, index: int):
        if not (0 <= index < len(self.image_paths)):
            return
        self.current_index = index
        full_path = self.image_paths[index]
        pixmap = QPixmap(full_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.status_bar.showMessage(f"{index + 1} / {len(self.image_paths)} — {os.path.basename(full_path)}")
        else:
            self.image_label.setText("无法加载图片")

        # 更新按钮状态
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.image_paths) - 1)

    def show_prev(self):
        if self.current_index > 0:
            self.show_image_at(self.current_index - 1)
            self.thumbnail_list.setCurrentRow(self.current_index)

    def show_next(self):
        if self.current_index < len(self.image_paths) - 1:
            self.show_image_at(self.current_index + 1)
            self.thumbnail_list.setCurrentRow(self.current_index)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.show_prev()
        elif event.key() == Qt.Key.Key_Right:
            self.show_next()
        else:
            super().keyPressEvent(event)

    def clear_thumbnail_cache(self):
        if not os.path.exists(CACHE_DIR):
            QMessageBox.information(self, "提示", "暂无缩略图缓存。")
            return

        reply = QMessageBox.question(
            self,
            "确认清除",
            f"将删除所有本地缩略图缓存（约 {self.get_cache_size_human()}），\n"
            "原图不会被删除。\n\n是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(CACHE_DIR)
                os.makedirs(CACHE_DIR, exist_ok=True)  # 重建空目录
                self.status_bar.showMessage("缩略图缓存已清除。", 3000)
                # 可选：重新加载当前文件夹（让缩略图重新生成）
                last_folder = self.settings.value("last_folder", "")
                if last_folder and os.path.isdir(last_folder):
                    self.load_images(last_folder)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清除缓存失败：{e}")

    def get_cache_size_human(self):
        """返回缓存目录大小的人类可读格式"""
        if not os.path.exists(CACHE_DIR):
            return "0 B"
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(CACHE_DIR):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        # 转换为 KB/MB
        for unit in ['B', 'KB', 'MB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} GB"


def main():
    app = QApplication(sys.argv)
    window = ImagePreviewer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    # python -m PyInstaller --onefile --windowed --name="ImagePreviewer" --icon="favicon.ico" --clean main.py
    # python -m PyInstaller  --onedir --windowed --name="ImagePreviewer" --icon="favicon.ico" --clean main.py
