import yt_dlp
import os
from config import DOWNLOAD_DIR, BASE_DIR

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

TIKTOK_COOKIES = os.path.join(BASE_DIR, "tiktok_cookies.txt")

def _add_cookies(opts: dict, url: str) -> dict:
    if 'tiktok.com' in url and os.path.exists(TIKTOK_COOKIES):
        opts['cookiefile'] = TIKTOK_COOKIES
    return opts

def get_info(url: str) -> dict:
    opts = _add_cookies({'quiet': True, 'skip_download': True}, url)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Без названия'),
            'duration': info.get('duration', 0),
            'uploader': info.get('uploader', ''),
        }

def download_audio(url: str) -> str:
    opts = _add_cookies({
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True,
    }, url)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename.rsplit('.', 1)[0] + '.mp3'

def download_video(url: str) -> str:
    opts = _add_cookies({
        'format': 'best[filesize<50M]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'quiet': True,
    }, url)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)