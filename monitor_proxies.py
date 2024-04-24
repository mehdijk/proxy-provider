from datetime import datetime
import os
import time
import requests
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitorProxies:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def get_connector_and_proxies(self):
        credentials = f"{self.username}:{self.password}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{self.base_url}/api/scraper/project/connectors", headers=headers)
        if response.status_code == 200:
            project_info = response.json()
            return project_info
        else:
            logger.error(f"Failed to get project connectors. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None

    def process_proxies(self, connectors_info, max_age_minutes, max_requests):
        selected_fields = ['id', 'connectorId', 'fingerprintError', 'createdTs', 'requests']
        all_proxies = []
        current_time = time.time() * 1000  # Convert current time to milliseconds
        print(current_time)
        for connector_info in connectors_info:
            proxies = connector_info.get("proxies", [])
            for proxy in proxies:
                # Filter conditions
                if proxy.get('fingerprintError') is not None \
                        and proxy.get('requests') <= max_requests \
                        and proxy.get('createdTs') <= current_time - (max_age_minutes * 60 * 1000):
                    proxy_data = {field: proxy.get(field) for field in selected_fields}
                    all_proxies.append(proxy_data)
        return all_proxies
    
    def remove_filtered_proxies(self, filtered_proxies):
        credentials = f"{self.username}:{self.password}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()
        endpoint = f"{self.base_url}/api/scraper/project/proxies/remove"
        payload = [{"id": proxy["id"], "force": True} for proxy in filtered_proxies]
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/json"
        }
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 204:
            logger.info("Filtered proxies removed successfully.")
        else:
            logger.error(f"Failed to remove filtered proxies. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")


if __name__ == "__main__":
    # Load credentials and base URL from environment variables
    base_url = os.getenv("BASE_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not all([base_url, username, password]):
        logger.error("Please set BASE_URL, USERNAME, and PASSWORD environment variables.")
        exit(1)

    monitor_proxies = MonitorProxies(base_url, username, password)
    connectors_info = monitor_proxies.get_connector_and_proxies()

    if connectors_info:
        logger.info("Connectors and proxies information retrieved successfully.")
        proxies = monitor_proxies.process_proxies(connectors_info,5,0)
        logger.info("Number of proxies to remove: %s", len(proxies))
        if len(proxies)> 0:
            monitor_proxies.remove_filtered_proxies(proxies)
    else:
        logger.error("Failed to retrieve connectors and proxies information.")
