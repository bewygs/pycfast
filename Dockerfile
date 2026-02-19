# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install CFAST
RUN wget https://github.com/firemodels/cfast/releases/latest/download/CFAST_Linux.tar.gz -O /tmp/CFAST_Linux.tar.gz && \
    tar -xzf /tmp/CFAST_Linux.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/cfast && \
    rm /tmp/CFAST_Linux.tar.gz

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the PyCFAST source code into the container
COPY ./src/pycfast /app/src/pycfast

# Set the default command to run when the container starts
CMD ["python"]