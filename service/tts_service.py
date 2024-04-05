"""
This module creates a Flask server to generate voice from text using TTS.
"""

from queue import Queue
from threading import Thread
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, url_for
import torch
from TTS.api import TTS

app = Flask(__name__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Create a queue to handle multiple requests
queue = Queue()


def worker():
    """
    Worker function to process the queue and generate audio for each item.
    """
    while True:
        item = queue.get()
        if item is None:
            break
        text, filename = item
        generate_voice_with_tts(text, filename)
        queue.task_done()


# Start the worker thread
Thread(target=worker, daemon=True).start()


def generate_voice_with_tts(
    text, filename, model="tts_models/en/ljspeech/tacotron2-DDC"
):
    """
    Generate voice with TTS model and save it to a file.
    :param text: The text to generate audio for
    :param filename: The filename to save the audio to
    :param model: The TTS model to use (default: tacotron2-DDC)
    """

    if not os.path.exists("static"):
        os.makedirs("static")

    tts = TTS(model_name=model, progress_bar=False).to(device)
    filepath = os.path.join("static", filename)

    tts.tts_to_file(text=text, file_path=filepath, save_format="wav")
    return filepath


@app.route("/generate_voice/", methods=["POST"])
def generate_voice_route():
    """
    Route to generate voice from text.
    Expects a JSON payload with a "text" key and POST method.
    """
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.wav"
    file_url = url_for("download", filename=filename, _external=True)
    # print(f"Adding: {text} | to with filename: {filename}")

    queue.put((text, filename))
    return jsonify(
        {
            "message": "Your request has been added to the queue and will be processed soon.",
            "file_url": file_url,
        },
        202,
    )


@app.route("/download/<filename>/", methods=["GET"])
def download(filename):
    """
    Route to download the generated audio file.
    Expects a filename and GET method.
    """
    if not os.path.exists(os.path.join("static", filename)):
        return jsonify({"error": "File not found or not yet ready"}), 404

    return send_from_directory(directory="static", path=filename)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
