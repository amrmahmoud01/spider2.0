FROM python:3.11-slim

WORKDIR /app

# Install native dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 1. Copy and install requirements from the absolute root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of the project files
COPY . .

# 3. Create a dedicated healthcheck script file
RUN echo "import urllib.request; urllib.request.urlopen('http://localhost:6800/daemonstatus.json')" > /app/healthcheck.py

# 4. Dive into the folder where scrapy.cfg actually lives
WORKDIR /app/spider20

# ... (rest of your Dockerfile remains the same) ...

EXPOSE 6800

# Set the binding environment variable so it listens on all interfaces
ENV SCRAPYD_BIND_ADDRESS=0.0.0.0

# Keep the CMD clean and simple
CMD ["scrapyd", "--pidfile", "/tmp/scrapyd.pid"]