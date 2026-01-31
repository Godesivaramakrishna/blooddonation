# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Cloud Run
EXPOSE 8080

# Use Gunicorn to run Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]