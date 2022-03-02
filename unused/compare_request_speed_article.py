import asyncio
import json
import time
from typing import Dict, Any, List, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from itertools import repeat
from aiohttp import ClientSession


def http_get_with_requests(url: str, headers: Dict = {}, proxies: Dict = {}, timeout: int = 10) -> (int, Dict[str, Any], bytes):
    response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)

    response_json = None
    try:
        response_json = response.json()
    except:
        pass

    response_content = None
    try:
        response_content = response.content
    except:
        pass

    return (response.status_code, response_json, response_content)


def http_get_with_requests_parallel(list_of_urls: List[str], headers: Dict = {}, proxies: Dict = {}, timeout: int = 10) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = []
    executor = ThreadPoolExecutor(max_workers=100)
    for result in executor.map(http_get_with_requests, list_of_urls, repeat(headers), repeat(proxies), repeat(timeout)):
        results.append(result)
    t2 = time.time()
    t = t2 - t1
    return results, t


async def http_get_with_aiohttp(session: ClientSession, url: str, headers: Dict = {}, proxy: str = None, timeout: int = 10) -> (int, Dict[str, Any], bytes):
    response = await session.get(url=url, headers=headers, proxy=proxy, timeout=timeout)

    response_json = None
    try:
        response_json = await response.json(content_type=None)
    except json.decoder.JSONDecodeError as e:
        pass

    response_content = None
    try:
        response_content = await response.read()
    except:
        pass

    return (response.status, response_json, response_content)


async def http_get_with_aiohttp_parallel(session: ClientSession, list_of_urls: List[str], headers: Dict = {}, proxy: str = None, timeout: int = 10) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = await asyncio.gather(*[http_get_with_aiohttp(session, url, headers, proxy, timeout) for url in list_of_urls])
    t2 = time.time()
    t = t2 - t1
    return results, t


async def main():
    print('--------------------')

    # URL list
    urls = ["https://api.myip.com/" for i in range(0, 1000)]

    # Benchmark aiohttp
    session = ClientSession()
    speeds_aiohttp = []
    for i in range(0, 10):
        results, t = await http_get_with_aiohttp_parallel(session, urls)
        v = len(urls) / t
        print('AIOHTTP: Took ' + str(round(t, 2)) + ' s, with speed of ' + str(round(v, 2)) + ' r/s')
        speeds_aiohttp.append(v)
    await session.close()

    print('--------------------')

    # Benchmark requests
    speeds_requests = []
    for i in range(0, 10):
        results, t = http_get_with_requests_parallel(urls)
        v = len(urls) / t
        print('REQUESTS: Took ' + str(round(t, 2)) + ' s, with speed of ' + str(round(v, 2)) + ' r/s')
        speeds_requests.append(v)

    # Calculate averages
    avg_speed_aiohttp = sum(speeds_aiohttp) / len(speeds_aiohttp)
    avg_speed_requests = sum(speeds_requests) / len(speeds_requests)
    print('--------------------')
    print('AVG SPEED AIOHTTP: ' + str(round(avg_speed_aiohttp, 2)) + ' r/s')
    print('AVG SPEED REQUESTS: ' + str(round(avg_speed_requests, 2)) + ' r/s')


asyncio.run(main())
