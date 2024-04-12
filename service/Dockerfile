FROM python:3.11-slim

# Set working directory
WORKDIR /usr/src/

# Install system dependencies
RUN apt update && apt upgrade -y

# Add server files
COPY . .

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt


CMD [ "python", "-m" , "flask", "--app=tts_service", "run", "--host=0.0.0.0", "--port=5005", "--debug"]
