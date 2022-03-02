import asyncio
import json
import time
import traceback
from threading import Thread
from typing import Dict, Any, List, Tuple

import aiohttp.client_exceptions
import requests
import concurrent.futures
from itertools import repeat
from aiohttp import ClientSession
from tekleo_common_utils import UtilsRandom

HTTP_STATUS_CODE_SUCCESS = 200
HTTP_STATUS_CODE_UNAUTHORIZED = 401
HTTP_STATUS_CODE_FORBIDDEN = 403
HTTP_STATUS_CODE_NOT_FOUND = 404
HTTP_STATUS_CODE_METHOD_NOT_ALLOWED = 405
HTTP_STATUS_CODE_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_STATUS_CODE_TOO_MANY_REQUESTS = 429
HTTP_STATUS_CODE_INTERNAL_SERVER_ERROR = 500
HTTP_STATUS_CODE_BAD_GATEWAY = 502
HTTP_STATUS_CODE_SERVICE_UNAVAILABLE = 503
HTTP_STATUS_CODE_EXCEPTION_CONNECTION_TIMEOUT = -1000
HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR = -2000
HTTP_STATUS_CODE_EXCEPTION_SSL_ERROR = -3000
HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR = -4000
HTTP_STATUS_CODE_EXCEPTION_READ_TIMEOUT = -5000
HTTP_STATUS_CODE_EXCEPTION_TOO_MANY_REDIRECTS = -6000
HTTP_STATUS_CODE_EXCEPTION_TIMEOUT = -7000


def http_get_with_requests(url: str, headers: Dict = {}, proxies: Dict = {}, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (int, Dict[str, Any], bytes):
    # Make request
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    except requests.exceptions.ConnectTimeout as e1:
        return (HTTP_STATUS_CODE_EXCEPTION_CONNECTION_TIMEOUT, None, None)
    except requests.exceptions.ProxyError as e2:
        return (HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR, None, None)
    except requests.exceptions.SSLError as e3:
        return (HTTP_STATUS_CODE_EXCEPTION_SSL_ERROR, None, None)
    except requests.exceptions.ConnectionError as e4:
        return (HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR, None, None)
    except requests.exceptions.ReadTimeout as e5:
        return (HTTP_STATUS_CODE_EXCEPTION_READ_TIMEOUT, None, None)
    except requests.exceptions.TooManyRedirects as e6:
        return (HTTP_STATUS_CODE_EXCEPTION_TOO_MANY_REDIRECTS, None, None)

    # Read JSON
    response_json = None
    if not ignore_json:
        try:
            response_json = response.json()
        except:
            pass

    # Read BODY
    response_content = None
    if not ignore_body:
        try:
            response_content = response.content
        except:
            pass

    return (response.status_code, response_json, response_content)


def http_get_with_requests_parallel(list_of_urls: List[str], headers: Dict = {}, proxies: Dict = {}, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=100)
    for result in executor.map(http_get_with_requests, list_of_urls, repeat(headers), repeat(proxies), repeat(timeout), repeat(ignore_json), repeat(ignore_body)):
        results.append(result)
    t2 = time.time()
    t = t2 - t1
    return results, t


async def http_get_with_aiohttp(session: ClientSession, url: str, headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (int, Dict[str, Any], bytes):
    # Make request
    try:
        response = await session.get(url=url, headers=headers, proxy=proxy, timeout=timeout)
    except asyncio.exceptions.TimeoutError as e1:
        return (HTTP_STATUS_CODE_EXCEPTION_TIMEOUT, None, None)
    except aiohttp.client_exceptions.ClientHttpProxyError as e2:
        return (HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR, None, None)
    except Exception as e3:
        print(traceback.format_exc())
        return (0, None, None)

    # Read JSON
    response_json = None
    if not ignore_json:
        try:
            response_json = await response.json(content_type=None)
        except json.decoder.JSONDecodeError as e:
            pass

    # Read BODY
    response_content = None
    if not ignore_body:
        try:
            response_content = await response.read()
        except:
            pass

    return (response.status, response_json, response_content)


async def http_get_with_aiohttp_parallel(session: ClientSession, list_of_urls: List[str], headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = await asyncio.gather(*[http_get_with_aiohttp(session, url, headers, proxy, timeout, ignore_json, ignore_body) for url in list_of_urls])
    t2 = time.time()
    t = t2 - t1
    return results, t




async def main():
    utils_random = UtilsRandom()
    headers = {
        'User-Agent': utils_random.get_random_user_agent(),
        'X-Forwarded-For': utils_random.get_random_ip(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
    }
    proxy = "http://127.0.0.1:8118"
    proxies = {
        'https': '127.0.0.1:8118'
    }
    urls = ["https://api.myip.com/" for i in range(0, 1000)]

    session = ClientSession()
    r = await http_get_with_aiohttp(session, "https://api.myip.com/", headers=headers, proxy=proxy)
    print(r)
    speeds_aiohttp = []
    for i in range(0, 10):
        results, t = await http_get_with_aiohttp_parallel(session, urls, headers=headers, proxy=proxy, ignore_json=True, ignore_body=True)
        v = len(urls) / t
        print('AIOHTTP: Took ' + str(round(t, 2)) + ' s, with speed of ' + str(round(v, 2)) + ' r/s')
        speeds_aiohttp.append(v)
    await session.close()


    speeds_requests = []
    r = http_get_with_requests("https://api.myip.com/", headers=headers, proxies=proxies)
    print(r)
    for i in range(0, 10):
        results, t = http_get_with_requests_parallel(urls, headers=headers, proxies=proxies)
        v = len(urls) / t
        print('REQUESTS: Took ' + str(round(t, 2)) + ' s, with speed of ' + str(round(v, 2)) + ' r/s')
        speeds_requests.append(v)


    avg_speed_aiohttp = sum(speeds_aiohttp) / len(speeds_aiohttp)
    avg_speed_requests = sum(speeds_requests) / len(speeds_requests)
    print('--------------------')
    print('AVG SPEED AIOHTTP: ' + str(round(avg_speed_aiohttp, 2)))
    print('AVG SPEED REQUESTS: ' + str(round(avg_speed_requests, 2)))



asyncio.run(main())
