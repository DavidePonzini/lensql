FROM python:3.11

ARG USERNAME=user
ARG OPENAI_API_KEY

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV JUPYTER_PORT=8888

WORKDIR /lensql

# Install requirements
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Jupyter Lab configuration
COPY jupyter_lab_config.py ./jupyter_lab_config.py

# Disable Jupyter Lab announcements
RUN jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# Ports
EXPOSE ${JUPYTER_PORT}

# Non-root user
RUN useradd -ms /bin/bash ${USERNAME}
COPY lensql/* /home/${USERNAME}/
COPY notebook.ipynb /home/${USERNAME}/

# Run as non-root user
USER ${USERNAME}
CMD ["jupyter-lab", "--no-browser", "--config=jupyter_lab_config.py"]
