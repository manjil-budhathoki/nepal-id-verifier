# 1. Base Image
FROM python:3.10-slim

# 2. Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 3. Install System Dependencies
# - build-essential: For compiling Python wheels
# - libglib2.0-0: Core OS dependency for image processing
# - libgl1: The graphic library OpenCV is screaming for
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Set Work Directory
WORKDIR /app

# 5. Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy the Application Code
COPY . .

# 7. Create directories
RUN mkdir -p /app/debug_crops /app/models

# 8. Expose Port
EXPOSE 8000

# 9. Start Command
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "1", "--timeout", "120", "--bind", "0.0.0.0:8000", "app.main:app"]