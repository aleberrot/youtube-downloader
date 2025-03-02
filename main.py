import os
from flask import Flask, request, jsonify, send_from_directory, after_this_request
import yt_dlp
from flask_cors import CORS
import base64
import urllib.parse
import time
import threading

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "static")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER

cookies_base64 = os.getenv("COOKIES_BASE64")
if cookies_base64:
    with open("/tmp/cookies.txt", "wb") as f:
        f.write(base64.b64decode(cookies_base64))
else:
    print("Warning: No cookies found. Some videos may not be downloadable.", flush=True)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    quality = data.get('quality')
    print("Checking if cookies.txt exists:", os.path.exists("/tmp/cookies.txt"), flush=True)

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received request: URL={url}, Quality={quality}", flush=True)
    def send_response(file_name):
        file_url = f"{request.host_url}static/{urllib.parse.quote(file_name)}"
        print(f"File available at: {file_url}")
        response = jsonify({"fileUrl": file_url, "fileName": file_name})
        return response

    thread = threading.Thread(target=download_video, args=(url, quality, format, send_response))
    thread.start()

    return jsonify({"message": "Download started"}), 202


@app.route("/static/<path:filename>")
def serve_file(filename):
    """Serve a file from the download directory and delete it after sending it"""

    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    # Clean up the downloaded file after serving
    @after_this_request
    def cleanup(response):
        try:
            os.remove(file_path)
            print(f"Removed file: {file_path}", flush=True)
        except Exception as e:
            print(f"Error removing file: {str(e)}", flush=True)
        return response

    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/status', methods=['GET'])
def status():
    """Check the status of a download"""

def download_video(url, quality, format, callback):
    """Download the video asynchronously"""
     # Set up the download path
    download_path = DOWNLOAD_FOLDER
    os.makedirs(download_path, exist_ok=True)  # Ensure directory exists

    # Configure yt-dlp options
    ydl_opts = {
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
        "cookiefile": "/tmp/cookies.txt",
    }

    # Adjust options based on format and quality
    if format == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
        ydl_opts["postprocessors_args"] = ["-vn"]
        ydl_opts["noplaylist"] = True
        ydl_opts["keepVideo"] = False
    elif format == "video":
        ydl_opts["format"] = f"best[height={quality}]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_ext = "mp3" if format == "audio" else info.get("ext", "mp4")
            file_name = f"{info['title']}.{file_ext}"
            file_path = os.path.join(download_path, file_name)


        callback(file_name)
    except Exception as e:
        print(f"Download error: {str(e)}", flush=True)


if __name__ == '__main__':
    app.run(debug=True)

    