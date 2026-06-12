# single image with all capabilities

# Use 'devel' image so CUDA headers are available for faiss-gpu compilation.
# 'runtime' lacks the compiler/headers needed to build CUDA extensions.
FROM docker.io/nvidia/cuda:12.1.0-devel-ubuntu22.04

LABEL maintainer="Molecular Spectroscopy Project"
LABEL description="Molecular Spectroscopy Project"

# Set non-interactive mode and UTF-8 encoding
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV MOD_INSTALL_PREFIX=/usr/local \
    LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH} \
    PYTHONPATH=/usr/local/lib/python3.10/site-packages:${PYTHONPATH} \
    PATH=/usr/local/bin:${PATH}

# Install system dependencies including MOD build requirements
RUN apt-get update \
    && apt-get install --no-install-recommends -y software-properties-common \
    && add-apt-repository universe \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
    python3.10 \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    ca-certificates \
    graphviz \
    graphviz-dev \
    libboost-all-dev \
    libgraphviz-dev \
    pkg-config \
    autoconf \
    automake \
    libtool \
    swig \
    apt-utils \
    librsvg2-dev \
    libpango1.0-dev \
    vim \
    less \
    coinor-libcbc-dev \
    libopenbabel-dev \
    python3-openbabel \
    gawk \
    lmodern \
    pdf2svg \
    texlive-latex-extra \
    texlive-pictures \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

ARG j=7

# Graphviz
WORKDIR /opt/graphviz
RUN \
    wget http://graphviz.gitlab.io/pub/graphviz/stable/SOURCES/graphviz.tar.gz \
    && tar -xf graphviz.tar.gz --one-top-level=graphviz --strip-components=1   \
    && cd graphviz                                                             \
    && ./configure                                                             \
    && make -j $j                                                              \
    && make install                                                            \
    && cd ..                                                                   \
    && rm -rf /opt/graphviz


# the folder can apparently not be called just 'boost', therefore 'boostDir'
WORKDIR /opt/boostDir
RUN wget                                                                   \
    https://archives.boost.io/release/1.76.0/source/boost_1_76_0.tar.gz       \
    -O boost.tar.gz
RUN \
    tar -xf boost.tar.gz --one-top-level=boostSrc --strip-components=1        \
    && cd boostSrc                                                            \
    && ./bootstrap.sh --with-python=python3                                   \
    && ./b2 --with-python --with-graph --with-iostreams --with-test -j $j     \
    && ./b2 install                                                           \
    && cd ..                                                                  \
    && rm -rf /opt/boostDir

RUN git clone \
        --branch v1.0.0 \
        --recurse-submodules \
        https://github.com/jakobandersen/mod.git /opt/mod \
    && cd /opt/mod \
    && git submodule update --init --recursive  \
    # bootstrap.sh generates CMakeFiles.txt and other files that cmake needs.
    # MOD's own error message explicitly requires this step.
    && ./bootstrap.sh

WORKDIR /opt/mod
RUN pip3 install -r requirements.txt \
    && bindep -b testing | tr '\n' ' ' | xargs apt-get install --no-install-recommends -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mod/build
RUN cmake ../ \
        -DBUILD_DOC=no \
        -DWITH_GUROBI=no \
        -DWITH_CPLEX=no \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_MODULE_LINKER_FLAGS="-flto=$j" \
        -DCMAKE_SHARED_LINKER_FLAGS="-flto=$j" \
        -DBUILD_TESTING=on \
    && make -j $j \
    && make tests -j $j \
    && make install \
    && cp -a ../examples/py /examples \
    && ctest -j $j --output-on-failure -E cmake_ \
    && rm -rf /opt/mod   # safe to delete: install prefix is /usr/local, not /opt/mod

RUN pip3 install --no-cache-dir  openbabel
RUN git clone https://github.com/forlilab/bottchscore.git /opt/bottchscore
ENV PYTHONPATH=/opt/bottchscore:${PYTHONPATH}

# --- Application setup --------------------------------------------------------------

WORKDIR /app

# Copy application source
COPY src/ src/

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r src/container/requirements.txt

# Set Python path for module resolution
ENV PYTHONPATH=/app:/usr/local/lib/python3.10/site-packages:${PYTHONPATH}

# Create necessary output directories
RUN mkdir -p /app/outputs/{logs,metrics,plots,checkpoints,best_params}

RUN chmod +x /app/src/container/entrypoint.sh

# Create a dedicated user and hand over ownership of the app directory.
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser && \
    chown -R appuser:appgroup /app /examples
USER appuser


ENTRYPOINT ["/app/src/container/entrypoint.sh"]
CMD ["help"]
