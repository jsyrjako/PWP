FROM python:3.12-slim

ARG entry="./docker-entrypoint-dev.sh"

# Set working directory
WORKDIR /usr/src/

# Install system dependencies
RUN apt update && apt upgrade -y

# Add server files
COPY . .

RUN chmod +x $entry

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

ENTRYPOINT [ $entry ]