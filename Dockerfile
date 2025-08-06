FROM runpod/base:0.6.3-cuda11.8.0

# Set python3.11 as the default python
RUN ln -sf $(which python3.11) /usr/local/bin/python && \
    ln -sf $(which python3.11) /usr/local/bin/python3

# Install system dependencies for llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for llama-cpp-python compilation
ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
ENV FORCE_CMAKE=1

# Install dependencies
COPY requirements.txt /requirements.txt
RUN uv pip install --upgrade -r /requirements.txt --no-cache-dir --system

# Create directory for models cache
RUN mkdir -p /runpod-volume/models

# Add application files
COPY config.py .
COPY cache_manager.py .
COPY model_manager.py .
COPY inference_engine.py .
COPY handler.py .

# Set working directory
WORKDIR /

# Run the handler
CMD python -u /handler.py
