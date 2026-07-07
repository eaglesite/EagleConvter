import os
import subprocess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QScrollArea, QFileDialog, QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from core.task import TaskState


class TaskItemWidget(QWidget):
    save_as_requested = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.task = task
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        name_row = QHBoxLayout()
        self.name_label = QLabel(task.input_name)
        self.name_label.setObjectName("taskName")
        self.state_label = QLabel("等待中")
        self.state_label.setObjectName("taskState")
        name_row.addWidget(self.name_label, 1)
        name_row.addWidget(self.state_label)
        layout.addLayout(name_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        info_row = QHBoxLayout()
        self.info_label = QLabel("")
        self.info_label.setObjectName("taskInfo")
        self.size_label = QLabel("")
        self.size_label.setObjectName("taskSize")
        info_row.addWidget(self.info_label, 1)
        info_row.addWidget(self.size_label)
        layout.addLayout(info_row)

    def _show_context_menu(self, pos):
        menu = QMenu()
        save_as = QAction("另存为...", self)
        save_as.triggered.connect(self._save_as)
        menu.addAction(save_as)
        if self.task.state == TaskState.DONE and self.task.file_size:
            open_folder = QAction("打开输出文件夹", self)
            open_folder.triggered.connect(self._open_folder)
            menu.addAction(open_folder)
        menu.exec(self.mapToGlobal(pos))

    def _save_as(self):
        ext = os.path.splitext(self.task.output_path)[1]
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", self.task.output_path,
            f"媒体文件 (*{ext});;所有文件 (*.*)"
        )
        if path:
            self.task.output_path = path
            self.save_as_requested.emit(self.task)

    def _open_folder(self):
        folder = os.path.dirname(self.task.output_path)
        if os.path.exists(folder):
            subprocess.Popen(["explorer", "/select,", os.path.normpath(self.task.output_path)])

    def update_state(self):
        t = self.task
        if t.state == TaskState.PENDING:
            self.state_label.setText("等待中")
            self.state_label.setStyleSheet("color: #888;")
            self.progress_bar.setValue(0)
            self.info_label.setText("")
            self.size_label.setText("")
        elif t.state == TaskState.RUNNING:
            self.state_label.setText("转换中")
            self.state_label.setStyleSheet("color: #20a53a;")
            val = round(t.progress) if t.duration > 0 else 0
            self.progress_bar.setValue(val)
            if t.duration <= 0:
                self.progress_bar.setFormat(f"帧 {t.fps:.0f}")
            pieces = []
            if t.fps:
                pieces.append(f"{t.fps:.0f}fps")
            if t.speed:
                pieces.append(f"{t.speed:.1f}x")
            elapsed = time.time() - t._start_time if t._start_time else 0
            m, s = divmod(int(elapsed), 60)
            pieces.append(f"{m:02d}:{s:02d}")
            if t.eta:
                pieces.append(f"剩余 {t.eta}")
            self.info_label.setText("  ".join(pieces))
            self.size_label.setText(os.path.basename(t.output_path))
        elif t.state == TaskState.DONE:
            self.state_label.setText("完成 ✓")
            self.state_label.setStyleSheet("color: #20a53a; font-weight: bold;")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("%p%")
            self.progress_bar.setStyleSheet("")
            size_str = self._fmt_size(t.file_size) if t.file_size else ""
            self.size_label.setText(size_str)
            dur = t.elapsed
            if dur:
                m, s = divmod(int(dur), 60)
                self.info_label.setText(f"用时 {m:02d}:{s:02d}")
            else:
                self.info_label.setText("")
        elif t.state == TaskState.FAILED:
            self.state_label.setText("失败 ✗")
            self.state_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")
            self.info_label.setText(t.error_msg or "")
            self.size_label.setText("")
        elif t.state == TaskState.CANCELLED:
            self.state_label.setText("已取消")
            self.state_label.setStyleSheet("color: #888;")
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("%p%")
            self.info_label.setText("")
            self.size_label.setText("")

    @staticmethod
    def _fmt_size(b):
        for u in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"


class ProgressPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        title = QLabel("转换进度")
        title.setObjectName("progressTitle")
        header.addWidget(title, 1)

        self.btn_clear = QPushButton("清除已完成")
        self.btn_clear.setObjectName("clearDoneBtn")
        self.btn_cancel_all = QPushButton("取消全部")
        self.btn_cancel_all.setObjectName("cancelAllBtn")
        header.addWidget(self.btn_clear)
        header.addWidget(self.btn_cancel_all)
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll, 1)

        self._task_widgets = {}

    def add_task(self, task):
        w = TaskItemWidget(task)
        w.save_as_requested.connect(self._on_save_as)
        self._task_widgets[task] = w
        self.scroll_layout.addWidget(w)

    def _on_save_as(self, task):
        pass

    def update_task(self, task):
        w = self._task_widgets.get(task)
        if w:
            w.update_state()

    def remove_task(self, task):
        w = self._task_widgets.pop(task, None)
        if w:
            self.scroll_layout.removeWidget(w)
            w.deleteLater()

    def clear_done(self):
        for task, w in list(self._task_widgets.items()):
            if task.state in (TaskState.DONE, TaskState.FAILED, TaskState.CANCELLED):
                self.scroll_layout.removeWidget(w)
                w.deleteLater()
                del self._task_widgets[task]

    def clear_all(self):
        for w in self._task_widgets.values():
            w.deleteLater()
        self._task_widgets.clear()
