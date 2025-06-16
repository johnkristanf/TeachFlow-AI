# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the app port
EXPOSE 8000

# Ensure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

# Set entrypoint from /app
ENTRYPOINT ["./entrypoint.sh"]