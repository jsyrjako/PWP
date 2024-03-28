
from flask import Flask, request, jsonify, send_from_directory, url_for
from queue import Queue
from threading import Thread
import os
import torch
import uuid
from TTS.api import TTS

app = Flask(__name__)
config_path = "config.json"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Create a queue to handle multiple requests
queue = Queue()

def generate_voice_with_tts(text, filename,  model="tts_models/multilingual/multi-dataset/xtts_v2", language="en"):
    tts = TTS(model).to(device)
    filepath = os.path.join('static', filename)
    tts.tts_to_file(text=text, file_path=filepath, save_format="wav")
    return filepath


def worker():
    while True:
        item = queue.get()
        if item is None:
            break
        text, filename = item
        generate_voice_with_tts(text, filename)
        queue.task_done()


Thread(target=worker, daemon=True).start()

@app.route('/generate_voice', methods=['POST'])
def generate_voice_route():

    text = request.json.get('text')
    filename = f"{uuid.uuid4}.wav"
    file_url = url_for('download', filename=filename, _external=True)
    queue.put((text, filename))

    return jsonify({'message': 'Your request has been added to the queue and will be processed soon.', 'file_url': file_url})

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='static', filename=filename)

if __name__ == '__main__':
    app.run(port=5005, debug=True)
