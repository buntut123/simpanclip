#!/usr/bin/env python3
"""Membuat semua halaman statis SimpanClip (Indonesia + Inggris) ke folder dist/.

Pakai:  python build.py            (domain bawaan simpanclip.com)
        SIMPANCLIP_DOMAIN=contoh.com python build.py
Hasil ada di frontend/dist, siap diunggah ke Cloudflare Pages.
"""
import html
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "static")
OUT = os.path.join(HERE, "dist")
DOMAIN = os.environ.get("SIMPANCLIP_DOMAIN", "simpanclip.com")
LANGS = ("id", "en")

LOGO = (
    '<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="16" fill="#6C4DF6"/>'
    '<path d="M24 14.5c0-1.9 2-3 3.6-2l20.4 12.6c1.5.9 1.5 3.1 0 4L27.6 41.7c-1.6 1-3.6-.1-3.6-2z" fill="#fff" '
    'transform="translate(-2 2) rotate(90 32 28) translate(-0 -4)"/>'
    '<rect x="18" y="49" width="28" height="4.5" rx="2.25" fill="#FF7A59"/></svg>'
)

# ---------------------------------------------------------------- teks
T = {
    "id": {
        "brand_tag": "Simpan video favoritmu, gratis.",
        "nav_guide": "Panduan",
        "other_lang": "EN",
        "ph": "Tempel tautan video di sini…",
        "paste": "Tempel",
        "go": "Unduh",
        "supported": "Didukung:",
        "steps_h": "Cara mengunduh video",
        "steps": [
            ("Salin tautan", "Buka video di aplikasi atau browser, ketuk Bagikan, lalu pilih Salin tautan."),
            ("Tempel di SimpanClip", "Tempel tautan ke kotak di atas, lalu tekan Unduh."),
            ("Simpan videonya", "Pilih kualitas yang kamu mau. Video langsung tersimpan di perangkatmu."),
        ],
        "why_h": "Kenapa pakai SimpanClip",
        "why": [
            ("Tanpa instal", "Langsung dari browser di Android, iPhone, atau komputer."),
            ("Tanpa akun", "Tidak perlu daftar atau login. Tempel, pilih, unduh."),
            ("Tidak disimpan", "File sementara dihapus otomatis dalam 10 menit. Tautanmu tidak kami catat."),
        ],
        "faq_h": "Pertanyaan umum",
        "faq": [
            ("Apakah SimpanClip gratis?", "Ya, gratis dan tanpa akun."),
            ("Video dan foto apa saja yang bisa diunduh?", "Video dan foto publik dari Facebook, Instagram, dan TikTok. Postingan foto tidak selalu bisa diambil, tergantung platform. Konten privat, video yang butuh login, atau siaran langsung yang masih berjalan tidak bisa diunduh."),
            ("Bagaimana cara mengunduh di iPhone?", "Gunakan Safari. Setelah proses selesai, ketuk ikon unduhan di Safari, lalu buka file di aplikasi Berkas. Dari sana video bisa dibagikan atau disimpan ke Foto."),
            ("Bolehkah mengunduh video orang lain?", "Hanya untuk penggunaan pribadi dan sesuai izin pemilik. Jangan mengunggah ulang video orang lain sebagai karyamu. Kamu bertanggung jawab atas cara memakai hasil unduhan."),
            ("Apakah SimpanClip menyimpan video saya?", "Tidak. File hanya ada sementara di server selama proses unduh, lalu dihapus otomatis dalam 10 menit. Kami tidak membuat akun dan tidak mencatat tautan yang kamu tempel."),
            ("Kenapa unduhan gagal?", "Penyebab paling umum: tautan salah, video bersifat privat atau sudah dihapus, atau platform sedang membatasi akses. Coba salin tautan lagi, atau coba beberapa menit kemudian."),
        ],
        "disclaimer": "SimpanClip tidak berafiliasi dengan Facebook, Instagram, atau TikTok. Gunakan hanya untuk konten milikmu sendiri atau yang diizinkan oleh pemiliknya.",
        "legal_names": {"terms": "Syarat Layanan", "privacy": "Kebijakan Privasi", "dmca": "DMCA", "contact": "Kontak"},
        "msgs": {
            "loading": "Mengambil info video…",
            "processing": "Memproses video. Video HD perlu digabung dulu, jadi bisa butuh beberapa detik.",
            "choose": "Pilih format:",
            "best": "MP4 Terbaik",
            "photo": "Foto",
            "photos": "Foto",
            "photos_h": "Foto di postingan ini:",
            "err_no_media": "Tidak ada video atau foto yang bisa diambil dari tautan ini. Pastikan postingannya publik.",
            "paste_manual": "Browser tidak mengizinkan membaca clipboard. Tempel manual di kotak.",
            "err_invalid": "Tautan tidak valid. Salin tautan video lalu tempel lagi.",
            "err_unsupported": "Tautan ini belum didukung. SimpanClip mendukung Facebook, Instagram, dan TikTok.",
            "err_private": "Video ini privat, butuh login, atau sudah dihapus. SimpanClip hanya bisa mengunduh video publik.",
            "err_too_long": "Video terlalu panjang atau terlalu besar untuk diproses.",
            "err_busy": "Server sedang ramai. Coba lagi beberapa saat.",
            "err_rate": "Terlalu banyak permintaan. Tunggu satu menit, lalu coba lagi.",
            "err_failed": "Gagal mengambil video. Cek tautannya atau coba lagi nanti.",
            "err_network": "Tidak bisa terhubung ke server. Periksa koneksi internetmu.",
        },
    },
    "en": {
        "brand_tag": "Save your favorite videos, free.",
        "nav_guide": "Guide",
        "other_lang": "ID",
        "ph": "Paste a video link here…",
        "paste": "Paste",
        "go": "Download",
        "supported": "Supported:",
        "steps_h": "How to download a video",
        "steps": [
            ("Copy the link", "Open the video in the app or browser, tap Share, then choose Copy link."),
            ("Paste it in SimpanClip", "Paste the link in the box above and press Download."),
            ("Save the video", "Pick the quality you want. The video is saved to your device."),
        ],
        "why_h": "Why SimpanClip",
        "why": [
            ("No install", "Works right in your browser on Android, iPhone, or computer."),
            ("No account", "No sign-up or login. Paste, choose, download."),
            ("Nothing stored", "Temporary files are deleted automatically within 10 minutes. We don't log your links."),
        ],
        "faq_h": "Frequently asked questions",
        "faq": [
            ("Is SimpanClip free?", "Yes. It is free and needs no account."),
            ("Which videos and photos can I download?", "Public videos and photos from Facebook, Instagram, and TikTok. Photo posts can't always be fetched, depending on the platform. Private content, videos that need a login, and live streams still in progress can't be downloaded."),
            ("How do I download on iPhone?", "Use Safari. When processing finishes, tap the download icon in Safari, then open the file in the Files app. From there you can share it or save it to Photos."),
            ("Can I download other people's videos?", "Only for personal use and with the owner's permission. Don't re-upload someone else's video as your own. You are responsible for how you use what you download."),
            ("Does SimpanClip store my videos?", "No. Files exist on the server only while your download is processed and are deleted automatically within 10 minutes. We have no accounts and don't log the links you paste."),
            ("Why did my download fail?", "Common causes: a wrong link, a private or deleted video, or the platform limiting access. Copy the link again, or try again in a few minutes."),
        ],
        "disclaimer": "SimpanClip is not affiliated with Facebook, Instagram, or TikTok. Use it only for content you own or have permission to save.",
        "legal_names": {"terms": "Terms of Service", "privacy": "Privacy Policy", "dmca": "DMCA", "contact": "Contact"},
        "msgs": {
            "loading": "Fetching video info…",
            "processing": "Processing the video. HD videos must be merged first, so it can take a few seconds.",
            "choose": "Choose a format:",
            "best": "MP4 Best",
            "photo": "Photo",
            "photos": "Photo",
            "photos_h": "Photos in this post:",
            "err_no_media": "No video or photo could be fetched from this link. Make sure the post is public.",
            "paste_manual": "Your browser won't let us read the clipboard. Paste into the box manually.",
            "err_invalid": "That link isn't valid. Copy the video link and paste it again.",
            "err_unsupported": "This link isn't supported yet. SimpanClip supports Facebook, Instagram, and TikTok.",
            "err_private": "This video is private, needs a login, or was removed. SimpanClip can only download public videos.",
            "err_too_long": "This video is too long or too large to process.",
            "err_busy": "The server is busy. Please try again shortly.",
            "err_rate": "Too many requests. Wait a minute and try again.",
            "err_failed": "Couldn't fetch the video. Check the link or try again later.",
            "err_network": "Can't reach the server. Check your internet connection.",
        },
    },
}

# halaman alat: kunci -> slug (sama di dua bahasa)
PLATFORMS = {
    "facebook": {
        "slug": "facebook-video-downloader",
        "name": "Facebook",
        "id": ("Unduh Video Facebook Gratis, Tanpa Aplikasi", "Unduh Video Facebook",
               "Simpan video publik Facebook ke ponsel atau komputer dalam format MP4. Tempel tautannya, pilih kualitas, selesai."),
        "en": ("Free Facebook Video Downloader, No App Needed", "Download Facebook Videos",
               "Save public Facebook videos to your phone or computer as MP4. Paste the link, pick a quality, done."),
    },
    "instagram": {
        "slug": "instagram-video-downloader",
        "name": "Instagram",
        "id": ("Unduh Video dan Reels Instagram Gratis", "Unduh Video Instagram",
               "Simpan video dan Reels publik Instagram ke perangkatmu. Tanpa aplikasi, tanpa login."),
        "en": ("Free Instagram Video and Reels Downloader", "Download Instagram Videos",
               "Save public Instagram videos and Reels to your device. No app, no login."),
    },
    "tiktok": {
        "slug": "tiktok-video-downloader",
        "name": "TikTok",
        "id": ("Unduh Video TikTok Gratis, Tanpa Aplikasi", "Unduh Video TikTok",
               "Simpan video publik TikTok ke ponselmu atau ambil audionya sebagai MP3."),
        "en": ("Free TikTok Video Downloader, No App Needed", "Download TikTok Videos",
               "Save public TikTok videos to your phone, or grab the audio as MP3."),
    },
}

HOME = {
    "id": ("SimpanClip: Unduh Video Facebook, Instagram, TikTok Gratis",
           "Simpan video favoritmu, gratis",
           "Tempel tautan video Facebook, Instagram, atau TikTok, pilih kualitas, lalu unduh. Tanpa aplikasi, tanpa akun."),
    "en": ("SimpanClip: Free Facebook, Instagram, TikTok Video Downloader",
           "Save your favorite videos, free",
           "Paste a Facebook, Instagram, or TikTok video link, pick a quality, and download. No app, no account."),
}

SLUGS = {  # halaman non-alat: kunci -> slug per bahasa
    "guide": {"id": "cara-download", "en": "how-to-download"},
    "terms": {"id": "syarat", "en": "terms"},
    "privacy": {"id": "privasi", "en": "privacy"},
    "dmca": {"id": "dmca", "en": "dmca"},
    "contact": {"id": "kontak", "en": "contact"},
}

GUIDE = {
    "id": ("Cara Download Video di Android, iPhone, dan PC", [
        ("Android", ["Salin tautan video dari aplikasi Facebook, Instagram, atau TikTok.", "Buka SimpanClip di Chrome, tempel tautan, lalu tekan Unduh.", "Pilih kualitas. File tersimpan di folder Download, dan muncul di Galeri atau aplikasi File."]),
        ("iPhone (iOS)", ["Gunakan Safari. Browser lain bisa gagal menyimpan file.", "Tempel tautan di SimpanClip, pilih kualitas, lalu ketuk Unduh.", "Ketuk ikon unduhan di pojok Safari, buka file di aplikasi Berkas, lalu ketuk Bagikan dan Simpan Video untuk memasukkannya ke Foto."]),
        ("Komputer (Windows, Mac, Linux)", ["Salin alamat video dari bilah alamat browser.", "Tempel di SimpanClip, pilih kualitas, lalu klik Unduh.", "File tersimpan di folder Download browser kamu."]),
    ], "Tips: video HD perlu waktu lebih lama karena gambar dan suara digabung dulu di server."),
    "en": ("How to Download Videos on Android, iPhone, and PC", [
        ("Android", ["Copy the video link from the Facebook, Instagram, or TikTok app.", "Open SimpanClip in Chrome, paste the link, and press Download.", "Pick a quality. The file is saved in your Downloads folder and shows up in Gallery or Files."]),
        ("iPhone (iOS)", ["Use Safari. Other browsers may fail to save the file.", "Paste the link in SimpanClip, choose a quality, and tap Download.", "Tap the download icon in Safari, open the file in the Files app, then tap Share and Save Video to add it to Photos."]),
        ("Computer (Windows, Mac, Linux)", ["Copy the video address from your browser's address bar.", "Paste it into SimpanClip, choose a quality, and click Download.", "The file is saved to your browser's Downloads folder."]),
    ], "Tip: HD videos take longer because picture and sound are merged on the server first."),
}

LEGAL = {
    "id": {
        "terms": ("Syarat Layanan", [
            "Terakhir diperbarui: 18 November 2026.",
            "## Penggunaan",
            "SimpanClip membantu kamu menyimpan video publik dari Facebook, Instagram, dan TikTok untuk penggunaan pribadi. Dengan memakai SimpanClip kamu setuju dengan syarat ini.",
            "## Hak cipta dan tanggung jawab kamu",
            "Video adalah milik pembuat atau pemegang haknya. Kamu hanya boleh mengunduh konten milikmu sendiri atau yang diizinkan pemiliknya. Dilarang mengunggah ulang, menjual, atau mengklaim video orang lain sebagai karyamu. Kamu bertanggung jawab penuh atas cara memakai hasil unduhan.",
            "## Yang tidak didukung",
            "Konten privat, konten berbayar, konten yang dilindungi DRM, dan akses otomatis massal (bot) dilarang. Kami berhak membatasi atau memblokir akses yang menyalahgunakan layanan.",
            "## Tanpa jaminan",
            "Layanan diberikan apa adanya. Platform sumber bisa mengubah sistemnya sewaktu-waktu sehingga unduhan bisa gagal tanpa pemberitahuan.",
            "## Afiliasi",
            "SimpanClip tidak berafiliasi dengan Meta, Facebook, Instagram, atau TikTok. Semua merek dagang milik pemiliknya masing-masing.",
        ]),
        "privacy": ("Kebijakan Privasi", [
            "Terakhir diperbarui: 18 November 2026.",
            "## Data yang kami proses",
            "Tautan video yang kamu tempel dikirim ke server kami hanya untuk mengambil video. Tautan itu tidak disimpan dan tidak dicatat dalam log. Kami tidak punya akun pengguna.",
            "## File sementara",
            "Video yang diproses disimpan sementara di server dan dihapus otomatis dalam 10 menit atau segera setelah selesai dikirim.",
            "## Data teknis",
            "Untuk mencegah penyalahgunaan, alamat IP dipakai sebentar di memori untuk membatasi jumlah permintaan dan tidak ditulis ke penyimpanan. Penyedia infrastruktur seperti Cloudflare dapat memproses data teknis sesuai kebijakan mereka.",
            "## Cookie dan iklan",
            "SimpanClip tidak memakai cookie pelacak sendiri. Jika iklan atau analitik ditambahkan, halaman ini akan diperbarui dengan penjelasannya.",
            "## Kontak",
            "Pertanyaan privasi dapat dikirim lewat halaman Kontak.",
        ]),
        "dmca": ("DMCA dan Permintaan Penghapusan", [
            "SimpanClip tidak menyimpan atau menayangkan video. Video diambil sementara dari platform sumber atas permintaan pengguna.",
            "Jika kamu pemegang hak cipta dan ingin tautan atau akun tertentu diblokir dari SimpanClip, kirim email ke hello@%DOMAIN% dengan: (1) tautan video asli, (2) bukti kamu pemegang hak atau wakilnya, (3) nama dan kontakmu, (4) pernyataan bahwa informasi tersebut benar.",
            "Kami akan meninjau dan menindaklanjuti permintaan yang lengkap secepat mungkin.",
        ]),
        "contact": ("Kontak", [
            "Pertanyaan, laporan error, atau permintaan penghapusan: hello@%DOMAIN%.",
            "Sertakan tautan video dan pesan error yang muncul agar kami bisa memeriksanya lebih cepat.",
        ]),
    },
    "en": {
        "terms": ("Terms of Service", [
            "Last updated: November 18, 2026.",
            "## Use of the service",
            "SimpanClip helps you save public videos from Facebook, Instagram, and TikTok for personal use. By using SimpanClip you agree to these terms.",
            "## Copyright and your responsibility",
            "Videos belong to their creators or rights holders. Only download content you own or have permission to save. Do not re-upload, sell, or claim someone else's video as your own. You are fully responsible for how you use what you download.",
            "## Not supported",
            "Private content, paid content, DRM-protected content, and bulk automated access (bots) are prohibited. We may limit or block access that abuses the service.",
            "## No warranty",
            "The service is provided as is. Source platforms can change at any time, so downloads may fail without notice.",
            "## Affiliation",
            "SimpanClip is not affiliated with Meta, Facebook, Instagram, or TikTok. All trademarks belong to their respective owners.",
        ]),
        "privacy": ("Privacy Policy", [
            "Last updated: November 18, 2026.",
            "## Data we process",
            "The video link you paste is sent to our server only to fetch the video. It is not stored or written to logs. We have no user accounts.",
            "## Temporary files",
            "Videos being processed are kept temporarily on the server and deleted automatically within 10 minutes, or right after delivery.",
            "## Technical data",
            "To prevent abuse, your IP address is held briefly in memory to rate-limit requests and is not written to storage. Infrastructure providers such as Cloudflare may process technical data under their own policies.",
            "## Cookies and ads",
            "SimpanClip sets no tracking cookies of its own. If ads or analytics are added, this page will be updated to explain them.",
            "## Contact",
            "Send privacy questions through the Contact page.",
        ]),
        "dmca": ("DMCA and Takedown Requests", [
            "SimpanClip does not store or display videos. Videos are fetched temporarily from the source platform at the user's request.",
            "If you are a copyright holder and want a specific link or account blocked from SimpanClip, email hello@%DOMAIN% with: (1) the link to the original video, (2) proof that you hold the rights or act for the holder, (3) your name and contact details, (4) a statement that the information is accurate.",
            "We will review complete requests and act on them as quickly as possible.",
        ]),
        "contact": ("Contact", [
            "Questions, error reports, or takedown requests: hello@%DOMAIN%.",
            "Include the video link and the error message you saw so we can check faster.",
        ]),
    },
}

# ---------------------------------------------------------------- template
PAGE = """<!doctype html>
<html lang="%%LANG%%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%TITLE%%</title>
<meta name="description" content="%%DESC%%">
<meta name="theme-color" content="#6C4DF6">
<link rel="canonical" href="https://%%DOMAIN%%%%PATH%%">
%%ALTS%%
<meta property="og:type" content="website">
<meta property="og:site_name" content="SimpanClip">
<meta property="og:title" content="%%TITLE%%">
<meta property="og:description" content="%%DESC%%">
<meta property="og:url" content="https://%%DOMAIN%%%%PATH%%">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Plus+Jakarta+Sans:wght@700;800&display=swap">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="brand" href="%%HOME%%">%%LOGO%%<span>simpanclip</span></a>
  <nav class="nav" aria-label="Menu">%%NAV%%<a class="lang" href="%%OTHER%%" hreflang="%%OTHERLANG%%">%%OTHERLABEL%%</a></nav>
</div></header>
<main>
%%MAIN%%
</main>
<footer class="site-footer"><div class="wrap">
  <div class="links">%%FLINKS%%</div>
  <p>%%DISCLAIMER%%</p>
  <p>&copy; 2026 SimpanClip</p>
</div></footer>
%%SCRIPTS%%
</body>
</html>
"""


def esc(s):
    return html.escape(s, quote=True)


def path_for(lang, slug):
    base = "/" if lang == "id" else "/en/"
    return base + (slug + "/" if slug else "")


def tool_slug(key):
    return "" if key == "home" else PLATFORMS[key]["slug"]


def page_slug(key, lang):
    if key == "home" or key in PLATFORMS:
        return tool_slug(key)
    return SLUGS[key][lang]


def all_pages():
    keys = ["home", *PLATFORMS, *SLUGS]
    return keys


def render_tool_main(lang, key):
    t = T[lang]
    if key == "home":
        _, h1, sub = HOME[lang]
    else:
        _, h1, sub = PLATFORMS[key][lang]
    steps = "".join(
        f'<div class="card"><div class="num">{i}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>'
        for i, (a, b) in enumerate(t["steps"], 1)
    )
    why = "".join(f'<div class="card"><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for a, b in t["why"])
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in t["faq"])
    return f"""<section class="hero"><div class="wrap">
  <h1>{esc(h1)}</h1>
  <p class="sub">{esc(sub)}</p>
  <form id="dl-form" class="tool" novalidate>
    <label class="sr" for="url">{esc(t['ph'])}</label>
    <div class="field">
      <input id="url" name="url" type="url" inputmode="url" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="{esc(t['ph'])}" required>
      <button type="button" id="paste" class="btn ghost">{esc(t['paste'])}</button>
    </div>
    <button type="submit" id="go" class="btn primary">{esc(t['go'])}</button>
  </form>
  <p class="supported">{esc(t['supported'])} <span class="chips">Facebook &middot; Instagram &middot; TikTok</span></p>
  <div id="status" role="status" aria-live="polite" class="status" hidden></div>
  <div id="result" class="result" hidden></div>
</div></section>
<section class="block"><div class="wrap"><h2>{esc(t['steps_h'])}</h2><div class="grid3">{steps}</div></div></section>
<section class="block"><div class="wrap"><h2>{esc(t['why_h'])}</h2><div class="grid3">{why}</div></div></section>
<section class="block"><div class="wrap"><h2>{esc(t['faq_h'])}</h2><div class="faq">{faq}</div></div></section>"""


def render_guide_main(lang):
    title, sections, tip = GUIDE[lang]
    body = "".join(
        f"<h2>{esc(name)}</h2><ol>{''.join(f'<li>{esc(s)}</li>' for s in steps)}</ol>"
        for name, steps in sections
    )
    return f'<article class="article"><h1>{esc(title)}</h1>{body}<p>{esc(tip)}</p></article>'


def render_legal_main(lang, key):
    title, lines = LEGAL[lang][key]
    out = [f"<h1>{esc(title)}</h1>"]
    for line in lines:
        line = line.replace("%DOMAIN%", DOMAIN)
        out.append(f"<h2>{esc(line[3:])}</h2>" if line.startswith("## ") else f"<p>{esc(line)}</p>")
    return f'<article class="article">{"".join(out)}</article>'


def meta_for(lang, key):
    if key == "home":
        return HOME[lang][0], HOME[lang][2]
    if key in PLATFORMS:
        return PLATFORMS[key][lang][0] + " | SimpanClip", PLATFORMS[key][lang][2]
    if key == "guide":
        return GUIDE[lang][0] + " | SimpanClip", GUIDE[lang][2]
    return LEGAL[lang][key][0] + " | SimpanClip", T[lang]["brand_tag"]


def build_page(lang, key):
    t = T[lang]
    other = "en" if lang == "id" else "id"
    slug = page_slug(key, lang)
    path = path_for(lang, slug)
    other_path = path_for(other, page_slug(key, other))
    title, desc = meta_for(lang, key)
    if key == "home" or key in PLATFORMS:
        main = render_tool_main(lang, key)
    elif key == "guide":
        main = render_guide_main(lang)
    else:
        main = render_legal_main(lang, key)
    nav = "".join(
        f'<a href="{path_for(lang, PLATFORMS[k]["slug"])}">{PLATFORMS[k]["name"]}</a>' for k in PLATFORMS
    ) + f'<a href="{path_for(lang, SLUGS["guide"][lang])}">{esc(t["nav_guide"])}</a>'
    flinks = "".join(
        f'<a href="{path_for(lang, SLUGS[k][lang])}">{esc(t["legal_names"][k])}</a>'
        for k in ("terms", "privacy", "dmca", "contact")
    )
    alts = (
        f'<link rel="alternate" hreflang="{lang}" href="https://{DOMAIN}{path}">\n'
        f'<link rel="alternate" hreflang="{other}" href="https://{DOMAIN}{other_path}">'
    )
    i18n = json.dumps(t["msgs"], ensure_ascii=False).replace("</", "<\\/")
    scripts = f'<script>window.SIMPANCLIP_I18N={i18n};</script>\n<script src="/config.js"></script>\n<script src="/app.js" defer></script>'
    out = PAGE
    for k, v in {
        "LANG": lang, "TITLE": esc(title), "DESC": esc(desc), "DOMAIN": DOMAIN, "PATH": path,
        "ALTS": alts, "LOGO": LOGO, "HOME": path_for(lang, ""), "NAV": nav, "OTHER": other_path,
        "OTHERLANG": other, "OTHERLABEL": t["other_lang"], "MAIN": main, "FLINKS": flinks,
        "DISCLAIMER": esc(t["disclaimer"]), "SCRIPTS": scripts,
    }.items():
        out = out.replace(f"%%{k}%%", v)
    return path, out


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    # Alamat API untuk produksi diisi lewat variabel SIMPANCLIP_API saat build
    # (contoh: https://api.simpanclip.com). Tanpa variabel, dipakai alamat lokal.
    api = os.environ.get("SIMPANCLIP_API", "http://localhost:8000").rstrip("/")
    with open(os.path.join(OUT, "config.js"), "w", encoding="utf-8") as f:
        f.write(f"window.SIMPANCLIP_API = {json.dumps(api)};\n")
    urls = []
    for lang in LANGS:
        for key in all_pages():
            path, content = build_page(lang, key)
            target = os.path.join(OUT, path.strip("/"), "index.html")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            urls.append(path)
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(build_page("id", "home")[1].replace("<title>", "<title>404 | ", 1))
    sm = "".join(f"<url><loc>https://{DOMAIN}{u}</loc></url>" for u in sorted(urls))
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n")
    print(f"OK: {len(urls)} halaman -> {OUT} (domain: {DOMAIN})")


if __name__ == "__main__":
    main()
