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

# 3. Dive into the folder where scrapy.cfg actually lives
WORKDIR /app/spider20

EXPOSE 6800

# 4. Wipe local caches in this specific folder and run Scrapyd
CMD ["sh", "-c", "rm -rf dbs eggs && scrapyd --pidfile= --http_port=6800"]