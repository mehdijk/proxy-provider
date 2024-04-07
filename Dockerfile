# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python scripts and requirements file to the container
COPY push_proxies.py proxy_provider.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV BASE_URL="http://host.docker.internal:8890"
ENV USERNAME="ndloqy2c0df6njvp7333"
ENV PASSWORD="qr3mhcy7tghf64osi5zr"

# Run the Python script when the container launches
CMD ["python", "push_proxies.py"]
