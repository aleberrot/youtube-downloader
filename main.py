import os
from flask import Flask, request, jsonify, send_file
import yt_dlp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    quality = data.get('quality')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received request: URL={url}, Quality={quality}", flush=True)

    # Set up the download path
    download_path = os.path.join(os.path.expanduser("~"), "downloads")
    os.makedirs(download_path, exist_ok=True)  # Ensure directory exists

    # Configure yt-dlp options
    ydl_opts = {
        "outtmpl": f"{download_path}/%(title)s.%(ext)s",
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

        # Send the file back to the client
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        print(f"Download error: {str(e)}", flush=True)
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)



"""
Previous approach using pytubefix

import os
from flask import Flask, request, jsonify, send_file
from pytubefix import YouTube
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    quality = data.get('quality')

    if not url:
        return jsonify({"error": "No url provided"}), 400

    print(f"Received request: URL={url}, Quality={quality}", flush=True)

    try:
            yt = YouTube(url, use_po_token=True)

            if format == 'video':
                stream = yt.streams.filter(res=quality, progressive=True, file_extension="mp4").first()
                if not stream:
                    return jsonify({"error": "Video quality not available"}), 400
            elif format == 'audio':
                stream = yt.streams.filter(only_audio=True).first()
                if not stream:
                    return jsonify({"error": "Audio stream not found"}), 400
            else:
                return jsonify({"error": "Invalid format"}), 400

            # Use a path within your home directory (PythonAnywhere best practice)
            download_path = os.path.join(os.path.expanduser("~"), "downloads")  # Correct path
            os.makedirs(download_path, exist_ok=True)  # exist_ok prevents errors if dir exists

            file_path = stream.download(output_path=download_path)
            print(f"File downloaded to: {file_path}", flush=True) # Log the full path

            # Crucial: Add mimetype and handle potential errors during send_file
            try:
                return send_file(file_path, as_attachment=True, mimetype=stream.mime_type)
            except Exception as e:
                print(f"Error sending file: {e}", flush=True)
                return jsonify({"error": "Error sending file"}), 500

    except Exception as e:
        print(f"Download error: {str(e)}", flush=True) # Log the error for debugging
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
"""