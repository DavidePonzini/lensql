FROM python:3.11

WORKDIR /sql_tutor

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jupyter_lab_config.py ./jupyter_lab_config.py

EXPOSE 8888

# Add a non-root user
RUN useradd -ms /bin/bash jupyter
COPY py /home/jupyter/py

# Run as non-root user
USER jupyter
CMD ["jupyter-lab", "--no-browser", "--config=jupyter_lab_config.py"]
