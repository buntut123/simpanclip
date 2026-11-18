#!/bin/sh
# yt-dlp sering perlu diperbarui karena platform mengubah sistemnya.
if [ "$AUTO_UPDATE_YTDLP" = "1" ]; then
  pip install -U --quiet --user yt-dlp || echo "update yt-dlp dilewati"
fi
# --no-access-log: tautan video yang diminta tidak ikut tercatat di log.
exec uvicorn main:app --host 0.0.0.0 --port 8000 --no-access-log
