PRESETS = {
    "MP4 H.264": {
        "ext": ".mp4", "vcodec": "libx264", "acodec": "aac",
        "crf": 23, "pix_fmt": "yuv420p",
        "desc": "通用兼容格式，适合网页/手机/电脑"
    },
    "MP4 H.265": {
        "ext": ".mp4", "vcodec": "libx265", "acodec": "aac",
        "crf": 28, "pix_fmt": "yuv420p",
        "desc": "HEVC 编码，体积比 H.264 小 30-50%"
    },
    "AVI": {
        "ext": ".avi", "vcodec": "mpeg4", "acodec": "mp3",
        "qscale": 3, "pix_fmt": "yuv420p",
        "desc": "旧式兼容格式，体积较大"
    },
    "MKV H.265": {
        "ext": ".mkv", "vcodec": "libx265", "acodec": "aac",
        "crf": 26, "pix_fmt": "yuv420p",
        "desc": "现代封装格式，支持多轨道"
    },
    "WEBM VP9": {
        "ext": ".webm", "vcodec": "libvpx-vp9", "acodec": "libopus",
        "crf": 30, "pix_fmt": "yuv420p",
        "desc": "开放格式，适合网页播放"
    },
    "WEBM VP8": {
        "ext": ".webm", "vcodec": "libvpx", "acodec": "libvorbis",
        "crf": 10, "pix_fmt": "yuv420p",
        "desc": "兼容性更好的 WebM"
    },
    "MOV": {
        "ext": ".mov", "vcodec": "libx264", "acodec": "aac",
        "crf": 18, "pix_fmt": "yuv420p",
        "desc": "Apple 原生格式，适合剪辑"
    },
    "GIF": {
        "ext": ".gif", "vcodec": "gif",
        "vf": "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "extra": [],
        "desc": "动图格式，自动缩放到 480px 宽"
    },
    "iPhone": {
        "ext": ".mp4", "vcodec": "libx264", "acodec": "aac",
        "crf": 22, "vf": "scale=-2:1080", "pix_fmt": "yuv420p",
        "desc": "适配 iPhone 屏幕，1080p"
    },
    "Telegram": {
        "ext": ".mp4", "vcodec": "libx264", "acodec": "aac",
        "crf": 28, "vf": "scale=-2:720", "pix_fmt": "yuv420p",
        "desc": "压缩至 50MB 以下，适合 Telegram 发送"
    },
    "3GP H.263": {
        "ext": ".3gp", "vcodec": "h263", "acodec": "aac",
        "qscale": 6, "pix_fmt": "yuv420p",
        "vf": "scale=-2:176",
        "desc": "老式手机格式，176p 低分辨率"
    },
    "MPEG-2": {
        "ext": ".mpg", "vcodec": "mpeg2video", "acodec": "mp2",
        "qscale": 4, "pix_fmt": "yuv420p",
        "desc": "DVD/VCD 兼容格式"
    },
    "OGV Theora": {
        "ext": ".ogv", "vcodec": "libtheora", "acodec": "libvorbis",
        "qscale": 6, "pix_fmt": "yuv420p",
        "desc": "开放免专利格式，适合开源项目"
    },
    "MP3 音频": {
        "ext": ".mp3", "vcodec": "copy",
        "acodec": "libmp3lame", "audio_bitrate": "192k",
        "desc": "提取/转换为 MP3 音频"
    },
    "FLAC 无损音频": {
        "ext": ".flac", "vcodec": "copy",
        "acodec": "flac",
        "desc": "无损音频格式"
    },
    "WAV PCM": {
        "ext": ".wav", "vcodec": "copy",
        "acodec": "pcm_s16le",
        "desc": "未压缩的 PCM 音频"
    },
    "AAC 音频": {
        "ext": ".m4a", "vcodec": "copy",
        "acodec": "aac", "audio_bitrate": "192k",
        "desc": "高压缩比音频格式"
    },
    "OPUS 音频": {
        "ext": ".ogg", "vcodec": "copy",
        "acodec": "libopus", "audio_bitrate": "128k",
        "desc": "开放音频格式，低延迟高音质"
    },
}

RESOLUTIONS = [
    ("原始", ""),
    ("8K (7680x4320)", "scale=-2:4320"),
    ("4K (3840x2160)", "scale=-2:2160"),
    ("1440p (2560x1440)", "scale=-2:1440"),
    ("1080p (1920x1080)", "scale=-2:1080"),
    ("720p (1280x720)", "scale=-2:720"),
    ("480p (854x480)", "scale=-2:480"),
    ("360p (640x360)", "scale=-2:360"),
    ("240p (426x240)", "scale=-2:240"),
]

ENCODERS = {
    "H.264 (libx264)": "libx264",
    "H.265/HEVC (libx265)": "libx265",
    "VP9 (libvpx-vp9)": "libvpx-vp9",
    "VP8 (libvpx)": "libvpx",
    "AV1 (libaom-av1)": "libaom-av1",
    "MPEG-4": "mpeg4",
    "MPEG-2": "mpeg2video",
    "Theora (libtheora)": "libtheora",
    "H.263": "h263",
    "原视频流 (copy)": "copy",
}

AUDIO_ENCODERS = {
    "AAC": "aac",
    "MP3": "libmp3lame",
    "Opus": "libopus",
    "Vorbis": "libvorbis",
    "FLAC": "flac",
    "PCM S16LE": "pcm_s16le",
    "AC-3": "ac3",
    "MP2": "mp2",
    "原音频流 (copy)": "copy",
}

BITRATES = ["64k", "96k", "128k", "160k", "192k", "224k", "256k", "320k"]

INPUT_FORMATS = (
    "所有媒体文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v "
    "*.ts *.mts *.3gp *.ogv *.ogg *.mpg *.mpeg *.vob *.mxf "
    "*.mp3 *.flac *.wav *.m4a *.aac *.opus *.wma)"
)

EXT_MAP = {
    ".3gp": [".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv"],
    ".avi": [".mp4", ".mkv", ".mov", ".webm", ".gif"],
    ".flv": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".mkv": [".mp4", ".avi", ".mov", ".webm", ".gif"],
    ".mov": [".mp4", ".avi", ".mkv", ".webm", ".gif"],
    ".mp4": [".avi", ".mkv", ".mov", ".webm", ".gif"],
    ".m4v": [".mp4", ".avi", ".mkv", ".mov", ".webm"],
    ".mts": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".ts": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".webm": [".mp4", ".mkv", ".avi", ".mov"],
    ".wmv": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".ogv": [".mp4", ".mkv", ".webm", ".mov"],
    ".mpg": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".mpeg": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".vob": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".mxf": [".mp4", ".mkv", ".avi", ".mov", ".webm"],
    ".3gp": [".mp3", ".flac", ".wav", ".m4a", ".ogg"],
    ".mp3": [".flac", ".wav", ".m4a", ".ogg"],
    ".flac": [".mp3", ".wav", ".m4a", ".ogg"],
    ".wav": [".mp3", ".flac", ".m4a", ".ogg"],
    ".m4a": [".mp3", ".flac", ".wav", ".ogg"],
    ".aac": [".mp3", ".flac", ".wav", ".m4a", ".ogg"],
    ".opus": [".mp3", ".flac", ".wav", ".m4a", ".ogg"],
    ".wma": [".mp3", ".flac", ".wav", ".m4a", ".ogg"],
}


def get_preset(name):
    return PRESETS.get(name)


def list_presets():
    return list(PRESETS.keys())
