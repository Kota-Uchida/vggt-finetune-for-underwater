# Use NVIDIA's official CUDA image as the base
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

# Create a non-root user and set the user ID and group ID
ARG USER=user
ARG UID=1000
ARG GID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Base packages, user, sudo
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo ca-certificates tzdata locales \
 && locale-gen en_US.UTF-8 \
 && update-locale LANG=en_US.UTF-8 \
 && groupadd -g ${GID} ${USER} \
 && useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USER} \
 && echo "${USER}:${USER}" | chpasswd \
 && usermod -aG sudo ${USER} \
 && echo "${USER} ALL=(ALL:ALL) NOPASSWD:ALL" >> /etc/sudoers \
 && rm -rf /var/lib/apt/lists/*

ENV USER=$USER

# XDG runtime dir
ENV XDG_RUNTIME_DIR=/tmp/runtime
RUN mkdir -p /tmp/runtime && chown ${UID}:${GID} /tmp/runtime && chmod 700 /tmp/runtime

# Dev tools and libraries (no OpenCV from source)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg2 lsb-release apt-utils \
    build-essential cmake pkg-config \
    libgtest-dev libeigen3-dev libboost-all-dev \
    qtbase5-dev qt5-qmake libglew-dev \
    git libyaml-cpp-dev \
    vim unzip rsync software-properties-common \
    # OpenCV (Ubuntu packages)
    libopencv-dev \
    python3-opencv \
    # PCL
    libpcl-dev \
 && rm -rf /var/lib/apt/lists/*

# Python 3.11 (keep system Python 3.8 for python3-opencv)
RUN add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-dev python3.11-distutils python3.11-venv \
    python3.8 python3.8-venv \
 && rm -rf /var/lib/apt/lists/*

# pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Make Python 3.11 default while keeping 3.8 available
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 2 && \
    update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3 2

# Optional: Python OpenCV wheel for Python 3.11 (so cv2 works in 3.11 too)
# If you prefer to rely ONLY on system OpenCV for Python (3.8), comment this out.
RUN python3.11 -m pip install --no-cache-dir opencv-python

################################################################################
# Install protobuf 3.13.0 from source (unchanged)
################################################################################
RUN apt-get update && apt-get remove -y libprotobuf-dev protobuf-compiler \
 && apt-get install -y --no-install-recommends autoconf automake libtool \
 && curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v3.13.0/protobuf-cpp-3.13.0.tar.gz \
 && tar -xvf protobuf-cpp-3.13.0.tar.gz \
 && cd protobuf-3.13.0 \
 && ./autogen.sh && ./configure \
 && make -j"$(nproc)" && make install && ldconfig \
 && cd .. \
 && rm -rf protobuf-cpp-3.13.0.tar.gz protobuf-3.13.0/ \
 && rm -rf /var/lib/apt/lists/*

# PyTorch + extras (CUDA wheel will match the base CUDA where possible)
# RUN pip3 install --no-cache-dir torch torchvision torchaudio
RUN pip3 install --no-cache-dir --pre \
    torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0  \
     --index-url https://download.pytorch.org/whl/cu124


# Because of the build error, I temporally commented out the following line.
#RUN pip3 install --no-cache-dir numba open3d

# Switch to the non-root user
USER ${USER}
WORKDIR /home/${USER}/data
RUN mkdir -p /home/${USER}/data

CMD ["/bin/bash"]
