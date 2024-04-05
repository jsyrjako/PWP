
# Auxiliary service

This Python server provides a Text-to-Speech (TTS) service using Flask and the TTS library.
It exposes two endpoints:
- generating voice from text
- downloading the generated voice file.

## Usage

### Generate Voice

Send a POST request to the `/generate_voice/` endpoint with a JSON body containing a "text" field. The service will add your request to a queue and process it in the background. The response will include a URL where you can download the generated voice file once it's ready.

Example request:

```sh
curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello, world!"}' http://localhost:5005/generate_voice/
```

### Download Voice File

Once your voice file is ready, you can download it by sending a GET request to the `/download/<filename>/` endpoint, where `<filename>` is the name of the file you want to download.

Example request:

```sh
curl -O http://localhost:5005/download/12345678-1234-1234-1234-123456789abc.wav
```

## Installation

### Requirements

This service requires Python <=3.11.

#### Virtual Environment

Create a virtual environment, run:

```sh
python -m venv venv
```

Activate the virtual environment, run:

Linux / macOS
```bash
source venv/bin/activate
```
or on Windows (CMD)
```bash
venv\Scripts\activate.bat
```
or on Windows (PowerShell)
```bash
venv\Scripts\Activate.ps1
```


### Dependencies

To install the required dependencies, run:

```sh
pip install -r requirements.txt
```


## Running the Service

To start the service, simply run the script:

```sh
python tts_service.py
```

The service will start on port 5005


## Note

This service uses a queue to handle multiple requests and a separate worker thread to process the requests in the background. This means that even if the service receives many requests at once, it will be able to handle them without becoming unresponsive (though text processing increases file generation time).
