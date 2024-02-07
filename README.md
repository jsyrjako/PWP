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


# Database
We are using SQLite3 for our database. The database is created by running the command `flask init-db` and populated by running the command `flask populate-db`. The database is populated with some random data to make testing easier. The database is located in the file `instance/development.db`.

### Create database

```bash
flask init-db
```

### Populate database

```bash
flask populate-db
```


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


