#!/usr/bin/env python3
"""创意桥 —— 把本机图像/视频/3D 工具包成 HTTP 接口，供智能体调用。
默认 127.0.0.1:8090。只依赖 Pillow + 系统 ffmpeg，Blender 可选。
"""
import json, os, shutil, subprocess, sys, tempfile, uuid
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional
    import uvicorn
except ImportError:
    print("缺依赖，先跑：pip install fastapi uvicorn", file=sys.stderr)
    raise

from PIL import Image, ImageDraw, ImageFont, ImageOps

app = FastAPI(title="创意桥", version="1.0.0")


KNOWN = {
    "blender": ["~/Applications/Blender.app/Contents/MacOS/Blender",
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "C:/Program Files/Blender Foundation/Blender 4.5/blender.exe"],
    "inkscape": ["~/Applications/Inkscape.app/Contents/MacOS/inkscape",
                 "/Applications/Inkscape.app/Contents/MacOS/inkscape",
                 "C:/Program Files/Inkscape/bin/inkscape.exe"],
    "magick": ["/opt/homebrew/bin/magick", "/usr/local/bin/magick",
               "C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe"],
}


def which(name):
    p = shutil.which(name)
    if p:
        return p
    for c in KNOWN.get(name, []):
        c = os.path.expanduser(c)
        if os.path.exists(c):
            return c
    for c in [os.path.expanduser("~/.openclaw/bin/" + name)]:
        if os.path.exists(c):
            return c
    return None


def run(cmd, timeout=1800):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-800:])
    return r


def real_ffprobe():
    p = which("ffprobe")
    if not p:
        return None
    try:
        r = subprocess.run([p, "-version"], capture_output=True, text=True, timeout=10)
        return p if "ffprobe" in (r.stdout or "") else None
    except Exception:
        return None


def parse_ffmpeg_i(path):
    """没有真 ffprobe 时，从 ffmpeg -i 的 stderr 里抠元数据。"""
    ff = which("ffmpeg")
    if not ff:
        return {}
    r = subprocess.run([ff, "-hide_banner", "-i", path], capture_output=True, text=True, timeout=60)
    txt = r.stderr or ""
    import re
    dur = 0.0
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", txt)
    if m:
        dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    streams = []
    for line in txt.splitlines():
        line = line.strip()
        if line.startswith("Stream #"):
            st = {"type": "audio" if "Audio:" in line else ("video" if "Video:" in line else "other"),
                  "codec": None, "width": None, "height": None, "fps": None}
            mc = re.search(r"(?:Video|Audio):\s*([a-zA-Z0-9_]+)", line)
            if mc:
                st["codec"] = mc.group(1)
            mw = re.search(r"(\d{2,5})x(\d{2,5})", line)
            if mw:
                st["width"], st["height"] = int(mw.group(1)), int(mw.group(2))
            mf = re.search(r"(\d+\.?\d*)\s*fps", line)
            if mf:
                st["fps"] = mf.group(1)
            streams.append(st)
    return {"duration": dur, "size": os.path.getsize(path) if os.path.exists(path) else 0,
            "bitrate": None, "streams": streams}


def out_path(out):
    if not out:
        out = os.path.join(tempfile.gettempdir(), "cb_" + uuid.uuid4().hex[:8])
    Path(os.path.dirname(os.path.abspath(out)) or ".").mkdir(parents=True, exist_ok=True)
    return out


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/capabilities")
def capabilities():
    ff = which("ffmpeg")
    bl = which("blender")
    ins = which("inkscape")
    magick = which("magick") or which("convert")
    return {
        "image": {"engine": "Pillow", "ok": True},
        "video": {"engine": "ffmpeg", "ok": bool(ff), "path": ff},
        "design": {"engine": "Inkscape", "ok": bool(ins), "path": ins},
        "image_cli": {"engine": "ImageMagick", "ok": bool(magick), "path": magick},
        "3d": {"engine": "Blender", "ok": bool(bl), "path": bl},
    }


class ImgIn(BaseModel):
    path: str
    out: Optional[str] = None


class ResizeIn(ImgIn):
    width: Optional[int] = None
    height: Optional[int] = None
    long_edge: Optional[int] = None
    quality: int = 92


@app.post("/image/resize")
def image_resize(b: ResizeIn):
    im = Image.open(b.path)
    im = ImageOps.exif_transpose(im)
    if b.long_edge:
        w, h = im.size
        scale = b.long_edge / max(w, h)
        size = (max(1, int(w * scale)), max(1, int(h * scale)))
    elif b.width and b.height:
        size = (b.width, b.height)
    elif b.width:
        size = (b.width, max(1, int(im.size[1] * b.width / im.size[0])))
    elif b.height:
        size = (max(1, int(im.size[0] * b.height / im.size[1])), b.height)
    else:
        raise HTTPException(400, "width / height / long_edge 至少给一个")
    im = im.resize(size, Image.LANCZOS)
    o = out_path(b.out or os.path.splitext(b.path)[0] + "_%dx%d.jpg" % size)
    im.convert("RGB").save(o, quality=b.quality)
    return {"out": o, "size": size, "bytes": os.path.getsize(o)}


class ConvertIn(ImgIn):
    format: str = "WEBP"
    quality: int = 90


@app.post("/image/convert")
def image_convert(b: ConvertIn):
    im = Image.open(b.path)
    o = out_path(b.out or os.path.splitext(b.path)[0] + "." + b.format.lower())
    if b.format.upper() == "JPG":
        im.convert("RGB").save(o, "JPEG", quality=b.quality)
    else:
        im.save(o, b.format.upper(), quality=b.quality)
    return {"out": o, "bytes": os.path.getsize(o)}


class WaterIn(ImgIn):
    text: str
    position: str = "br"
    opacity: int = 140
    size_ratio: float = 0.045


@app.post("/image/watermark")
def image_watermark(b: WaterIn):
    im = Image.open(b.path).convert("RGBA")
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    fs = max(14, int(min(im.size) * b.size_ratio))
    font = None
    for f in ["/System/Library/Fonts/PingFang.ttc",
              "/System/Library/Fonts/Hiragino Sans GB.ttc",
              "/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyh.ttc"]:
        if os.path.exists(f):
            try:
                font = ImageFont.truetype(f, fs); break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()
    box = d.textbbox((0, 0), b.text, font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    pad = int(min(im.size) * 0.03)
    pos = {"br": (im.size[0] - tw - pad, im.size[1] - th - pad * 2),
           "bl": (pad, im.size[1] - th - pad * 2),
           "tr": (im.size[0] - tw - pad, pad),
           "tl": (pad, pad)}.get(b.position, (im.size[0] - tw - pad, im.size[1] - th - pad * 2))
    d.text(pos, b.text, font=font, fill=(255, 255, 255, b.opacity))
    o = out_path(b.out or os.path.splitext(b.path)[0] + "_wm.png")
    Image.alpha_composite(im, layer).convert("RGB").save(o, quality=93)
    return {"out": o, "bytes": os.path.getsize(o)}


class BatchIn(BaseModel):
    dir: str
    long_edge: Optional[int] = None
    format: Optional[str] = None
    quality: int = 90


@app.post("/image/batch")
def image_batch(b: BatchIn):
    exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}
    done, errs = [], []
    for p in sorted(Path(b.dir).iterdir()):
        if p.suffix.lower() not in exts:
            continue
        try:
            im = Image.open(p)
            im = ImageOps.exif_transpose(im)
            if b.long_edge:
                w, h = im.size
                s = b.long_edge / max(w, h)
                im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
            fmt = (b.format or "jpg").upper()
            o = p.with_name(p.stem + "_out." + fmt.lower())
            im.convert("RGB").save(o, fmt, quality=b.quality)
            done.append(str(o))
        except Exception as e:
            errs.append({"file": str(p), "error": str(e)[:120]})
    return {"count": len(done), "outputs": done, "errors": errs}


class VidIn(BaseModel):
    path: str
    out: Optional[str] = None


@app.post("/video/probe")
def video_probe(b: VidIn):
    ff = real_ffprobe()
    if not ff:
        j = parse_ffmpeg_i(b.path)
        if not j:
            raise HTTPException(500, "缺少 ffmpeg/ffprobe")
        return j
    r = run([ff, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", b.path])
    j = json.loads(r.stdout)
    f = j.get("format", {})
    return {"duration": float(f.get("duration", 0)), "size": int(f.get("size", 0)),
            "bitrate": f.get("bit_rate"), "streams": [
                {"type": s.get("codec_type"), "codec": s.get("codec_name"),
                 "width": s.get("width"), "height": s.get("height"),
                 "fps": s.get("r_frame_rate")} for s in j.get("streams", [])]}


class TrimIn(VidIn):
    start: float = 0
    duration: float = 5
    reencode: bool = False


@app.post("/video/trim")
def video_trim(b: TrimIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    o = out_path(b.out or os.path.splitext(b.path)[0] + "_trim.mp4")
    cmd = [ff, "-y", "-ss", str(b.start), "-i", b.path, "-t", str(b.duration)]
    cmd += (["-c:v", "libx264", "-crf", "20", "-c:a", "aac"] if b.reencode else ["-c", "copy"])
    cmd += [o]
    run(cmd)
    return {"out": o, "bytes": os.path.getsize(o)}


class TransIn(VidIn):
    crf: int = 23
    max_width: Optional[int] = None
    preset: str = "medium"


@app.post("/video/transcode")
def video_transcode(b: TransIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    o = out_path(b.out or os.path.splitext(b.path)[0] + "_c.mp4")
    vf = ("scale=%d:-2" % b.max_width) if b.max_width else "scale=trunc(iw/2)*2:trunc(ih/2)*2"
    run([ff, "-y", "-i", b.path, "-vf", vf, "-c:v", "libx264", "-crf", str(b.crf),
         "-preset", b.preset, "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", o])
    return {"out": o, "bytes": os.path.getsize(o)}


class GifIn(VidIn):
    start: float = 0
    duration: float = 3
    width: int = 480
    fps: int = 12


@app.post("/video/gif")
def video_gif(b: GifIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    o = out_path(b.out or os.path.splitext(b.path)[0] + ".gif")
    run([ff, "-y", "-ss", str(b.start), "-t", str(b.duration), "-i", b.path,
         "-vf", "fps=%d,scale=%d:-1:flags=lanczos" % (b.fps, b.width), "-loop", "0", o])
    return {"out": o, "bytes": os.path.getsize(o)}


class FrameIn(VidIn):
    time: float = 0
    width: Optional[int] = None


@app.post("/video/frame")
def video_frame(b: FrameIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    o = out_path(b.out or os.path.splitext(b.path)[0] + "_%.1fs.jpg" % b.time)
    vf = ("scale=%d:-2" % b.width) if b.width else "null"
    run([ff, "-y", "-ss", str(b.time), "-i", b.path, "-frames:v", "1", "-vf", vf, "-q:v", "2", o])
    return {"out": o, "bytes": os.path.getsize(o)}


class AudioIn(VidIn):
    format: str = "mp3"


@app.post("/audio/extract")
def audio_extract(b: AudioIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    info = parse_ffmpeg_i(b.path)
    if not any(s.get("type") == "audio" for s in info.get("streams", [])):
        raise HTTPException(400, "源文件没有音轨，无法提取音频")
    o = out_path(b.out or os.path.splitext(b.path)[0] + "." + b.format)
    run([ff, "-y", "-i", b.path, "-vn", "-c:a", "libmp3lame" if b.format == "mp3" else "aac", o])
    return {"out": o, "bytes": os.path.getsize(o)}


class ConcatIn(BaseModel):
    paths: List[str]
    out: Optional[str] = None


@app.post("/video/concat")
def video_concat(b: ConcatIn):
    ff = which("ffmpeg")
    if not ff:
        raise HTTPException(500, "ffmpeg 未安装")
    lst = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    for p in b.paths:
        lst.write("file '" + os.path.abspath(p).replace("'", "'\\''") + "'\n")
    lst.close()
    o = out_path(b.out or os.path.join(os.path.dirname(b.paths[0]), "concat.mp4"))
    run([ff, "-y", "-f", "concat", "-safe", "0", "-i", lst.name, "-c", "copy", o])
    os.unlink(lst.name)
    return {"out": o, "bytes": os.path.getsize(o)}



# ---------- 矢量 / 设计 ----------
class SvgIn(BaseModel):
    svg_text: Optional[str] = None
    path: Optional[str] = None
    out: Optional[str] = None
    size: int = 1600


def _svg_engine():
    if which("inkscape"):
        return "inkscape"
    if os.uname().sysname == "Darwin" and shutil.which("qlmanage"):
        return "quicklook"
    return None


@app.post("/design/svg_to_png")
def svg_to_png(b: SvgIn):
    eng = _svg_engine()
    if not eng:
        raise HTTPException(501, "没有可用的 SVG 渲染器（需 Inkscape，或 macOS 系统 qlmanage）")
    if b.svg_text:
        src = os.path.join(tempfile.gettempdir(), "svg_" + uuid.uuid4().hex[:8] + ".svg")
        open(src, "w", encoding="utf-8").write(b.svg_text)
    elif b.path:
        src = b.path
    else:
        raise HTTPException(400, "svg_text 或 path 必须给一个")
    o = b.out or os.path.splitext(src)[0] + ".png"
    Path(os.path.dirname(os.path.abspath(o)) or ".").mkdir(parents=True, exist_ok=True)
    if eng == "inkscape":
        run([which("inkscape"), src, "--export-type=png", "--export-filename=" + o,
             "--export-width=" + str(b.size)])
    else:
        d = tempfile.mkdtemp()
        run(["/usr/bin/qlmanage", "-t", "-s", str(b.size), "-o", d, src])
        gen = os.path.join(d, os.path.basename(src) + ".png")
        if not os.path.exists(gen):
            raise HTTPException(500, "qlmanage 未生成预览")
        shutil.move(gen, o)
    return {"out": o, "bytes": os.path.getsize(o), "engine": eng}


@app.post("/design/svg_to_pdf")
def svg_to_pdf(b: SvgIn):
    r = svg_to_png(SvgIn(svg_text=b.svg_text, path=b.path, out=None, size=b.size))
    im = Image.open(r["out"]).convert("RGB")
    o = b.out or os.path.splitext(r["out"])[0] + ".pdf"
    Path(os.path.dirname(os.path.abspath(o)) or ".").mkdir(parents=True, exist_ok=True)
    im.save(o, "PDF", resolution=150)
    return {"out": o, "bytes": os.path.getsize(o), "via": "raster"}


@app.get("/design/info")
def design_info():
    return {"engine": _svg_engine(), "inkscape": which("inkscape"),
            "note": "macOS 用系统 qlmanage 渲染 SVG，无需外装；Windows 需 Inkscape"}

class RenderIn(BaseModel):
    blend: str
    out: Optional[str] = None
    frame: int = 1


@app.post("/3d/render")
def render3d(b: RenderIn):
    bl = which("blender")
    if not bl:
        raise HTTPException(500, "Blender 未安装（https://www.blender.org/download/）")
    o = out_path(b.out or os.path.splitext(b.blend)[0] + "_f%d.png" % b.frame)
    run([bl, "-b", b.blend, "-o", o.replace(".png", "_####"), "-f", str(b.frame)], timeout=3600)
    import glob
    prefix = o.replace(".png", "")
    found = sorted(glob.glob(prefix + "*"))
    real = found[0] if found else o
    return {"out": real, "frame": b.frame,
            "bytes": os.path.getsize(real) if os.path.exists(real) else 0}


if __name__ == "__main__":
    port = int(os.environ.get("CB_PORT", "8090"))
    print("创意桥 -> http://127.0.0.1:" + str(port))
    caps = capabilities()
    for k, v in caps.items():
        print("  %-10s %s" % (k, "OK" if v["ok"] else "未安装"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")