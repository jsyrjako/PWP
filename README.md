# PWP SPRING 2024

# PROJECT NAME

# Group information

| Name             | Student ID | Email                      |
| ---------------- | ---------- | -------------------------- |
| Janne Yrjänäinen | Y58554010  | jyrjanai20@student.oulu.fi |
| Joona Syrjäkoski | Y58172266  | jsyrjako20@student.oulu.fi |
| Joonas Ojanen    | 2305882    | jojanen20@student.oulu.fi  |
| Lasse Rapo       | Y58553703  | lrapo20@student.oulu.fi    |

**Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client**


## Virtual environment
### Create virtual environment

```bash
python3 -m venv venv
```

### Activate virtual environment

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

### Deactivate virtual environment

```bash
deactivate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Database
We are using SQLite3 for our database. The database is created by running the command `flask init-db` and populated by running the command `flask populate-db`. The database is populated with some random data to make testing easier. The development database is located in the file `instance/development.db`.

### Create database

```bash
flask --app bikinghub init-db
```

### Populate database

```bash
flask --app bikinghub populate-db
```


## Run the Project

Add MML_API_KEY to the [constants.py](./bikinghub/constants.py) file. MML_API_KEY is required to fetch the data from the Maanmittauslaitos API.

```python
MML_API_KEY = ""
```

Run the project with the following command:

```bash
flask --app bikinghub run
```

or with docker

```bash
docker-compose up
```

## Testing

### Run tests

Run all tests

```bash
pytest
```

Run tests with coverage

```bash
pytest --cov-report term-missing --cov=bikinghub
```


## Development

### Linting

Using Pylint linter

```bash
pylint bikinghub
```

### Formatting

Using Black formatter

```bash
black .
```

### API Keys for different services

#### Creating and managing API keys for Maanmittauslaitos

Creating and managing API keys
You can create an API key in the Maanmittauslaitoksen OmaTili-service as follows:

1. Register for [OmaTili](https://omatili.maanmittauslaitos.fi/user/new/avoimet-rajapintapalvelut).
2. Log in with the user name you have registered.

After registering and logging in, you can:
- create an API key by registering with your personal account.
- edit your details or delete your username.
