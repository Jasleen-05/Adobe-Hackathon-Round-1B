# Use a slim Python 3.10 base image for a smaller footprint
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download nltk punkt data
RUN python -m nltk.downloader punkt

# Copy only the source code directory
COPY src/ ./src/

# Ensure input and output directories exist (created at runtime via volume mounts)
RUN mkdir -p /app/input /app/output

# Set the command to run the analyzer script
CMD ["python", "src/analyzer.py"]