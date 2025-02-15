import os
from flask import Flask, request, jsonify, send_file
import yt_dlp
from flask_cors import CORS
import base64
import mimetypes

app = Flask(__name__)
CORS(app)

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

    # Set up the download path
    download_path = os.path.join(os.path.expanduser("~"), "downloads")
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
    elif format == "video":
        ydl_opts["format"] = f"best[height={quality}]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_ext = "mp3" if format == "audio" else info.get("ext", "mp4")
            file_name = f"{info['title']}.{file_ext}"
            file_path = os.path.join(download_path, file_name)

        print(f"File downloaded to: {file_path}", flush=True)

        mime_type, _ = mimetypes.guess_type(file_path)
        # Send the file back to the client
        return send_file(file_path, as_attachment=True, mimetype=mime_type)
    except Exception as e:
        print(f"Download error: {str(e)}", flush=True)
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)

    