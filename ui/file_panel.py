import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QLabel,
    QAbstractItemView, QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QAction
from core.ffmpeg import probe_info


class FileItemWidget(QWidget):
    remove_clicked = Signal(object)

    def __init__(self, path):
        super().__init__()
        self.path = path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        info = QVBoxLayout()
        info.setSpacing(2)
        name = os.path.basename(path)
        self.name_label = QLabel(name)
        self.name_label.setObjectName("fileName")
        self.detail_label = QLabel("")
        self.detail_label.setObjectName("fileInfo")
        info.addWidget(self.name_label)
        info.addWidget(self.detail_label)
        layout.addLayout(info, 1)

        self.size_label = QLabel("")
        self.size_label.setObjectName("fileSize")
        self.size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.size_label)

        btn_remove = QPushButton("✕")
        btn_remove.setFixedSize(22, 22)
        btn_remove.setObjectName("removeBtn")
        btn_remove.clicked.connect(lambda: self.remove_clicked.emit(self))
        layout.addWidget(btn_remove)

        self._probe_info()

    def _fmt_size(self, b):
        for u in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {u}"
            b /= 1024
        return f"{b:.1f} TB"

    def _fmt_duration(self, secs):
        if secs <= 0:
            return ""
        m, s = divmod(int(secs), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h{m:02d}m{s:02d}s"
        return f"{m:02d}:{s:02d}"

    def _probe_info(self):
        ext = os.path.splitext(self.path)[1].lower()
        video_exts = {".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv",
                      ".webm", ".m4v", ".ts", ".mts", ".3gp", ".ogv",
                      ".mpg", ".mpeg", ".vob", ".mxf"}
        if ext not in video_exts:
            try:
                fsize = os.path.getsize(self.path)
                self.size_label.setText(self._fmt_size(fsize))
                self.detail_label.setText("音频文件")
            except OSError:
                pass
            return

        try:
            fsize = os.path.getsize(self.path)
            self.size_label.setText(self._fmt_size(fsize))
        except OSError:
            pass

        info = probe_info(self.path)
        if not info:
            return

        streams = info.get("streams", [])
        fmt = info.get("format", {})
        parts = []

        video_streams = [s for s in streams if s.get("codec_type") == "video"]
        audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

        if video_streams:
            vs = video_streams[0]
            codec = vs.get("codec_name", "").upper()
            w = vs.get("width", 0)
            h = vs.get("height", 0)
            res = f"{w}x{h}" if w and h else ""
            fr = vs.get("r_frame_rate", "")
            fps_str = ""
            if fr and "/" in fr:
                try:
                    n, d = map(int, fr.split("/"))
                    fps_str = f"{n/d:.0f}fps" if d else ""
                except ValueError:
                    pass
            parts.append(f"{codec}")
            if res:
                parts.append(res)
            if fps_str:
                parts.append(fps_str)

        if audio_streams:
            ac = audio_streams[0].get("codec_name", "").upper()
            parts.append(f"音频:{ac}")

        dur = fmt.get("duration", "0")
        try:
            dur_secs = float(dur)
            dur_str = self._fmt_duration(dur_secs)
            if dur_str:
                parts.append(dur_str)
        except ValueError:
            pass

        self.detail_label.setText("  |  ".join(parts) if parts else "")

    def update_size(self):
        try:
            fsize = os.path.getsize(self.path)
            self.size_label.setText(self._fmt_size(fsize))
        except OSError:
            pass


class FilePanel(QWidget):
    files_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        btn_add = QPushButton("添加文件")
        btn_add.setObjectName("addBtn")
        btn_add.clicked.connect(self._browse)
        btn_clear = QPushButton("清空列表")
        btn_clear.setObjectName("clearBtn")
        btn_clear.clicked.connect(self._clear)
        header.addWidget(btn_add)
        header.addWidget(btn_clear)
        header.addStretch()
        layout.addLayout(header)

        drop_label = QLabel("拖拽媒体文件到此处，或点击「添加文件」")
        drop_label.setObjectName("dropHint")
        drop_label.setAlignment(Qt.AlignCenter)
        drop_label.setMinimumHeight(60)
        layout.addWidget(drop_label)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget, 1)

        self._paths = []

    def _browse(self):
        from core.formats import INPUT_FORMATS
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择媒体文件", "", f"{INPUT_FORMATS};;所有文件 (*.*)"
        )
        if files:
            self._add_files(files)

    def _clear(self):
        self._paths.clear()
        self.list_widget.clear()
        self.files_changed.emit([])

    def _add_files(self, paths):
        added = 0
        for p in paths:
            if p not in self._paths and os.path.isfile(p):
                self._paths.append(p)
                item = QListWidgetItem()
                self.list_widget.addItem(item)
                w = FileItemWidget(p)
                w.remove_clicked.connect(self._on_item_remove)
                item.setSizeHint(w.sizeHint())
                self.list_widget.setItemWidget(item, w)
                added += 1
        if added:
            self.files_changed.emit(list(self._paths))

    def _on_item_remove(self, widget):
        path = widget.path
        if path in self._paths:
            self._paths.remove(path)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if self.list_widget.itemWidget(item) is widget:
                self.list_widget.takeItem(i)
                break
        widget.deleteLater()
        self.files_changed.emit(list(self._paths))

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        remove_action = QAction("移除此文件", self)
        remove_action.triggered.connect(lambda: self._remove_item(item))
        menu.addAction(remove_action)
        clear_action = QAction("清空全部", self)
        clear_action.triggered.connect(self._clear)
        menu.addAction(clear_action)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def _remove_item(self, item):
        w = self.list_widget.itemWidget(item)
        if w:
            self._on_item_remove(w)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p and os.path.isfile(p):
                paths.append(p)
        if paths:
            self._add_files(paths)
            event.acceptProposedAction()

    @property
    def paths(self):
        return list(self._paths)
