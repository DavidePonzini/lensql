FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

# Requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app/server/

# Ports
EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout=120", "server.run:app"]
