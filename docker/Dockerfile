FROM python:3.11

ARG USERNAME=user
ARG OPENAI_API_KEY
ARG LENSQL_LOGGER_HOST
ARG LENSQL_LOGGER_PORT
ARG LENSQL_LOGGER_DBNAME
ARG LENSQL_LOGGER_USER
ARG LENSQL_LOGGER_PASSWORD

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV JUPYTER_PORT=8888
ENV LENSQL_LOGGER_HOST=${LENSQL_LOGGER_HOST}}
ENV LENSQL_LOGGER_PORT=${LENSQL_LOGGER_PORT}
ENV LENSQL_LOGGER_DBNAME=${LENSQL_LOGGER_DBNAME}
ENV LENSQL_LOGGER_USER=${LENSQL_LOGGER_USER}
ENV LENSQL_LOGGER_PASSWORD=${LENSQL_LOGGER_PASSWORD}

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
