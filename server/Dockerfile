FROM python:3.11

WORKDIR /app

# Requirements
COPY requirements.txt ./
RUN pip install -r requirements.txt --no-cache-dir

COPY *.py .

# Ports
EXPOSE 5000

CMD [ "python", "main.py" ]