# Base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY nlp_service.py .

# Run the app
CMD ["uvicorn", "nlp_service:app", "--host", "0.0.0.0", "--port", "8000"]