# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy server code
COPY server.py .

# Expose the server port
EXPOSE 5000

# Command to run the server
CMD ["python", "server.py"]
