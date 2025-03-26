FROM python:3.11

ARG USERNAME=user
ARG OPENAI_API_KEY

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV JUPYTER_PORT=8888

WORKDIR /lensql

# Requirements
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# JupyterLab configuration
COPY jupyter_lab_config.py ./jupyter_lab_config.py
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Ports
EXPOSE ${JUPYTER_PORT}

# Add a non-root account for the user
RUN useradd -ms /bin/bash ${USERNAME}

# Copy sample notebook
COPY notebook.ipynb /home/${USERNAME}/
RUN chown ${USERNAME}:${USERNAME} /home/${USERNAME}/notebook.ipynb

# Run as non-root user
USER ${USERNAME}
CMD ["jupyter-lab", "--no-browser", "--config=jupyter_lab_config.py"]
