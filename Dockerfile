# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python scripts and requirements file to the container
COPY push_proxies.py proxy_provider.py monitor_proxies.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Create a script to run the Python script with environment variables
RUN echo '#!/bin/bash\n\
export BASE_URL=$BASE_URL\n\
export USERNAME=$USERNAME\n\
export PASSWORD=$PASSWORD\n\
/usr/local/bin/python /app/push_proxies.py >> /etc/push_proxies.log 2>&1' > /app/run_push_proxies.sh

# Make the script executable
RUN chmod +x /app/run_push_proxies.sh

# Create a cron job to run the Python script every 6 hours
RUN echo "0 */6 * * * root /app/run_push_proxies.sh" >> /etc/crontab

RUN chmod 0644 /etc/crontab

# Run the command on container startup
CMD ["cron", "-f"]
