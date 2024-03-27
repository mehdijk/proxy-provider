import asyncio
import platform
import aiohttp
from Proxy_List_Scrapper import Scrapper
import logging

class ProxyProvider:
    logger = logging.getLogger()
    test_url = "https://divar.ir"
    timeout_sec = 30

    def __init__(self):
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def is_bad_proxy(self, proxy):
        ipport = f"{proxy.ip}:{proxy.port}"
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self.test_url, proxy=f'http://{ipport}', timeout=self.timeout_sec)
                self.logger.info(f'{ipport} => {resp.status}')
                if resp.status != 200:
                    raise Exception("Error")
                return proxy
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None
        except Exception as e:
            self.logger.error(f'Error checking proxy {ipport}: {e}')
            return None

    def fetch_proxies(self):
        try:
            scrapper = Scrapper(category='ALL', print_err_trace=False)
            data = scrapper.getProxies()
            print(f'{len(data.proxies)} proxies are fetched from the web.')
            return data.proxies
        except Exception as e:
            print(f"An error occurred while fetching proxies: {str(e)}")
            return []

    async def checkProxies(self):
        self.proxyList = self.fetch_proxies()
        if not self.proxyList:
            return []

        working_proxies = set()
        tasks = [self.is_bad_proxy(proxy) for proxy in self.proxyList]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result is not None:
                working_proxies.add(result)

        return working_proxies
