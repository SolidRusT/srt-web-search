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

# Run the App
CMD ["python3", "main.py"]
