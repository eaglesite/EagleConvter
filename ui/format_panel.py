from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QComboBox, QLabel, QSlider, QFormLayout,
)
from PySide6.QtCore import Qt
from core.formats import (
    list_presets, PRESETS, RESOLUTIONS,
    ENCODERS, AUDIO_ENCODERS, BITRATES,
)


ALL_EXTS = sorted({p["ext"] for p in PRESETS.values()})


class FormatPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        preset_box = QGroupBox("快速预设")
        preset_layout = QVBoxLayout(preset_box)
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("自定义", "")
        for name in list_presets():
            p = PRESETS[name]
            label = f"{name}"
            if p.get("desc"):
                label += f"  —  {p['desc']}"
            self.preset_combo.addItem(label, name)
        self.preset_combo.currentIndexChanged.connect(self._on_preset)
        preset_layout.addWidget(self.preset_combo)

        self.preset_desc = QLabel("选择预设或自定义下方参数")
        self.preset_desc.setObjectName("presetDesc")
        self.preset_desc.setWordWrap(True)
        preset_layout.addWidget(self.preset_desc)
        layout.addWidget(preset_box)

        adv_box = QGroupBox("详细参数")
        form = QFormLayout(adv_box)

        self.res_combo = QComboBox()
        for name, _ in RESOLUTIONS:
            self.res_combo.addItem(name)
        form.addRow("分辨率:", self.res_combo)

        self.fps_combo = QComboBox()
        for val in ["原始", "60", "30", "24", "15", "10"]:
            self.fps_combo.addItem(val, val if val != "原始" else "")
        form.addRow("帧率 (FPS):", self.fps_combo)

        self.enc_combo = QComboBox()
        for name, val in ENCODERS.items():
            self.enc_combo.addItem(name, val)
        self.enc_combo.currentIndexChanged.connect(self._on_encoder_change)
        form.addRow("视频编码:", self.enc_combo)

        self.aenc_combo = QComboBox()
        for name, val in AUDIO_ENCODERS.items():
            self.aenc_combo.addItem(name, val)
        form.addRow("音频编码:", self.aenc_combo)

        crf_row = QHBoxLayout()
        self.crf_slider = QSlider(Qt.Horizontal)
        self.crf_slider.setRange(0, 51)
        self.crf_slider.setValue(23)
        self.crf_label = QLabel("23")
        self.crf_label.setMinimumWidth(30)
        self.crf_slider.valueChanged.connect(lambda v: self.crf_label.setText(str(v)))
        crf_row.addWidget(self.crf_slider, 1)
        crf_row.addWidget(self.crf_label)
        form.addRow("CRF 质量 (0=无损, 51=最差):", crf_row)

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItem("自动 (CRF)", "")
        for b in BITRATES:
            self.bitrate_combo.addItem(b, b)
        form.addRow("音频码率:", self.bitrate_combo)

        self.ext_combo = QComboBox()
        for ext in ALL_EXTS:
            self.ext_combo.addItem(ext, ext)
        form.addRow("输出格式:", self.ext_combo)

        layout.addWidget(adv_box)
        layout.addStretch()

    def _on_preset(self, idx):
        name = self.preset_combo.currentData()
        if not name or name not in PRESETS:
            self.preset_desc.setText("自定义参数")
            return
        p = PRESETS[name]
        self.preset_desc.setText(p.get("desc", ""))

        for k, v in ENCODERS.items():
            if v == p.get("vcodec"):
                self.enc_combo.setCurrentText(k)
                break

        for k, v in AUDIO_ENCODERS.items():
            if v == p.get("acodec"):
                self.aenc_combo.setCurrentText(k)
                break

        if "crf" in p and "qscale" not in p:
            self.crf_slider.setValue(p["crf"])

        ab = p.get("audio_bitrate", "")
        idx_ab = self.bitrate_combo.findData(ab)
        if idx_ab >= 0:
            self.bitrate_combo.setCurrentIndex(idx_ab)

        ext = p.get("ext", ".mp4")
        idx_ext = self.ext_combo.findData(ext)
        if idx_ext >= 0:
            self.ext_combo.setCurrentIndex(idx_ext)

        vf = p.get("vf", "")
        if "scale=" in vf:
            for i, (rname, rval) in enumerate(RESOLUTIONS):
                if rval and rval in vf:
                    self.res_combo.setCurrentIndex(i)
                    break

        fps = p.get("fps", "")
        if fps:
            idx_fps = self.fps_combo.findData(str(fps))
            if idx_fps >= 0:
                self.fps_combo.setCurrentIndex(idx_fps)

    def _on_encoder_change(self, idx):
        enc = self.enc_combo.currentData()
        if enc == "libx265":
            if self.crf_slider.value() < 24:
                self.crf_slider.setValue(28)
        elif enc == "libaom-av1":
            if self.crf_slider.value() < 30:
                self.crf_slider.setValue(35)

    def get_options(self):
        opts = {}
        res_val = RESOLUTIONS[self.res_combo.currentIndex()][1]
        if res_val:
            opts["vf"] = res_val

        fps = self.fps_combo.currentData()
        if fps:
            opts["fps"] = fps

        vf_parts = []
        if opts.get("vf"):
            vf_parts.append(opts["vf"])

        preset_name = self.preset_combo.currentData()
        if preset_name and preset_name in PRESETS:
            p = PRESETS[preset_name]
            preset_vf = p.get("vf", "")
            if preset_vf and preset_vf not in vf_parts:
                vf_parts.append(preset_vf)

        if vf_parts:
            opts["vf"] = ",".join(vf_parts)

        opts["vcodec"] = self.enc_combo.currentData()
        opts["acodec"] = self.aenc_combo.currentData()
        opts["crf"] = self.crf_slider.value()
        opts["ext"] = self.ext_combo.currentData()

        ab = self.bitrate_combo.currentData()
        if ab:
            opts["audio_bitrate"] = ab

        return opts
