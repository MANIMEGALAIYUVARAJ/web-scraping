# -----------------------------
# Base Image
# -----------------------------
FROM python:3.10-slim

# -----------------------------
# Environment
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV TZ=UTC

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    libxkbcommon0 \
    libglib2.0-0 \
    ca-certificates \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Google Chrome (modern way)
# -----------------------------
RUN mkdir -p /etc/apt/keyrings && \
    wget -q https://dl.google.com/linux/linux_signing_key.pub -O /etc/apt/keyrings/google-linux-signing-key.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Workdir
# -----------------------------
WORKDIR /app

# -----------------------------
# Python deps
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy app
# -----------------------------
COPY . .

# -----------------------------
# Runtime dirs
# -----------------------------
RUN mkdir -p output temp_profiles temp_fallback_profiles scraped_csvs

# -----------------------------
# Port
# -----------------------------
EXPOSE 61631

# -----------------------------
# Start Flask + Xvfb
# -----------------------------
CMD ["bash", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python app.py"]
