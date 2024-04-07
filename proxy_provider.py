import asyncio
import platform
import aiohttp
from Proxy_List_Scrapper import Scrapper
import logging

import requests

class ProxyProvider:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    test_url = "https://divar.ir"
    timeout_sec = 60

    def __init__(self):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def is_bad_proxy(self, proxy):
        ipport = f"{proxy['ip']}:{proxy['port']}"
        proxy_url = None
        if proxy['type'].lower() == 'http':
            proxy_url = f'http://{ipport}'
        elif proxy['type'].lower() == 'socks4':
            proxy_url = f'socks4://{ipport}'
        elif proxy['type'].lower() == 'socks5':
            proxy_url = f'socks5://{ipport}'
        
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self.test_url, proxy=proxy_url, timeout=self.timeout_sec)
                self.logger.info(f'{ipport} => {resp.status}')
                if resp.status != 200:
                    raise Exception("Error")
                return proxy
        except Exception as e:
            self.logger.error(f'Error checking proxy {ipport}: {e}')
            return None
        

    def fetch_proxies_from_scrapper(self):
        try:
            scrapper = Scrapper(category='ALL', print_err_trace=False)
            data = scrapper.getProxies()
            self.logger.info(f'{len(data.proxies)} proxies are fetched from the Scrapper.')
            proxies_with_type = [{'ip': proxy.ip, 'port': proxy.port, 'type': 'http'} for proxy in data.proxies]
            return proxies_with_type
        except Exception as e:
            self.logger.error(f"An error occurred while fetching proxies: {str(e)}")
            return []
        
    def fetch_proxies_from_geonode(self):
        url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                proxies_data = response.json().get('data', [])
                self.logger.info(f"{len(proxies_data)} proxies are fetched from the geonode.")
                proxies_with_type = [{'ip': proxy['ip'], 'port': proxy['port'], 'type': proxy['protocols'][0]} for proxy in proxies_data]
                return proxies_with_type
            else:
                self.logger.error(f"Failed to fetch proxies. Status code: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"An error occurred while fetching proxies: {str(e)}")
            return []
    
    def fetch_proxies_from_TheSpeedX(self):
        urls = {
            "socks5": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "socks4": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
            "http": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
        }

        proxies = []
        for protocol, url in urls.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    proxy_list = response.text.split('\n')
                    proxy_list = [proxy.strip() for proxy in proxy_list if proxy.strip()]
                    self.logger.info(f"{len(proxy_list)} {protocol} proxies are fetched from TheSpeedX.")
                    proxies.extend([{'ip': proxy.split(':')[0], 'port': proxy.split(':')[1], 'type': protocol.lower()} for proxy in proxy_list])
                else:
                    self.logger.error(f"Failed to fetch {protocol} proxies. Status code: {response.status_code}")
            except Exception as e:
                self.logger.error(f"An error occurred while fetching {protocol} proxies: {str(e)}")
        return proxies

    def fetch_proxies(self):
        proxies_s = self.fetch_proxies_from_scrapper()
        proxies_g = self.fetch_proxies_from_geonode()
        proxies_TheSpeedX = self.fetch_proxies_from_TheSpeedX()
        
        all_proxies = proxies_s + proxies_g + proxies_TheSpeedX

        unique_proxies = []
        for proxy in all_proxies:
            if proxy not in unique_proxies:
                unique_proxies.append(proxy)
        
        return unique_proxies

    async def checkProxies(self):
        self.proxyList = self.fetch_proxies()
        if not self.proxyList:
            return []

        working_proxies = []
        tasks = [self.is_bad_proxy(proxy) for proxy in self.proxyList]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result is not None:
                working_proxies.append(result)

        return working_proxies
