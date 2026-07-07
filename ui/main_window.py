import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QLabel,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from core.task import ConvertTask, TaskQueue, TaskState
from ui.file_panel import FilePanel
from ui.format_panel import FormatPanel
from ui.progress_panel import ProgressPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EagleConvter — 视频格式转换")
        self.setMinimumSize(900, 600)
        self.resize(1024, 720)
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "app.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("EagleConvter")
        title.setObjectName("appTitle")
        subtitle = QLabel("视频格式转换-https://www.eagleclouds.com")
        subtitle.setObjectName("appVersion")
        title_row.addWidget(title)
        title_row.addWidget(subtitle)
        title_row.addStretch()
        root.addLayout(title_row)

        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(12)

        self.file_panel = FilePanel()
        left_layout.addWidget(self.file_panel, 2)

        self.format_panel = FormatPanel()
        left_layout.addWidget(self.format_panel, 1)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("开始转换")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self._start_convert)
        btn_row.addStretch()
        btn_row.addWidget(self.start_btn)
        left_layout.addLayout(btn_row)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        self.progress_panel = ProgressPanel()
        right_layout.addWidget(self.progress_panel)
        splitter.addWidget(right_widget)

        splitter.setSizes([500, 400])
        root.addWidget(splitter, 1)

        self.status_label = QLabel("就绪")
        self.status_label.setObjectName("statusBar")
        root.addWidget(self.status_label)

        self._queue = TaskQueue(max_parallel=1)
        self._queue.on_change(self._on_queue_change)

        self.file_panel.files_changed.connect(self._on_files_changed)
        self.progress_panel.btn_clear.clicked.connect(self._clear_done)
        self.progress_panel.btn_cancel_all.clicked.connect(self._cancel_all)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._timer.start(100)

    def _on_files_changed(self, paths):
        self.status_label.setText(f"{len(paths)} 个文件已添加")
        self._update_start_btn()

    def _update_start_btn(self):
        self.start_btn.setEnabled(
            len(self.file_panel.paths) > 0 and not self._queue.has_running
        )

    def _start_convert(self):
        paths = self.file_panel.paths
        if not paths:
            return

        base_opts = self.format_panel.get_options()
        ext = base_opts.pop("ext", ".mp4")

        tasks = []
        for p in paths:
            base = os.path.splitext(os.path.basename(p))[0]
            out_path = os.path.join(os.getcwd(), f"{base}_converted{ext}")
            task = ConvertTask(p, out_path, opts=dict(base_opts))
            tasks.append(task)

        for t in tasks:
            self.progress_panel.add_task(t)

        self._queue.add_list(tasks)
        self._queue.tick()
        self._update_start_btn()
        self.status_label.setText(f"开始转换 {len(tasks)} 个文件 → 保存至当前目录")

    def _on_timer(self):
        self._queue.poll_completed()
        for t in self._queue.tasks:
            self.progress_panel.update_task(t)

    def _on_queue_change(self):
        self._update_start_btn()
        running = [t for t in self._queue.tasks if t.state == TaskState.RUNNING]
        pending = [t for t in self._queue.tasks if t.state == TaskState.PENDING]
        done = [t for t in self._queue.tasks if t.state == TaskState.DONE]
        failed = [t for t in self._queue.tasks if t.state == TaskState.FAILED]

        parts = []
        if running:
            parts.append(f"转换中: {len(running)}")
        if pending:
            parts.append(f"等待: {len(pending)}")
        if done:
            parts.append(f"完成: {len(done)}")
        if failed:
            parts.append(f"失败: {len(failed)}")
        self.status_label.setText("  |  ".join(parts) if parts else "就绪")

    def _clear_done(self):
        self._queue.clear_done()
        self.progress_panel.clear_done()

    def _cancel_all(self):
        self._queue.cancel_all()
        self.progress_panel.clear_all()
        self.status_label.setText("已取消全部任务")
