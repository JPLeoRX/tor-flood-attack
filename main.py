import time
import traceback
import concurrent.futures
from typing import List
import requests
from stem import Signal
from stem.control import Controller
from user_agent import generate_user_agent


def switch_tor_ip():
    time.sleep(1)

    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='my password')
        controller.signal(Signal.NEWNYM)

    print("switch_tor_ip(): Generated new IP")


def get_random_user_agent() -> str:
    return str(generate_user_agent())


def request_get(url: str):
    response = requests.get(url)
    return response.json()


def request_get_with_tor(url: str) -> (int, str):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '115',
        'Connection': 'keep-alive'
    }
    proxies={'https': '127.0.0.1:8118'}
    response = requests.get(url, headers=headers, proxies=proxies, timeout=15)

    # We don't always expect JSON, so ignore this
    try:
        response_json = response.json()
        return response.status_code, response_json
    except:
        return response.status_code, None


def request_get_with_tor_wrapped(url: str) -> bool:
    try:
        result = request_get_with_tor(url)
        print("request_get_with_tor_wrapped(): " + str(url) + ' is responding with code ' + str(result[0]))
        return True
    except:
        print("request_get_with_tor_wrapped(): " + str(url) + ' request failed')
        return False


def batch_request_get_with_tor(list_of_urls: List[str]):
    results = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(len(list_of_urls), 24))
    for result in executor.map(request_get_with_tor_wrapped, list_of_urls):
        results.append(result)


print("This is your real IP address:", request_get('https://api.myip.com/'))
print("This is your 1st TOR IP address:", request_get_with_tor('https://api.myip.com/'))
switch_tor_ip()
print("This is your 2nd TOR IP address:", request_get_with_tor('https://api.myip.com/'))
print("\n")
print("IF THESE IPS ARE NOT FAKE OR SOMETHING CRASHED IN THE PROCESS - IMMEDIATELY KILL THIS CONTAINER (you have 15 seconds to do this)")
print("IF THESE IPS ARE NOT FAKE OR SOMETHING CRASHED IN THE PROCESS - IMMEDIATELY KILL THIS CONTAINER (you have 15 seconds to do this)")
print("IF THESE IPS ARE NOT FAKE OR SOMETHING CRASHED IN THE PROCESS - IMMEDIATELY KILL THIS CONTAINER (you have 15 seconds to do this)")
print("IF THESE IPS ARE NOT FAKE OR SOMETHING CRASHED IN THE PROCESS - IMMEDIATELY KILL THIS CONTAINER (you have 15 seconds to do this)")
time.sleep(15)


for i in range(0, 100):
    print('Started batch #' + str(i))
    time.sleep(1)

    # This is a sample list of URLs taken from a chat group
    # RUN THIS AT YOUR OWN RISK
    # This project was intended only for educational / experimental purposes
    batch_request_get_with_tor([
        #"http://www.rt.com",
        #"http://www.cbr.ru",
        "http://rbc.ru",
        "http://www.kremlin.ru",
        "http://www.vesti.ru",
        "http://www.smotrim.ru",
        "http://www.vgtrk.ru",
        "https://www.kommersant.ru",
        "https://www.kp.ru/",
        "https://rg.ru/",
        "http://lenta.ru",
        "http://gosuslugi.ru",
        "http://194.54.14.168",
        "https://www.sberbank.ru/ru/person",
        "http://194.54.14.131",
        "https://online.sberbank.ru",
    ])
    print('Ended batch #' + str(i))
    switch_tor_ip()
    try:
        print("This is your new TOR IP address:", request_get_with_tor('https://api.myip.com/'))
    except:
        print("Failed to check new TOR IP address, switching one more time")
        switch_tor_ip()
