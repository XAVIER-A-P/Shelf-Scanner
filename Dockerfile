# Use offical lightweight Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose 
EXPOSE 8000

# Run the application with Uvicorn (Production Server)
# Host 0.0.0.0 is required for Docker containers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]