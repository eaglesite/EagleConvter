import re
import subprocess as sp
import shutil


def find_ffmpeg():
    return shutil.which("ffmpeg") or shutil.which("ffmpeg.exe") or "ffmpeg"


def find_ffprobe():
    return shutil.which("ffprobe") or shutil.which("ffprobe.exe") or "ffprobe"


_TIME_RE = re.compile(r"time=(\d+):(\d+):(\d+)\.(\d+)")
_FPS_RE = re.compile(r"fps=\s*(\d+(?:\.\d+)?)")
_SPEED_RE = re.compile(r"speed=\s*(\d+(?:\.\d+)?)x")
_FRAME_RE = re.compile(r"frame=\s*(\d+)")


def parse_progress(line):
    m = _TIME_RE.search(line)
    if not m:
        return None
    h, mn, s, cs = map(int, m.groups())
    secs = h * 3600 + mn * 60 + s + cs / 100
    fps_m = _FPS_RE.search(line)
    speed_m = _SPEED_RE.search(line)
    frame_m = _FRAME_RE.search(line)
    return {
        "secs": secs,
        "fps": float(fps_m.group(1)) if fps_m else 0,
        "speed": float(speed_m.group(1)) if speed_m else 0,
        "frame": int(frame_m.group(1)) if frame_m else 0,
    }


CREATE_NO_WINDOW = 0x08000000


class FFmpegProcess:
    def __init__(self, on_progress=None, on_done=None, on_error=None):
        self._proc = None
        self._on_progress = on_progress
        self._on_done = on_done
        self._on_error = on_error
        self._total_secs = 0

    def set_duration(self, secs):
        self._total_secs = secs

    def build_cmd(self, input_path, output_path, opts):
        cmd = [find_ffmpeg(), "-y", "-i", input_path]

        vcodec = opts.get("vcodec", "libx264")
        acodec = opts.get("acodec", "aac")
        vf = opts.get("vf", "")
        extra = opts.get("extra", [])
        is_audio_only = vcodec == "copy" and acodec != "copy"

        if vcodec == "gif":
            if vf:
                cmd += ["-vf", vf]
            cmd += ["-pix_fmt", "rgb8"]
        else:
            if vf:
                cmd += ["-vf", vf]
            if not is_audio_only:
                cmd += ["-c:v", vcodec, "-pix_fmt", opts.get("pix_fmt", "yuv420p")]
                crf = opts.get("crf")
                if crf is not None:
                    cmd += ["-crf", str(crf)]
                qscale = opts.get("qscale")
                if qscale is not None:
                    cmd += ["-qscale:v", str(qscale)]
                video_bitrate = opts.get("video_bitrate")
                if video_bitrate:
                    cmd += ["-b:v", video_bitrate]
                fps = opts.get("fps")
                if fps:
                    cmd += ["-r", str(fps)]
            cmd += ["-c:a", acodec]
            audio_bitrate = opts.get("audio_bitrate")
            if audio_bitrate:
                cmd += ["-b:a", audio_bitrate]

        if extra:
            cmd += extra

        cmd.append(output_path)
        return cmd

    def run(self, cmd):
        try:
            self._proc = sp.Popen(
                cmd,
                stdout=sp.DEVNULL,
                stderr=sp.PIPE,
                creationflags=CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            if self._on_error:
                self._on_error("未找到 FFmpeg，请安装后重试")
            return

        for raw in iter(self._proc.stderr.readline, b""):
            if self._proc is None:
                break
            try:
                line = raw.decode("utf-8", errors="replace")
            except Exception:
                continue
            parsed = parse_progress(line)
            if parsed and self._total_secs > 0 and self._on_progress:
                pct = min(parsed["secs"] / self._total_secs * 100, 99.9)
                self._on_progress(pct, parsed)

        self._proc.wait()
        if self._proc is None:
            return

        if self._proc.returncode == 0:
            if self._on_done:
                self._on_done(True)
        else:
            if self._on_error:
                self._on_error(f"FFmpeg 退出码: {self._proc.returncode}")

    def cancel(self):
        if self._proc:
            self._proc.terminate()
            self._proc = None


def probe_duration(path):
    try:
        cmd = [find_ffprobe(), "-v", "error", "-show_entries",
               "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path]
        r = sp.run(cmd, capture_output=True, text=True, timeout=15,
                   encoding="utf-8", errors="replace",
                   creationflags=CREATE_NO_WINDOW)
        return float(r.stdout.strip()) if r.stdout.strip() else 0
    except Exception:
        return 0


def probe_info(path):
    try:
        cmd = [find_ffprobe(), "-v", "error",
               "-show_entries", "format=duration,size,bit_rate,format_name",
               "-show_entries", "stream=codec_name,codec_type,width,height,r_frame_rate",
               "-of", "json", path]
        r = sp.run(cmd, capture_output=True, text=True, timeout=15,
                   encoding="utf-8", errors="replace",
                   creationflags=CREATE_NO_WINDOW)
        import json
        return json.loads(r.stdout)
    except Exception:
        return {}
