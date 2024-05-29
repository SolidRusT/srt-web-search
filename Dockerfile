# Base image
FROM python:3.11-slim-bookworm

# Initialize working directory
COPY . /src
WORKDIR /src

# Install APT dependencies and clean up
RUN apt update && apt install -y \
  git make cmake \
  build-essential \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip3 install --upgrade --no-cache-dir pip \
  && pip3 install --no-cache-dir wheel setuptools

## Just for Llama CPP Python provider dependency
# Clone llama-cpp repository and install
RUN git clone https://github.com/ggerganov/llama.cpp.git \
  && cd llama.cpp \
  && mkdir build \
  && cd build \
  && cmake .. -DBUILD_PYTHON=ON \
  && make -j4 \
  && make install

# Install app dependencies
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Copy config-example.yaml to config.yaml if it doesn't exist
RUN if [ ! -f config.yaml ]; then \
  cp config-example.yaml config.yaml && \
  echo "Default configuration file created: config.yaml"; \
  else \
  echo "Configuration file found: config.yaml"; \
  fi

# Configure default service settings
ENV PERSONA="Default"
ENV PORT=8650
ENV SERVER_NAME="0.0.0.0"

# Run the service
CMD ["python3", "main.py", "--mode", "chat", "--interface", "gradio"]
