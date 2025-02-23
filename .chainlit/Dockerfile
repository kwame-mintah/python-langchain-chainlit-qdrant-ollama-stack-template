ARG BASE_IMAGE=python:3.11.6-slim-bullseye
FROM --platform=linux/amd64 $BASE_IMAGE

# Set working directory as `/code/`
WORKDIR /code

# Copy python modules used within application
COPY ../requirements.txt /code/requirements.txt

# Install all python modules, keep image as small as possible
# don't store the cache directory during install
RUN pip install --upgrade pip && \
    pip install --no-build-isolation --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code to `/code/app/`
COPY ../main.py /code/app/
COPY ../config.py /code/app/
COPY ../.chainlit/chainlit.md /code/
COPY ../.chainlit /code/.chainlit

# Start chainlit application
# https://docs.chainlit.io/backend/command-line
CMD ["chainlit", "run", "--host", "0.0.0.0", "--port", "8000", "/code/app/main.py"]
