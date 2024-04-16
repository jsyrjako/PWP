"""
This module creates a Flask server to generate voice from text using TTS.
"""

from queue import Queue
from threading import Thread
from datetime import datetime
import os
import uuid
import json
import requests
from flask import Flask, request, jsonify, send_from_directory, url_for, Response
import torch
from TTS.api import TTS

BIKINGHUB_API = "http://localhost:5000/api"

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

    Parameters:
    text (str): The text to generate audio for
    filename (str): The filename to save the audio to
    model (str): The TTS model to use (default: tacotron2-DDC)
    """

    if not os.path.exists("static"):
        os.makedirs("static")

    tts = TTS(model_name=model, progress_bar=False).to(device)
    filepath = os.path.join("static", filename)

    tts.tts_to_file(text=text, file_path=filepath, split_sentences=False)
    return filepath


def get_weather_from_api(location_id):
    """
    Fetches weather description from the bikinghub service.

    Parameters:
    location_id (int): The location id to fetch weather description for
    """
    weather_endpoint = f"{BIKINGHUB_API}/locations/{location_id}/weather/"
    sess = requests.Session()

    try:
        resp = sess.get(f"{weather_endpoint}")
        json_resp = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"An error occurred: {e}")
        return None

    formatted_weather = format_weather(json_resp.get("items", {}))
    print(f"Formatted weather: {formatted_weather}")
    return formatted_weather


def format_weather(weather_json):
    """
    Converts the weather JSON response to a formatted string.
    :param weather_json: The weather JSON response
    """
    # remove location_id from the weather_json
    weather_json.pop("location_id", None)
    parsed_time = parse_datetime(weather_json.get("weather_time"))
    try:
        weather_json["weather_time"] = parsed_time
    except KeyError as e:
        print(f"An error occurred: {e}")
        weather_json["weather_time"] = None

    formatted_dict = {
        key.replace("_", " "): value for key, value in weather_json.items()
    }
    formatted_string = ", ".join(
        f"{key}: {value}" for key, value in formatted_dict.items()
    )

    formatted_string = (
        formatted_string.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    )
    for key, value in formatted_dict.items():
        if isinstance(value, float):
            formatted_string = formatted_string.replace(
                f"{key}: {value}", f"{key}: {value:.1f}"
            )

    return formatted_string


def parse_datetime(datetime_str):
    """
    Parses the datetime string to a formatted string for voice generation.

    Parameters:
    datetime_str (str): The datetime string to parse
    """
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    formatted_time = dt.strftime("%d %B %Y at %H")
    return formatted_time


@app.route("/generate_voice/", methods=["POST"])
async def generate_voice():
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
    return Response(
        json.dumps(
            {
                "message": "Your request has been added to the queue and will be processed soon.",
                "href": file_url,
            },
        ),
        status=202,
        mimetype="application/json",
    )


@app.route("/weather_voice/<int:location_id>/", methods=["GET"])
async def generate_voice_weather(location_id):
    """
    Route to generate voice from weather description.
    Fetches weather description from the bikinghub service and generates voice.

    Parameters:
    location_id (int): The location id to fetch weather description for
    """
    text = get_weather_from_api(location_id)
    if not text:
        return jsonify({"error": "No text provided"}), 400

    filename = f"{uuid.uuid4()}.wav"
    file_url = url_for("download", filename=filename, _external=True)
    # print(f"Adding: {text} | to with filename: {filename}")

    queue.put((text, filename))
    return Response(
        json.dumps(
            {
                "message": "Your request has been added to the queue and will be processed soon.",
                "href": file_url,
            },
        ),
        status=202,
        mimetype="application/json",
    )


@app.route("/download/<path:filename>/", methods=["GET"])
def download(filename):
    """
    Route to download the generated audio file.
    Expects a filename and GET method.

    Parameters:
    filename (str): The filename to download
    """
    if not os.path.exists(os.path.join("static", filename)):
        return jsonify({"error": "File not found or not yet ready"}), 404

    return send_from_directory(directory="static", path=filename)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
