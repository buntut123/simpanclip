"""Fungsi pembantu murni (tanpa FastAPI/yt-dlp) supaya mudah diuji.

- collect(): memisahkan hasil yt-dlp menjadi item video dan item foto
- fetch_image(): mengambil foto dari server dengan perlindungan SSRF
"""
import ipaddress
import os
import socket
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

IMAGE_EXTS = {"jpg", "jpeg", "png", "webp", "gif", "heic"}
VIDEO_EXTS = {"mp4", "webm", "mov", "m4v", "mkv", "m3u8"}
MAX_IMAGE_BYTES = 25 * 1024 * 1024
_CTYPE_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}


class ApiError(Exception):
    def __init__(self, status: int, code: str):
        self.status, self.code = status, code


def is_video(e: dict) -> bool:
    if any(f.get("vcodec") not in (None, "none") for f in e.get("formats") or []):
        return True
    if e.get("vcodec") not in (None, "none"):
        return True
    if e.get("duration"):
        return True
    return (e.get("ext") or "").lower() in VIDEO_EXTS


def best_image_url(e: dict):
    url, ext = e.get("url"), (e.get("ext") or "").lower()
    if url and ext in IMAGE_EXTS:
        return url
    fm = [f for f in e.get("formats") or [] if f.get("url") and (f.get("ext") or "").lower() in IMAGE_EXTS]
    if fm:
        return max(fm, key=lambda f: (f.get("width") or 0) * (f.get("height") or 0))["url"]
    th = [t for t in e.get("thumbnails") or [] if t.get("url")]
    if th:
        return max(th, key=lambda t: ((t.get("width") or 0) * (t.get("height") or 0), t.get("preference") or 0))["url"]
    return e.get("thumbnail")


def collect(info: dict):
    """-> (entri_video_pertama | None, [url_foto, ...])"""
    raw = info.get("entries")
    entries = [e for e in raw if e] if raw else [info]
    video, images = None, []
    for e in entries:
        if is_video(e):
            video = video or e
        else:
            u = best_image_url(e)
            if u:
                images.append(u)
    return video, images


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # redirect ditangani manual agar tiap tujuan divalidasi
        return None


def assert_public_https(url: str):
    """Tolak alamat non-HTTPS dan alamat yang menunjuk ke jaringan internal (SSRF)."""
    u = urlparse(url)
    if u.scheme != "https" or not u.hostname:
        raise ApiError(502, "failed")
    try:
        addrs = socket.getaddrinfo(u.hostname, u.port or 443, type=socket.SOCK_STREAM)
    except OSError:
        raise ApiError(502, "failed")
    for a in addrs:
        if not ipaddress.ip_address(a[4][0]).is_global:
            raise ApiError(502, "failed")


def fetch_image(url: str, dest_dir: str):
    """Unduh satu foto ke dest_dir. Mengembalikan (path, ext)."""
    opener = urllib.request.build_opener(_NoRedirect)
    for _ in range(4):
        assert_public_https(url)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            resp = opener.open(req, timeout=20)
        except urllib.error.HTTPError as exc:
            loc = exc.headers.get("Location") if exc.headers else None
            if exc.code in (301, 302, 303, 307, 308) and loc:
                url = urljoin(url, loc)
                continue
            raise ApiError(502, "failed")
        except OSError:
            raise ApiError(502, "failed")
        with resp:
            ctype = resp.headers.get_content_type() or ""
            if not ctype.startswith("image/"):
                raise ApiError(502, "failed")
            ext = _CTYPE_EXT.get(ctype, "jpg")
            path = os.path.join(dest_dir, f"image.{ext}")
            size = 0
            with open(path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_IMAGE_BYTES:
                        raise ApiError(413, "too_long")
                    f.write(chunk)
        return path, ext
    raise ApiError(502, "failed")
