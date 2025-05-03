# Step 1: Use the official Python 3.11 slim image as base
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Install dependencies for running Selenium (we need Chrome and ChromeDriver)
# Install required system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ca-certificates \
    chromium \
    chromium-driver \
    libx11-xcb1 \
    libfontconfig1 \
    libxrender1 \
    libjpeg62-turbo \
    libgsf-1-114 \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Install Chrome dependencies for running headless Chrome
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libappindicator3-1 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libnss3 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libgtk-3-0 \
    libgbm1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the rest of the application code into the container
COPY ./app ./app

# Step 7: Set environment variable to use headless Chrome
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Step 8: Set the default command to run the FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
