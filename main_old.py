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
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(len(list_of_urls), 36))
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


for i in range(0, 1000):
    print('Started batch #' + str(i))
    time.sleep(1)

    # This is a sample list of URLs taken from a chat group
    # RUN THIS AT YOUR OWN RISK
    # This project was intended only for educational / experimental purposes
    batch_request_get_with_tor([
        #"http://www.rt.com",
        "https://russian.rt.com/",
        #"http://www.cbr.ru",
        "http://rbc.ru",
        "http://www.kremlin.ru",
        "http://www.vesti.ru",
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
        "http://gosuslugi.ru",
        "http://194.54.14.168",
        "https://www.sberbank.ru/ru/person",
        "http://194.54.14.131",
        "https://online.sberbank.ru",
        "https://yandex.ru/",
        "https://tv.yandex.ru/?utm_source=main_stripe_big",
        "https://tv.yandex.ru/api/sk",
        "https://music.yandex.ru/?utm_source=main_stripe_big",
        "https://auto.ru/?utm_source=main_stripe_big",
        "https://yandex.ru/news/?utm_source=main_stripe_big",
        "https://strm.yandex.ru/probe/jobs?count=5&size=51200",
        "https://akamai.strm.yandex.net/probe/test_file_51200.mp4?size=51200&rnd=3843909514455359",
        "https://www.1tv.ru",
        "http://3dsec.sberbank.ru",
        'http://185.157.97.52', 'http://185.157.97.135', 'http://185.157.97.135', 'http://185.157.96.60', 'http://194.54.14.241', 'http://194.54.14.242', 'http://194.54.14.192', 'http://194.54.14.193', 'http://194.54.14.236', 'http://194.54.14.49', 'http://193.143.119.208', 'http://194.186.207.109', 'http://194.186.207.37', 'http://194.54.14.251', 'http://194.54.14.186', 'http://194.186.207.33', 'http://194.54.14.96', 'http://185.157.97.11', 'http://194.54.14.94', 'http://194.54.14.95', 'http://193.143.119.209', 'http://185.157.97.125', 'http://194.54.14.252', 'http://194.54.14.187', 'http://194.186.207.34', 'http://194.186.207.189', 'http://194.54.14.91', 'http://194.54.14.97', 'http://194.54.14.28', 'http://185.157.96.154', 'http://194.186.207.184', 'http://194.54.14.209', 'http://194.186.207.183', 'http://194.186.207.185', 'http://194.186.207.23', 'http://185.157.96.29', 'http://194.54.14.6', 'http://194.54.14.255', 'http://194.54.14.119', 'http://178.248.233.180', 'http://35.164.66.26', 'http://194.186.207.14', 'http://185.157.96.23', 'http://194.54.14.88', 'http://185.157.97.200', 'http://194.54.14.213', 'http://185.157.96.31', 'http://80.66.93.227', 'http://194.54.14.129', 'http://194.54.14.159', 'http://194.54.14.6', 'http://193.19.100.126', 'http://194.186.207.153', 'http://195.43.144.20', 'http://45.12.238.92', 'http://194.54.15.96', 'http://62.76.205.110', 'http://185.157.97.99', 'http://185.157.97.68', 'http://194.186.207.63', 'http://194.54.14.219', 'http://185.163.158.143', 'http://185.163.158.149', 'http://194.54.14.168', 'http://178.248.234.63', 'http://194.54.15.168', 'http://83.167.87.87', 'http://185.157.96.104', 'http://185.157.96.88', 'http://185.157.96.87', 'http://91.217.194.198', 'http://91.217.194.198',
        "http://109.207.1.118", "http://213.59.255.175", "http://91.217.21.1", "http://109.207.2.218", "http://91.217.20.1",
        "https://www.sberbank.ru/portalserver/static/features/%5BBBHOST%5D/CorpPortalCommonFeature/platform.cxp.fallback.js?v=b0fb6731b791cda1f51923a7710446cda90567f0",
        "https://wagnera.ru/",
        "https://wagnera.ru/delites-svoimi-istoriyami-i-foto",
        "https://wagnera.ru/wp-content/uploads/2020/07/cropped-logo-300x300.png",
        "https://wagnera.ru/wp-content/plugins/elementor-pro/assets/js/preloaded-elements-handlers.min.js?ver=3.3.0",
        "https://wagnera.ru/wp-content/uploads/2021/10/Kadr-ot-WAGNER-GROUP-_-WORK-AND-TRAVEL.mp4.png",
    ])
    print('Ended batch #' + str(i))
    switch_tor_ip()
    try:
        print("This is your new TOR IP address:", request_get_with_tor('https://api.myip.com/'))
    except:
        print("Failed to check new TOR IP address, switching one more time")
        switch_tor_ip()
