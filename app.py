import os
import subprocess
import time
import threading
from flask import Flask, render_template, request, send_file, jsonify, Response

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Ensure the downloads folder exists

@app.route('/')
def index():
    """Render the main HTML page with the input form."""
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    video_url = request.form.get('url')

    try:
        # Fetch available formats using yt-dlp
        result = subprocess.run(['yt-dlp', '-F', video_url], text=True, capture_output=True, check=True)

        formats = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) > 3 and parts[0].isdigit():
                itag = parts[0]
                ext = parts[1]
                resolution = parts[2] if "x" in parts[2] else "audio only"
                details = ' '.join(parts[3:])

                # Collect MP3 options and MP4 video qualities
                if ext == "m4a":
                    formats.append({'itag': itag, 'type': 'mp3', 'quality': '128kbps' if '128k' in details else '320kbps'})
                elif ext == "mp4" and "x" in resolution:
                    formats.append({'itag': itag, 'type': 'mp4', 'quality': resolution})

        return jsonify({'title': 'YouTube Video', 'formats': formats})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to retrieve formats: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    itag = request.form.get('itag')
    format_type = request.form.get('format')
    # Just accept the timestamp parameter, no need to use it
    timestamp = request.form.get('timestamp')
    
    # Rest of your function remains the same...

    try:
        # Get the video title for naming
        title_result = subprocess.run(
            ['yt-dlp', '--get-title', video_url],
            text=True, capture_output=True, check=True
        )
        video_title = title_result.stdout.strip().replace(" ", "_").replace("/", "_")

        # Construct the filename
        filename = f"{video_title}.{format_type}"
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        # Run yt-dlp to download the file
        if format_type == "mp4":
            command = ['yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', '-o', file_path, video_url]
        else:
            command = ['yt-dlp', '-f', itag, '-o', file_path, video_url]

        print("Running command:", " ".join(command))
        subprocess.run(command, check=True)

        # Ensure proper mimetype for downloads
        mimetype = "audio/mpeg" if format_type == "mp3" else "video/mp4"

        # Ensure the browser always asks where to save the file
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )

        # Delete file in a separate thread **AFTER** sending
        def delete_file():
            time.sleep(5)  # Wait for the browser to finish downloading
            try:
                os.remove(file_path)
                print(f"✅ Deleted file: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete file {file_path}: {e}")

        threading.Thread(target=delete_file, daemon=True).start()

        print(f"✅ Sending file: {filename}")
        return response

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to download video: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
