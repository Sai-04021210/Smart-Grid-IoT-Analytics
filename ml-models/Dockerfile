FROM python:3.11.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directories for models
RUN mkdir -p /app/models/lstm /app/models/forecasting /app/models/optimization

# Create non-root user
RUN useradd --create-home --shell /bin/bash mluser \
    && chown -R mluser:mluser /app
USER mluser

# Default command
CMD ["python", "train_models.py"]
