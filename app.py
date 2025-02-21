import os
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO

app = Flask(__name__)

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
        return jsonify({'error': f'Failed to retrieve formats: {e.stderr}'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form.get('url')
    itag = request.form.get('itag')
    format_type = request.form.get('format')

    try:
        temp_file = f"downloads/temp_file.{format_type}"

        # Download selected format
        subprocess.run(['yt-dlp', '-f', itag, '-o', temp_file, video_url], check=True)

        return send_file(temp_file, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to download: {e.stderr}'})
    except Exception as e:
        return jsonify({'error': str(e)})

    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    app.run(debug=True)
