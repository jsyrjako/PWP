# Bikinghub Client

This is the client for the Bikinghub project. It is a simple command line interface that allows the user to interact with the Bikinghub API.

All the dependencies are listed in the [`requirements.txt`](./requirements.txt) file.

## Installation

### Create and activate Virtual Environment
```bash
python -m venv venv
```

Linux / macOS
```bash
source venv/bin/activate
```

Windows (CMD)
```bash
venv\Scripts\activate.bat
```

Windows (PowerShell)
```bash
venv\Scripts\Activate.ps1
```

### Install the required dependencies

```bash
pip install -r requirements.txt
```

## Run the Project

```bash
python ./app.py
```

## Development

### Linting

Using Pylint linter (With some disabled warnings per course instructions)

```bash
pylint .\app.py .\client.py --disable=no-member,import-outside-toplevel,no-self-use
```

### Formatting

Using Black formatter

```bash
black .
```
