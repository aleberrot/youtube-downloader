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

    app.logger.info(f"Received request: URL={url}, Quality={quality}")

    try:
            yt = YouTube(url)

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
            app.logger.info(f"File downloaded to: {file_path}") # Log the full path

            # Crucial: Add mimetype and handle potential errors during send_file
            try:
                return send_file(file_path, as_attachment=True, mimetype=stream.mime_type)
            except Exception as e:
                app.logger.info(f"Error sending file: {e}")
                return jsonify({"error": "Error sending file"}), 500

    except Exception as e:
        app.logger.info(f"Download error: {str(e)}") # Log the error for debugging
        return jsonify({"error": f"Download failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)


"""
from flask import Flask,  request, jsonify, send_file
from pytubefix import YouTube
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    format = data.get('format')
    quality = data.get('quality')
    download_path = "/home/aleberot/mysite/downloads"

    if not url:
        return jsonify({"error": "No url provided"}), 400

    app.logger.info(f"Received request: URL={url}, Quality={quality}")

    try:
        yt = YouTube(url)
        if format == 'video':
            stream = yt.streams.filter(res=quality,progressive=True, file_extension="mp4").first()
            if not stream:
                return jsonify({"error": "Quality not available"}), 400
            if not os.path.exists(download_path):
                os.makedirs(download_path)
        elif format == 'audio':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            return 'Invalid format', 400

        file_path = stream.download(output_path=download_path)
        app.logger.info(f"File downloaded somewhere :/ {file_path} ")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f'Error: {str(e)}'



if __name__ == '__main__':
    app.run(debug=True)

"""