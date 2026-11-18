# SimpanClip

Website pengunduh video publik (Facebook, Instagram, TikTok). Dibuat berdasarkan PRD SimpanClip.

```
simpanclip/
├── frontend/          situs statis (HTML/CSS/JS), dibuat oleh build.py
│   ├── build.py       generator 18 halaman (Indonesia + Inggris)
│   └── static/        styles.css, app.js, config.js, logo, PWA
├── backend/           API FastAPI + yt-dlp + ffmpeg (Docker)
├── docker-compose.yml backend + Caddy (HTTPS otomatis)
├── Caddyfile
└── .env.example
```

## 1. Jalankan di laptop dulu

Syarat: Python 3.11+, ffmpeg, Docker (opsional).

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ALLOWED_ORIGINS=http://localhost:8080 uvicorn main:app --port 8000
```

Cek: buka http://localhost:8000/health, harus keluar `{"ok":true,...}`.

**Frontend** (terminal lain)

```bash
cd frontend
python build.py
cd dist && python -m http.server 8080
```

Buka http://localhost:8080, tempel tautan video publik, lalu coba unduh.
`static/config.js` sudah menunjuk ke `http://localhost:8000`.

## 2. Naik ke internet

Urutannya: domain → server backend → frontend → hubungkan. Ada 4 akun yang kamu butuhkan:
penyedia domain, Cloudflare, GitHub, dan penyedia server (VPS).

### a. Beli domain dan pasang di Cloudflare
1. Beli domain (misal `simpanclip.com`) di Niagahoster, Rumahweb, atau Namecheap. Cek dulu domain dan nama merek belum dipakai orang lain.
2. Daftar di cloudflare.com, pilih **Add a site**, masukkan domain, pilih paket Free.
3. Ganti nameserver di penyedia domain ke dua nameserver yang diberikan Cloudflare. Tunggu aktif (biasanya kurang dari 1 jam, kadang sampai 24 jam).

### b. Siapkan server backend (VPS)
1. Sewa VPS Ubuntu 22.04/24.04 dengan RAM minimal 2 GB (DigitalOcean, Contabo, IDCloudHost, dll).
2. Masuk lewat SSH, lalu pasang Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. Di Cloudflare → DNS, tambah record **A**: nama `api`, isi IP VPS. Untuk pertama kali, pilih **DNS only** (awan abu-abu) supaya Caddy bisa mengambil sertifikat.
4. Salin folder proyek ke server (`git clone` dari repo kamu, atau `scp -r simpanclip user@IP:~`).
5. Di server:
   ```bash
   cd simpanclip
   cp .env.example .env
   nano .env          # isi API_DOMAIN dan ALLOWED_ORIGINS dengan domain kamu
   docker compose up -d --build
   ```
6. Cek `https://api.domainkamu/health`. Jika muncul `{"ok":true,...}`, backend sudah hidup.
7. Aktifkan firewall: izinkan hanya port 22, 80, 443 (`ufw allow 22,80,443/tcp && ufw enable`).

### c. Naikkan frontend ke Cloudflare Pages
1. Edit `frontend/static/config.js`: ganti isinya menjadi `window.SIMPANCLIP_API = "https://api.domainkamu";`
2. Taruh proyek di repo GitHub.
3. Di Cloudflare → **Workers & Pages** → **Create** → **Pages** → hubungkan repo GitHub.
4. Isi pengaturan build:
   - Root directory: `frontend`
   - Build command: `SIMPANCLIP_DOMAIN=domainkamu.com python build.py`
   - Build output directory: `dist`
5. Setelah deploy, buka **Custom domains** di proyek Pages, tambahkan `domainkamu.com` dan `www.domainkamu.com`.

Alternatif tanpa GitHub: jalankan `SIMPANCLIP_DOMAIN=domainkamu.com python build.py` di laptop, lalu unggah folder `frontend/dist` lewat **Direct Upload** di Cloudflare Pages.

### d. Cek akhir
- Buka situs di ponsel Android dan iPhone (Safari), uji satu tautan dari tiap platform.
- Ganti email `hello@domainkamu` di halaman Kontak dan DMCA: siapkan alamat email itu (misal lewat Cloudflare Email Routing yang gratis).
- Pantau uptime di uptimerobot.com dengan alamat `https://api.domainkamu/health`.

## 3. Perawatan rutin

- **Perbarui yt-dlp**: platform sering mengubah sistemnya. Dengan `AUTO_UPDATE_YTDLP=1`, yt-dlp diperbarui tiap container dijalankan ulang. Jadwalkan restart mingguan:
  ```bash
  crontab -e
  0 4 * * 1  cd ~/simpanclip && docker compose restart backend
  ```
- **Log**: akses log dimatikan (`--no-access-log`) agar tautan pengguna tidak tercatat. Jangan menyalakan log akses di Caddy.
- **Permintaan DMCA**: balas cepat, dan blokir tautan atau akun yang dilaporkan.
- **Server dibatasi**: jika IP server mulai diblokir platform, unduhan akan gagal. Ini risiko bawaan layanan seperti ini (lihat PRD bagian 10).

## 4. Pengaturan penting (environment backend)

| Variabel | Bawaan | Fungsi |
| --- | --- | --- |
| `ALLOWED_ORIGINS` | `http://localhost:8080` | Situs yang boleh memanggil API |
| `MAX_DURATION` | 1800 | Batas durasi video (detik) |
| `MAX_FILESIZE_MB` | 500 | Batas ukuran file |
| `MAX_HEIGHT` | 1080 | Resolusi tertinggi yang ditawarkan |
| `MAX_CONCURRENT` | 3 | Unduhan bersamaan |
| `INFO_LIMIT` / `DOWNLOAD_LIMIT` | 20 / 8 | Batas permintaan per menit per IP |
| `TRUST_PROXY` | 0 | Isi 1 jika di belakang Caddy/Cloudflare |

## 5. Catatan

- Hanya konten publik. Video privat atau butuh login memang tidak didukung.
- Syarat layanan, privasi, dan DMCA di situs ini adalah draf awal, bukan nasihat hukum. Tinjau dengan ahli hukum sebelum peluncuran publik.
- Iklan belum dipasang. Banyak jaringan iklan menolak situs pengunduh video, jadi cek kebijakan mereka dulu sebelum mendaftar.
