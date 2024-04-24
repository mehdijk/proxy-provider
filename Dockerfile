# Use an official Python runtime as a base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Python scripts and requirements file to the container
COPY push_proxies.py proxy_provider.py requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Create a cron job to run the Python script every 1 hour
RUN echo "0 * * * * root BASE_URL=http://93.186.251.59:8890 USERNAME=26cqm6gfmykqdrkqrzhrq PASSWORD=yglcntjavqp5ccuggqvh6r /usr/local/bin/python /app/push_proxies.py >> /etc/mycronlog.log 2>&1" >> /etc/crontab
RUN chmod 0644 /etc/crontab

# Run the command on container startup
CMD ["cron", "-f"]
