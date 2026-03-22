# Dockerfile for web3-security-scout
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy source
COPY src ./src
COPY tests ./tests
COPY data ./data

CMD ["pytest", "--cov=src", "-v", "tests/"]