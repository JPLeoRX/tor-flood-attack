import time
import requests
from stem import Signal
from stem.control import Controller


def switch_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='my password')
        controller.signal(Signal.NEWNYM)


def request_get(url: str):
    response = requests.get(url)
    return response.json()


def request_get_with_tor(url: str):
    response = requests.get(url, proxies={'https': '127.0.0.1:8118'})
    return response.json()


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