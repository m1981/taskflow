# syntax=docker/dockerfile:1.4

FROM python:3.9-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY req.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install streamlit==1.41.1
RUN pip install --no-cache-dir -r req.txt

# Add this line to ensure streamlit is in PATH
ENV PATH="/usr/local/bin:$PATH"

# Testing stage
FROM base AS testing
WORKDIR /app

COPY req_tests.txt /app/
RUN pip install --no-cache-dir -r req_tests.txt

# Copy the entire project structure
COPY . /app

WORKDIR /app
