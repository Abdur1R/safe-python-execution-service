FROM python:3.10-slim

# Install dependencies for nsjail, NumPy, and user namespace mapping
RUN apt-get update && apt-get install -y \
    git build-essential wget python3-dev curl libcap2-bin \
    libprotobuf-dev protobuf-compiler pkg-config \
    libnl-3-dev libnl-route-3-dev flex bison \
    libgfortran5 uidmap \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir flask==2.3.3 numpy==1.26.4 pandas==2.2.2

# Install nsjail from source with patch for kafel
RUN git clone https://github.com/google/nsjail.git /nsjail && \
    cd /nsjail && \
    git checkout 3.0 && \
    git submodule update --init && \
    sed -i 's/YYUSE(/\/\/ YYUSE(/g' kafel/src/parser.y && \
    make && \
    mv nsjail /usr/local/bin/ && \
    chmod +x /usr/local/bin/nsjail && \
    cd .. && rm -rf /nsjail

# Create a non-root user and set up sandbox directory
RUN useradd -m -u 1000 sandboxuser && \
    mkdir -p /sandbox && \
    chown sandboxuser:sandboxuser /sandbox && \
    chmod 755 /sandbox && \
    # Create necessary directories for nsjail
    mkdir -p /tmp/nsjail && \
    chown sandboxuser:sandboxuser /tmp/nsjail && \
    chmod 755 /tmp/nsjail

# Switch to non-root user for running the application
USER sandboxuser

WORKDIR /app
COPY --chown=sandboxuser:sandboxuser . .

EXPOSE 8080
CMD ["python3", "app.py"]