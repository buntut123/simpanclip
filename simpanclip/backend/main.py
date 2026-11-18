"""SimpanClip backend: FastAPI + yt-dlp.

Endpoint:
  GET  /health
  POST /api/info      {"url": "..."}  -> judul, thumbnail, durasi, daftar kualitas
  GET  /api/download  ?url=...&q=720|best|audio -> file (attachment)

Prinsip: hanya domain yang diizinkan, hanya konten publik, tidak menyimpan apa pun,
tidak mencatat tautan (jalankan uvicorn dengan --no-access-log).
"""
import asyncio
import mimetypes
import os
import re
import shutil
import tempfile
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import yt_dlp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from media import ApiError, collect, fetch_image

# ------------------------------------------------------------------ konfigurasi
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",") if o.strip()]
MAX_DURATION = int(os.getenv("MAX_DURATION", "1800"))          # detik
MAX_FILESIZE = int(os.getenv("MAX_FILESIZE_MB", "500")) * 1024 * 1024
MAX_HEIGHT = int(os.getenv("MAX_HEIGHT", "1080"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", "3"))
INFO_LIMIT = int(os.getenv("INFO_LIMIT", "20"))                  # per menit per IP
DOWNLOAD_LIMIT = int(os.getenv("DOWNLOAD_LIMIT", "8"))           # per menit per IP
TRUST_PROXY = os.getenv("TRUST_PROXY", "0") == "1"
FILE_TTL = 600                                                   # detik
TMP_PREFIX = "simpanclip-"

PLATFORMS = {
    "facebook.com": "Facebook",
    "fb.watch": "Facebook",
    "instagram.com": "Instagram",
    "tiktok.com": "TikTok",
}


class InfoBody(BaseModel):
    url: str


# ------------------------------------------------------------------ util
def check_url(raw: str):
    """Validasi tautan dan kembalikan (url, nama_platform). Hanya domain di allowlist."""
    raw = (raw or "").strip()
    if len(raw) > 2048:
        raise ApiError(400, "invalid")
    try:
        u = urlparse(raw)
    except ValueError:
        raise ApiError(400, "invalid")
    if u.scheme not in ("http", "https") or not u.hostname:
        raise ApiError(400, "invalid")
    host = u.hostname.lower().rstrip(".")
    for domain, name in PLATFORMS.items():
        if host == domain or host.endswith("." + domain):
            return raw, name
    raise ApiError(400, "unsupported")


_hits = defaultdict(deque)


def client_ip(request: Request) -> str:
    if TRUST_PROXY:
        for h in ("cf-connecting-ip", "x-forwarded-for"):
            v = request.headers.get(h)
            if v:
                return v.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request, bucket: str, limit: int):
    key = (bucket, client_ip(request))
    now = time.monotonic()
    q = _hits[key]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        raise ApiError(429, "rate")
    q.append(now)
    if len(_hits) > 20000:  # jaga memori
        for k in [k for k, v in _hits.items() if not v or now - v[-1] > 60]:
            _hits.pop(k, None)


def classify(exc: Exception) -> ApiError:
    msg = str(exc).lower()
    if "no video in this post" in msg:
        return ApiError(422, "no_media")
    if any(w in msg for w in ("private", "login", "log in", "sign in", "cookies", "not available", "unavailable", "removed", "deleted")):
        return ApiError(422, "private")
    if "unsupported url" in msg:
        return ApiError(400, "unsupported")
    return ApiError(502, "failed")


def base_opts() -> dict:
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 20,
        "retries": 2,
        "nocheckcertificate": False,
    }


def safe_filename(title: str, ext: str) -> str:
    name = re.sub(r'[\\/:*?"<>|\r\n\t]+', " ", title or "").strip()[:80].strip(" .")
    return f"{name or 'simpanclip'}.{ext}"


def sweep_old_dirs():
    base = tempfile.gettempdir()
    now = time.time()
    for n in os.listdir(base):
        if n.startswith(TMP_PREFIX):
            p = os.path.join(base, n)
            try:
                if now - os.path.getmtime(p) > FILE_TTL:
                    shutil.rmtree(p, ignore_errors=True)
            except OSError:
                pass


async def sweeper():
    while True:
        await asyncio.sleep(120)
        try:
            await run_in_threadpool(sweep_old_dirs)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    sweep_old_dirs()
    task = asyncio.create_task(sweeper())
    yield
    task.cancel()


app = FastAPI(title="SimpanClip API", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["Content-Disposition"],
)
slots = asyncio.Semaphore(MAX_CONCURRENT)


@app.exception_handler(ApiError)
async def api_error_handler(_: Request, exc: ApiError):
    return JSONResponse({"error": exc.code}, status_code=exc.status)


# ------------------------------------------------------------------ endpoint
@app.get("/health")
def health():
    return {"ok": True, "yt_dlp": yt_dlp.version.__version__}


def extract_info(url: str) -> dict:
    with yt_dlp.YoutubeDL({**base_opts(), "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    return info or {}


@app.post("/api/info")
async def api_info(body: InfoBody, request: Request):
    rate_limit(request, "info", INFO_LIMIT)
    url, platform = check_url(body.url)
    try:
        info = await run_in_threadpool(extract_info, url)
    except Exception as exc:  # yt_dlp.utils.DownloadError dan sejenisnya
        raise classify(exc)
    if not info:
        raise ApiError(502, "failed")
    video, images = collect(info)
    if not video and not images:
        raise ApiError(422, "no_media")
    duration, qualities = 0, []
    if video:
        duration = int(video.get("duration") or 0)
        if duration and duration > MAX_DURATION:
            raise ApiError(413, "too_long")
        heights = sorted(
            {int(f["height"]) for f in video.get("formats") or []
             if f.get("height") and f.get("vcodec") not in (None, "none") and int(f["height"]) <= MAX_HEIGHT},
            reverse=True,
        )[:5]
        qualities = [{"id": str(h)} for h in heights] or [{"id": "best"}]
    first = video or info
    return {
        "platform": platform,
        "title": (first.get("title") or info.get("title") or "")[:200],
        "thumbnail": first.get("thumbnail") or (images[0] if images else None),
        "duration": duration,
        "qualities": qualities,
        "audio": bool(video),
        "images": [{"index": i, "thumbnail": u} for i, u in enumerate(images[:20])],
    }


@app.get("/api/image")
async def api_image(request: Request, url: str, i: int = 0):
    rate_limit(request, "dl", DOWNLOAD_LIMIT * 3)
    url, _ = check_url(url)
    try:
        info = await run_in_threadpool(extract_info, url)
    except Exception as exc:
        raise classify(exc)
    _, images = collect(info or {})
    if not 0 <= i < len(images):
        raise ApiError(404, "no_media")
    tmp = tempfile.mkdtemp(prefix=TMP_PREFIX)
    try:
        path, ext = await run_in_threadpool(fetch_image, images[i], tmp)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    return FileResponse(
        path,
        media_type=mimetypes.guess_type(path)[0] or "image/jpeg",
        filename=safe_filename(f"foto-{i + 1}", ext),
        background=BackgroundTask(shutil.rmtree, tmp, ignore_errors=True),
    )


def format_for(q: str) -> str:
    if q == "audio":
        return "bestaudio/best"
    if q == "best":
        return "bv*+ba/b"
    h = int(q)
    return (f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/bv*[height<={h}]+ba/b[height<={h}]/b")


def run_download(url: str, q: str, tmp: str):
    opts = {
        **base_opts(),
        "format": format_for(q),
        "outtmpl": os.path.join(tmp, "video.%(ext)s"),
        "max_filesize": MAX_FILESIZE,
        "match_filter": yt_dlp.utils.match_filter_func(f"duration<=?{MAX_DURATION}"),
        "merge_output_format": "mp4",
    }
    if q == "audio":
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    if info and info.get("_type") == "playlist" and info.get("entries"):
        info = next((e for e in info["entries"] if e), info)
    files = [os.path.join(tmp, n) for n in os.listdir(tmp)]
    files = [f for f in files if os.path.isfile(f) and not f.endswith((".part", ".ytdl"))]
    if not files:
        raise ApiError(413, "too_long")
    path = max(files, key=os.path.getsize)
    return path, (info or {}).get("title") or ""


@app.get("/api/download")
async def api_download(request: Request, url: str, q: str = "best"):
    rate_limit(request, "dl", DOWNLOAD_LIMIT)
    url, _ = check_url(url)
    if q not in ("best", "audio") and not (q.isdigit() and 100 <= int(q) <= MAX_HEIGHT):
        raise ApiError(400, "invalid")
    try:
        await asyncio.wait_for(slots.acquire(), timeout=20)
    except asyncio.TimeoutError:
        raise ApiError(503, "busy")
    tmp = tempfile.mkdtemp(prefix=TMP_PREFIX)
    try:
        path, title = await run_in_threadpool(run_download, url, q, tmp)
    except ApiError:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        raise classify(exc)
    finally:
        slots.release()
    ext = os.path.splitext(path)[1].lstrip(".") or "mp4"
    media = mimetypes.guess_type(path)[0] or "application/octet-stream"
    return FileResponse(
        path,
        media_type=media,
        filename=safe_filename(title, ext),
        background=BackgroundTask(shutil.rmtree, tmp, ignore_errors=True),
    )
