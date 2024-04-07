import asyncio
import requests
import base64

from proxy_provider import ProxyProvider

def get_connector_info(username, password):
    credentials = f"{username}:{password}"
    credentials_encoded = base64.b64encode(credentials.encode()).decode()
    base_url = "http://localhost:8890/api/scraper/project"
    headers = {
        "Authorization": f"Basic {credentials_encoded}",
        "Content-Type": "application/json"
    }
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        project_info = response.json()
        return project_info["connectorDefaultId"]
    else:
        print(f"Failed to get project information. Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        return None

def remove_proxies(username, password, connector_uuid, duplicate=False, only_offline=False):
    credentials = f"{username}:{password}"
    credentials_encoded = base64.b64encode(credentials.encode()).decode()
    base_url = "http://localhost:8890/api/scraper/project/connectors"
    endpoint = f"{base_url}/{connector_uuid}/freeproxies/remove"
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
        print("Proxies removed successfully.")
    else:
        print(f"Failed to remove proxies. Status code: {response.status_code}")
        print(f"Response content: {response.text}")

def add_proxies(username, password, connector_uuid, proxies):
    credentials = f"{username}:{password}"
    credentials_encoded = base64.b64encode(credentials.encode()).decode()
    base_url = "http://localhost:8890/api/scraper/project/connectors"
    endpoint = f"{base_url}/{connector_uuid}/freeproxies"
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
        print(f" {len(proxies)} proxies added successfully.")
    else:
        print(f"Failed to add proxies. Status code: {response.status_code}")
        print(f"Response content: {response.text}")

async def fetch_good_proxies():
    provider = ProxyProvider()
    working_proxies = await provider.checkProxies()
    return working_proxies

if __name__ == "__main__":
    username = "ndloqy2c0df6njvp7333"
    password = "qr3mhcy7tghf64osi5zr"
    
    connector_uuid = get_connector_info(username, password)
    if connector_uuid:
        print("UUID of the project:", connector_uuid)
        #remove_proxies(username, password, connector_uuid, only_offline=True)
        proxies = asyncio.run(fetch_good_proxies())
        if len(proxies) > 0:
            add_proxies(username, password, connector_uuid, proxies)
            remove_proxies(username, password, connector_uuid,duplicate=True)
    else:
        print("Failed to retrieve project UUID.")
