import time
from typing import Dict, Any, List, Tuple
import requests
import random
import sys
import concurrent.futures
from itertools import repeat
from string import ascii_lowercase, ascii_uppercase
from user_agent import generate_user_agent
from stem import Signal
from stem.control import Controller



ALL_LETTERS = []
ALL_LETTERS.extend(ascii_lowercase)
ALL_LETTERS.extend(ascii_uppercase)


HTTP_METHOD_GET = 'get'
HTTP_METHOD_POST = 'post'
HTTP_METHOD_PUT = 'put'


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
HTTP_STATUS_CODE_CONNECTION_TIMEOUT = -1000
HTTP_STATUS_CODE_PROXY_ERROR = -2000



# Random helper functions
#-----------------------------------------------------------------------------------------------------------------------
def get_random_user_agent() -> str:
    return str(generate_user_agent())


def get_random_ip() -> str:
    return '.'.join([str(random.randint(0,255)) for i in range(0,4)])


def get_random_string(size: int) -> str:
    return ''.join([random.choice(ALL_LETTERS) for i in range(0, size)])


def get_random_body(min_number_of_keys: int = 50, max_number_of_keys: int = 400, min_key_size: int = 100, max_key_size: int = 800, min_value_size: int = 400, max_value_size: int = 16000) -> Dict[str, str]:
    body = {}
    number_of_keys = random.randint(min_number_of_keys, max_number_of_keys)
    for ik in range(0, number_of_keys):
        key_size = random.randint(min_key_size, max_key_size)
        value_size = random.randint(min_value_size, max_value_size)
        key = get_random_string(key_size)
        value = get_random_string(value_size)
        body[key] = value
    return body


def get_headers() -> Dict[str, str]:
    return {
        'User-Agent': get_random_user_agent(),
        'X-Forwarded-For': get_random_ip(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive',
    }


def get_proxies_tor() -> Dict[str, str]:
    return {
        'https': '127.0.0.1:8118'
    }
#-----------------------------------------------------------------------------------------------------------------------



# Request
#-----------------------------------------------------------------------------------------------------------------------
def make_request_raw(http_method: str, url: str, body: Dict = {}, headers: Dict = {}, proxies: Dict = {}, timeout: int = 15) -> requests.Response:
    if len(proxies) == 0:
        print("make_request_raw(): Warning! No proxies were set for request " + http_method + " " + url)
    http_method = http_method.strip().lower()
    if http_method == HTTP_METHOD_GET:
        return requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
    elif http_method == HTTP_METHOD_POST:
        return requests.post(url, data=body, headers=headers, proxies=proxies, timeout=timeout)
    elif http_method == HTTP_METHOD_PUT:
        return requests.put(url, data=body, headers=headers, proxies=proxies, timeout=timeout)
    else:
        raise RuntimeError("Unknown http_method=" + str(http_method))


def make_request(http_method: str, url: str, body: Dict = {}, headers: Dict = {}, proxies: Dict = {}, timeout: int = 15) -> (int, Dict[str, Any], bytes):
    try:
        response = make_request_raw(http_method, url, body=body, headers=headers, proxies=proxies, timeout=timeout)
    except requests.exceptions.ConnectTimeout as e1:
        return (HTTP_STATUS_CODE_CONNECTION_TIMEOUT, None, None)
    except requests.exceptions.ProxyError as e2:
        return (HTTP_STATUS_CODE_PROXY_ERROR, None, None)


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


def make_requests_parallel(http_method: str, url: str, number_of_requests: int, max_worker_count: int, body: Dict = {}, headers: Dict = {}, proxies: Dict = {}, timeout: int = 10) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_worker_count)
    for result in executor.map(make_request, repeat(http_method, number_of_requests), repeat(url, number_of_requests), repeat(body), repeat(headers), repeat(proxies), repeat(timeout)):
        results.append(result)
    t2 = time.time()
    t = t2 - t1
    return results, t


def debug_stats(results: List[Tuple[int, Dict[str, Any], bytes]], t: float):
    print('debug_stats(): ----------------------- ')
    success_responses = len([r for r in results if 200 <= r[0] <= 299])
    redirect_responses = len([r for r in results if 300 <= r[0] <= 399])
    client_error_responses = len([r for r in results if 400 <= r[0] <= 499])
    not_found_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_NOT_FOUND])
    method_not_allowed_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_METHOD_NOT_ALLOWED])
    server_error_responses = len([r for r in results if 500 <= r[0] <= 599])
    timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_CONNECTION_TIMEOUT])

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

    if timeouts > 0:
        print('debug_stats(): Timeouts (by client): ' + str(timeouts))

    print('debug_stats(): Execution time is ' + str(round(t, 2)) + ' s,' + ' speed is ' + str(round(len(results) / t, 2)) + ' r/s')
    print('debug_stats(): ')
#-----------------------------------------------------------------------------------------------------------------------



# TOR helpers
#-----------------------------------------------------------------------------------------------------------------------
def switch_tor_ip():
    time.sleep(1)
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='my password')
        controller.signal(Signal.NEWNYM)
    print("switch_tor_ip(): Generated new IP")
    time.sleep(1)

def check_my_ip_with_tor() -> (int, Dict[str, Any], bytes):
    result = make_request('GET', 'https://api.myip.com/', proxies=get_proxies_tor())
    print("check_my_ip_with_tor(): Your current TOR IP address: " + str(result))
    return result
#-----------------------------------------------------------------------------------------------------------------------



# Testing
#-----------------------------------------------------------------------------------------------------------------------
def test_get_random_user_agent():
    print('-----------------------------------------------------------------------------------------------------------')
    print('test_get_random_user_agent(): Started')
    print('test_get_random_user_agent(): Generated UA', get_random_user_agent())
    print('test_get_random_user_agent(): Generated UA', get_random_user_agent())
    print('test_get_random_user_agent(): Generated UA', get_random_user_agent())
    print('test_get_random_user_agent(): Generated UA', get_random_user_agent())
    print('test_get_random_user_agent(): Ended')

def test_get_random_ip():
    print('-----------------------------------------------------------------------------------------------------------')
    print('test_get_random_ip(): Started')
    print('test_get_random_ip(): Generated IP', get_random_ip())
    print('test_get_random_ip(): Generated IP', get_random_ip())
    print('test_get_random_ip(): Generated IP', get_random_ip())
    print('test_get_random_ip(): Generated IP', get_random_ip())
    print('test_get_random_ip(): Ended')

def test_get_random_string():
    print('-----------------------------------------------------------------------------------------------------------')
    print('test_get_random_string(): Started')
    print('test_get_random_string(): Generated string', get_random_string(10))
    print('test_get_random_string(): Generated string', get_random_string(20))
    print('test_get_random_string(): Generated string', get_random_string(30))
    print('test_get_random_string(): Generated string', get_random_string(100))
    print('test_get_random_string(): Ended')

def test_get_random_body():
    print('-----------------------------------------------------------------------------------------------------------')
    print('test_get_random_body(): Started')
    for i in range(0, 3):
        body = get_random_body()
        print('test_get_random_body(): Generated body with size of dict', sys.getsizeof(body), 'bytes, and size of string', sys.getsizeof(str(body)), 'bytes')
    print('test_get_random_body(): Ended')

def test_make_request():
    r = make_request("GET", "http://google.com")
    print('CODE:', r[0])
    print('JSON:', type(r[1]), r[1])
    print('CONTENT:', type(r[2]), r[2])
    print('\n')
    r = make_request("GET", "https://api.myip.com/")
    print('CODE:', r[0])
    print('JSON:', type(r[1]), r[1])
    print('CONTENT:', type(r[2]), r[2])
    print('\n')
    r = make_request("GET", "https://example.com/sadjhdaslkjasd")
    print('CODE:', r[0])
    print('JSON:', type(r[1]), r[1])
    print('CONTENT:', type(r[2]), r[2])
    print('\n')
    r = make_request("POST", "https://stackoverflow.com/users/login-or-signup/validation/track")
    print('CODE:', r[0])
    print('JSON:', type(r[1]), r[1])
    print('CONTENT:', type(r[2]), r[2])

def test_make_requests_parallel():
    number_of_requests = 300
    max_worker_count = 100
    results, t = make_requests_parallel('GET', "https://tekleo.net/", number_of_requests, max_worker_count, headers=get_headers())
    debug_stats(results, t)

def test_global():
    test_get_random_user_agent()
    print('')
    test_get_random_ip()
    print('')
    test_get_random_string()
    print('')
    test_get_random_body()
#-----------------------------------------------------------------------------------------------------------------------

#test_make_requests_parallel()
#test_global()


print("Started main script!")
for epoch in range(0, 10):
    print('------- Epoch #', epoch, '-------')
    check_my_ip_with_tor()
    number_of_requests = random.randint(200, 400)
    max_worker_count = 100
    results, t = make_requests_parallel('GET', "http://tekleo.net/", number_of_requests, max_worker_count, headers=get_headers(), proxies=get_proxies_tor())
    debug_stats(results, t)
    switch_tor_ip()