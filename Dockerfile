# Use official Python image
FROM docker.io/python:slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt
# Copy applicatpion code
COPY . .

# Create a non-root user and switch to it
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose Flask port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:5000/health || exit 1
# Run the Flask app
CMD ["flask", "run"]