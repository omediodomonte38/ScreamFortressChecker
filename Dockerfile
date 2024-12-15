# Start with the official Python 3.12 image
FROM python:3.12-slim-bookworm


# Install 'uv' via pip
RUN pip install --no-cache-dir uv

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml file to the working directory
COPY pyproject.toml /app/

# Install dependencies using uv
RUN uv pip install --system --requirements pyproject.toml

