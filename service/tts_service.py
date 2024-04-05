from flask import Flask, request, jsonify, send_from_directory, url_for
from queue import Queue
from threading import Thread
import os
import torch
import uuid
from TTS.api import TTS

app = Flask(__name__)
conf_path = "config.json"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Create a queue to handle multiple requests
queue = Queue()


def generate_voice_with_tts(
    text, filename, model="tts_models/en/ljspeech/tacotron2-DDC", language="en"
):
    if not os.path.exists("static"):
        os.makedirs("static")

    tts = TTS(model_name=model, progress_bar=False).to(device)
    filepath = os.path.join("static", filename)

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


@app.route("/generate_voice/", methods=["POST"])
def generate_voice_route():
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.wav"
    file_url = url_for("download", filename=filename, _external=True)

    print(f"Adding: {text} | to with filename: {filename}")

    queue.put((text, filename))
    return jsonify(
        {
            "message": "Your request has been added to the queue and will be processed soon.",
            "file_url": file_url,
        }
    )


@app.route("/download/<filename>/", methods=["GET"])
def download(filename):
    print(f"Downloading: {filename}")
    if not os.path.join("static", filename):
        return jsonify({"error": "File not found or not yet ready"}), 404

    return send_from_directory(directory="static", path=filename)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
