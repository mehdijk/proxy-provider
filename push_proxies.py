import os
import asyncio
import requests
import base64
import logging
from proxy_provider import ProxyProvider

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PushProxies:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def get_connector_info(self):
        credentials = f"{self.username}:{self.password}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{self.base_url}/api/scraper/project", headers=headers)
        if response.status_code == 200:
            project_info = response.json()
            return project_info.get("connectorDefaultId")
        else:
            logger.error(f"Failed to get project information. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None

    def remove_proxies(self, connector_uuid, duplicate=False, only_offline=False):
        credentials = f"{self.username}:{self.password}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()
        endpoint = f"{self.base_url}/api/scraper/project/connectors/{connector_uuid}/freeproxies/remove"
        payload = {}
        if duplicate:
            payload["duplicate"] = True
        if only_offline:
            payload["onlyOffline"] = True
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/json"
        }
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 204:
            logger.info("Proxies removed successfully.")
        else:
            logger.error(f"Failed to remove proxies. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")

    def add_proxies(self, connector_uuid, proxies):
        credentials = f"{self.username}:{self.password}"
        credentials_encoded = base64.b64encode(credentials.encode()).decode()
        endpoint = f"{self.base_url}/api/scraper/project/connectors/{connector_uuid}/freeproxies"
        payload = []
        for proxy in proxies:
            proxy_payload = {
                "key": f"{proxy['ip']}:{proxy['port']}",
                "type": proxy['type'],
                "address": {
                    "hostname": proxy['ip'],
                    "port": proxy['port']
                }
            }
            payload.append(proxy_payload)
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/json"
        }
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 204:
            logger.info(f"{len(proxies)} proxies added successfully.")
        else:
            logger.error(f"Failed to add proxies. Status code: {response.status_code}")
            logger.error(f"Response content: {response.text}")

async def fetch_good_proxies():
    provider = ProxyProvider()
    working_proxies = await provider.checkProxies()
    return working_proxies

if __name__ == "__main__":
    # Load credentials and base URL from environment variables
    base_url = os.getenv("BASE_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    if not all([base_url, username, password]):
        logger.error("Please set BASE_URL, USERNAME, and PASSWORD environment variables.")
        exit(1)

    push_proxies = PushProxies(base_url, username, password)
    connector_uuid = push_proxies.get_connector_info()
    
    if connector_uuid:
        logger.info("UUID of the project: %s", connector_uuid)
        proxies = asyncio.run(fetch_good_proxies())
        if proxies:
            push_proxies.add_proxies(connector_uuid, proxies)
            push_proxies.remove_proxies(connector_uuid, duplicate=True)
    else:
        logger.error("Failed to retrieve project UUID.")
