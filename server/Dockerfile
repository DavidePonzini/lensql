FROM python:3.11

WORKDIR /app

# Requirements
COPY *.py .
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY docker-compose.yml ./

# Ports
EXPOSE 5000

CMD [ "python", "main.py" ]