FROM python:3.11

ENV JUPYTER_PORT=8888

WORKDIR /app

# Requirements
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# JupyterLab configuration
COPY jupyter_lab_config.py ./jupyter_lab_config.py
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Ports
EXPOSE ${JUPYTER_PORT}

# Add a non-root account for the user
RUN useradd -ms /bin/bash user

# Copy sample notebook and clear output
COPY notebook.ipynb /home/user/
RUN jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace /home/user/notebook.ipynb
RUN chown user:user /home/user/notebook.ipynb

# Run as non-root user
USER user
CMD ["jupyter-lab", "--no-browser", "--config=jupyter_lab_config.py"]
