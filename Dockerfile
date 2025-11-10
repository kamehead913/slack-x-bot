# Use official Python runtime
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy dependency list
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose the port Cloud Run expects
ENV PORT 8080
EXPOSE 8080

# Start the app
CMD exec gunicorn main:app --bind :$PORT --workers 1 --threads 8 --timeout 0
