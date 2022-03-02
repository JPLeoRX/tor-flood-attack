import time
from typing import Dict, List, Any
import asyncio
from injectable import injectable, autowired, Autowired
from aiohttp import ClientSession
from tekleo_common_utils import UtilsRandom
from models.http_response import HttpResponse
from services.service_aiohttp import ServiceAiohttp
from services.service_free_proxy import ServiceFreeProxy


@injectable
class ServiceAnonymity:
    @autowired
    def __init__(self, service_aiohttp: Autowired(ServiceAiohttp), service_free_proxy: Autowired(ServiceFreeProxy), utils_random: Autowired(UtilsRandom)):
        self.service_aiohttp = service_aiohttp
        self.service_free_proxy = service_free_proxy
        self.utils_random = utils_random



    # Headers
    #-------------------------------------------------------------------------------------------------------------------
    def get_headers(self) -> List[Dict[str,Any]]:
        return [
            {
                'User-Agent': self.utils_random.get_random_user_agent(),
                'X-Forwarded-For': self.utils_random.get_random_ip(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '115',
                'Connection': 'keep-alive',
            }
            for i in range(0, 300)
        ]
    #-------------------------------------------------------------------------------------------------------------------



    # Proxies
    #-------------------------------------------------------------------------------------------------------------------
    def get_tor_proxy(self) -> str:
        return "http://127.0.0.1:8118"

    def get_free_proxies_all(self) -> List[str]:
        return [a.get_proxy_str() for a in self.service_free_proxy.get_all()]

    async def get_free_proxies_working(self, session: ClientSession) -> List[str]:
        proxies = self.get_free_proxies_all()
        results, t = await self.check_my_ip_parallel_for_proxies(session, proxies, debug=False, timeout=15)

        working_proxies = []
        for i in range(0, len(proxies)):
            current_proxy = proxies[i]
            current_result = results[i]
            if current_result.status_code == 200:
                working_proxies.append(current_proxy)
        print('ServiceAnonymity.get_free_proxies_working(): Found ' + str(len(working_proxies)) + ' working free proxies in ' + str(round(t, 3)) + ' seconds')
        return working_proxies
    #-------------------------------------------------------------------------------------------------------------------



    # Checking IP
    #-------------------------------------------------------------------------------------------------------------------
    async def check_my_ip(self, session: ClientSession, headers: Dict = {}, proxy: str = None, timeout: int = 10, debug: bool = True) -> HttpResponse:
        result = await self.service_aiohttp.http_get_with_aiohttp(session, 'https://api.myip.com/', headers=headers, proxy=proxy, timeout=timeout)
        if result.status_code == 200:
            if debug:
                print("ServiceAnonymity.check_my_ip(): Your current IP address: " + str(result.json))
        else:
            if debug:
                print("ServiceAnonymity.check_my_ip(): WARNING!!! Failed to get your current IP address: " + str(result))
        return result

    async def check_my_ip_parallel_for_proxies(self, session: ClientSession, list_of_proxies: List[str], headers: Dict = {}, timeout: int = 10, debug: bool = True) -> (List[HttpResponse], float):
        t1 = time.time()
        results = await asyncio.gather(*[self.check_my_ip(session, headers, proxy, timeout, debug) for proxy in list_of_proxies])
        t2 = time.time()
        t = t2 - t1
        return results, t
    #-------------------------------------------------------------------------------------------------------------------
