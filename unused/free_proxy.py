from typing import List
import requests
from pydantic import BaseModel
from simplestr import gen_str_repr_eq
from bs4 import BeautifulSoup
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




u = UtilsFreeProxy()
all = u.get_ssl()
for a in all:
    print(a)



async def http_get_with_aiohttp(session: ClientSession, url: str, headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (int, Dict[str, Any], bytes):
    # Make request
    try:
        response = await session.get(url=url, headers=headers, proxy=proxy, timeout=timeout)
    except Exception as e:
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


async def check_my_ip_with_tor(session: ClientSession) -> (int, Dict[str, Any], bytes):
    result = await http_get_with_aiohttp(session, 'https://api.myip.com/', proxy="http://169.57.1.84:80")
    print("check_my_ip_with_tor(): Your current TOR IP address: " + str(result))
    return result

async def main():
    # Open session
    session = ClientSession()

    await check_my_ip_with_tor(session)

    # Close session
    await session.close()

asyncio.run(main())