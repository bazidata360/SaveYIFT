from flask import Flask, render_template, request, Response,send_from_directory
import yt_dlp
import requests
import io
import os
import re
import unicodedata
from datetime import datetime

app = Flask(__name__)

# ======================
# Helper Functions
# ======================

def sanitize_filename(filename):
    """Convert to ASCII and clean special characters"""
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    filename = re.sub(r'[^\w\s-]', '', filename).strip()
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename[:100]  # Limit length

def safe_content_disposition(filename):
    """Generate safe Content-Disposition header"""
    safe_name = sanitize_filename(filename)
    try:
        return f"attachment; filename*=UTF-8''{safe_name}.mp4"
    except:
        return f"attachment; filename={safe_name}.mp4"

def follow_redirect(url):
    """Follow the redirection from a shortened TikTok URL."""
    response = requests.get(url, allow_redirects=True)
    return response.url  # Returns the final URL after redirection

# ======================
# Instagram Functions
# ======================

def get_instagram_info(url):
    """Extract information from Instagram video"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.instagram.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Instagram Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'uploader': info.get('uploader', 'Instagram User'),
                'url': url,
                'platform': 'instagram'
            }
    except Exception as e:
        raise Exception(f"Failed to get Instagram info: {str(e)}")

def download_instagram_video(url):
    """Download the Instagram video"""
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.instagram.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'overwrites': True,
            'noplaylist': True
        }

        buffer = io.BytesIO()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as f:
                buffer.write(f.read())
            os.unlink(filename)

            buffer.seek(0)
            return buffer, sanitize_filename(info.get('title', 'instagram_video'))

    except Exception as e:
        raise Exception(f"Failed to download Instagram video: {str(e)}")

# ======================
# Facebook Functions
# ======================

def get_facebook_info(url):
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.facebook.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Facebook Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'uploader': info.get('uploader', 'Facebook User'),
                'url': url,
                'platform': 'facebook'
            }
    except Exception as e:
        raise Exception(f"Failed to get Facebook info: {str(e)}")

def download_facebook_video(url):
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.facebook.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'overwrites': True,
            'noplaylist': True
        }

        buffer = io.BytesIO()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as f:
                buffer.write(f.read())
            os.unlink(filename)

            buffer.seek(0)
            return buffer, sanitize_filename(info.get('title', 'facebook_video'))

    except Exception as e:
        raise Exception(f"Failed to download Facebook video: {str(e)}")

# ======================
# YouTube Functions
# ======================

COOKIES_FILE = "cookies.txt"  # Make sure this file exists in the same directory

def get_youtube_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'cookiefile': COOKIES_FILE  # Add cookies to authenticate
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'No title'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'views': info.get('view_count', 0),
            'uploader': info.get('uploader', 'Unknown'),
            'url': url,
            'platform': 'youtube'
        }

def download_youtube_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Select best available format
        'quiet': True,
        # 'cookiefile': COOKIES_FILE
    }

    buffer = io.BytesIO()

    def progress_hook(d):
        if d['status'] == 'finished':
            with open(d['filename'], 'rb') as f:
                buffer.write(f.read())
            os.unlink(d['filename'])

    ydl_opts['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        buffer.seek(0)
        return buffer, info['title']


# ======================
# TikTok Functions
# ======================

def is_valid_tiktok_url(url):
    """Check if URL is a valid TikTok URL"""
    patterns = [
        r'https?://(www\.|m\.|vm\.)?tiktok\.com/@[^/]+/video/\d+',
        r'https?://(www\.|m\.|vm\.)?tiktok\.com/t/[a-zA-Z0-9]+',
        r'https?://(www\.|m\.|vm\.)?tiktok\.com/video/\d+',
        r'https?://vm\.tiktok\.com/[a-zA-Z0-9]+',
        r'https?://vt\.tiktok\.com/[a-zA-Z0-9]+'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

def get_tiktok_info(url):
    try:
        if 'vt.tiktok.com' in url:
            url = follow_redirect(url)

        if not is_valid_tiktok_url(url):
            raise Exception("Invalid TikTok URL format")

        ydl_opts = {
            'quiet': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.tiktok.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'TikTok Video'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'views': info.get('view_count', 0),
                'uploader': info.get('uploader', 'TikTok User'),
                'url': url,
                'platform': 'tiktok'
            }
    except Exception as e:
        raise Exception(f"Failed to get TikTok info: {str(e)}")

def download_tiktok_video(url):
    try:
        if 'vt.tiktok.com' in url:
            url = follow_redirect(url)

        if not is_valid_tiktok_url(url):
            raise Exception("Invalid TikTok URL format")

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'force_generic_extractor': True,
            'referer': 'https://www.tiktok.com/',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'overwrites': True,
            'noplaylist': True
        }

        buffer = io.BytesIO()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as f:
                buffer.write(f.read())
            os.unlink(filename)

            buffer.seek(0)
            return buffer, sanitize_filename(info.get('title', 'tiktok_video'))

    except Exception as e:
        raise Exception(f"Failed to download TikTok video: {str(e)}")

# ======================
# Main Routes
# ======================

@app.route('/')
def home():
    return render_template('index.html', current_year=datetime.now().year)

@app.route('/tiktok')
def tiktok_home():
    return render_template('tiktok.html', current_year=datetime.now().year)

@app.route('/facebook')
def facebook_home():
    return render_template('facebook.html', current_year=datetime.now().year)

@app.route('/instagram')
def instagram_home():
    return render_template('instagram.html', current_year=datetime.now().year)

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', current_year=datetime.now().year)

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory(os.path.abspath(os.getcwd()), 'ads.txt')



@app.route('/search', methods=['POST'])
def search():
    url = request.form['video_url']
    platform = detect_platform(url)

    try:
        if platform == 'youtube':
            video = get_youtube_info(url)
            return render_template('results.html', video=video, current_year=datetime.now().year)
        elif platform == 'tiktok':
            video = get_tiktok_info(url)
            return render_template('tiktok_results.html', video=video, current_year=datetime.now().year)
        elif platform == 'facebook':
            video = get_facebook_info(url)
            return render_template('facebook_results.html', video=video, current_year=datetime.now().year)
        elif platform == 'instagram':
            video = get_instagram_info(url)
            return render_template('instagram_results.html', video=video, current_year=datetime.now().year)
        else:
            return "Platform not supported yet!"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/download', methods=['POST'])
def download():
    url = request.form['video_url']
    platform = detect_platform(url)

    try:
        if platform == 'youtube':
            buffer, title = download_youtube_video(url)
            return Response(
                buffer,
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': safe_content_disposition(title),
                    'Content-Type': 'video/mp4'
                }
            )
        elif platform == 'tiktok':
            buffer, title = download_tiktok_video(url)
            return Response(
                buffer,
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': safe_content_disposition(f"tiktok_{title}"),
                    'Content-Type': 'video/mp4'
                }
            )
        elif platform == 'facebook':
            buffer, title = download_facebook_video(url)
            return Response(
                buffer,
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': safe_content_disposition(f"facebook_{title}"),
                    'Content-Type': 'video/mp4'
                }
            )
        elif platform == 'instagram':
            buffer, title = download_instagram_video(url)
            return Response(
                buffer,
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': safe_content_disposition(f"instagram_{title}"),
                    'Content-Type': 'video/mp4'
                }
            )
        else:
            return "Platform not supported yet!"
    except Exception as e:
        return f"Error: {str(e)}"

def detect_platform(url):
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    elif 'instagram.com' in url:
        return 'instagram'
    else:
        return 'unknown'

@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'active_page': request.path
    }

if __name__ == '__main__':
    app.run(debug=True)
