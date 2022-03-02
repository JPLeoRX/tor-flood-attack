import asyncio
import json
import time
import traceback
from typing import Dict, Any, List, Tuple
import aiohttp.client_exceptions
from aiohttp import ClientSession
from models.http_response import HttpResponse
from injectable import injectable


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
HTTP_STATUS_CODE_EXCEPTION_CLIENT_RESPONSE_ERROR = -10000


@injectable
class ServiceAiohttp:
    async def http_get_with_aiohttp(self, session: ClientSession, url: str, headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> HttpResponse:
        # Make request
        try:
            response = await session.get(url=url, headers=headers, proxy=proxy, timeout=timeout)
        except asyncio.exceptions.TimeoutError as e1:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_TIMEOUT, None, None)
        except aiohttp.client_exceptions.ClientHttpProxyError as e2:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR, None, None)
        except aiohttp.client_exceptions.ClientConnectorError as e3:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR, None, None)
        except aiohttp.client_exceptions.ServerDisconnectedError as e4:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_SERVER_DISCONNECTED_ERROR, None, None)
        except aiohttp.client_exceptions.ClientOSError as e5:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_CLIENT_OS_ERROR, None, None)
        except aiohttp.client_exceptions.ClientResponseError as e6:
            return HttpResponse(HTTP_STATUS_CODE_EXCEPTION_CLIENT_RESPONSE_ERROR, None, None)
        except Exception as e7:
            print(traceback.format_exc())
            return HttpResponse(0, None, None)

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

        return HttpResponse(response.status, response_json, response_content)

    async def http_get_with_aiohttp_parallel(self, session: ClientSession, list_of_urls: List[str], headers: Dict = {}, proxy: str = None, timeout: int = 10, ignore_json: bool = False, ignore_body: bool = False) -> (List[HttpResponse], float):
        t1 = time.time()
        results = await asyncio.gather(*[self.http_get_with_aiohttp(session, url, headers, proxy, timeout, ignore_json, ignore_body) for url in list_of_urls])
        t2 = time.time()
        t = t2 - t1
        return results, t

    def debug_stats(self, url: str, results: List[HttpResponse], t: float):
        print('ServiceAiohttp.debug_stats(): ' + url)
        success_responses = len([r for r in results if 200 <= r.status_code <= 299])
        redirect_responses = len([r for r in results if 300 <= r.status_code <= 399])
        client_error_responses = len([r for r in results if 400 <= r.status_code <= 499])
        not_found_responses = len([r for r in results if r.status_code == HTTP_STATUS_CODE_NOT_FOUND])
        method_not_allowed_responses = len([r for r in results if r.status_code == HTTP_STATUS_CODE_METHOD_NOT_ALLOWED])
        server_error_responses = len([r for r in results if 500 <= r.status_code <= 599])
        connection_timeouts = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_CONNECTION_TIMEOUT])
        proxy_errors = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_PROXY_ERROR])
        ssl_errors = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_SSL_ERROR])
        connection_errors = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_CONNECTION_ERROR])
        read_timeouts = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_READ_TIMEOUT])
        too_many_redirects = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_TOO_MANY_REDIRECTS])
        timeouts = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_TIMEOUT])
        server_disconnected_error = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_SERVER_DISCONNECTED_ERROR])
        client_os_error = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_CLIENT_OS_ERROR])
        client_response_error = len([r for r in results if r.status_code == HTTP_STATUS_CODE_EXCEPTION_CLIENT_RESPONSE_ERROR])

        print('ServiceAiohttp.debug_stats(): Total responses count: ' + str(len(results)))
        if success_responses > 0:
            print('ServiceAiohttp.debug_stats(): Success responses: ' + str(success_responses))
        if redirect_responses > 0:
            print('ServiceAiohttp.debug_stats(): Redirect responses: ' + str(redirect_responses))

        if client_error_responses > 0:
            print('ServiceAiohttp.debug_stats(): Client error responses (4XX): ' + str(client_error_responses))
        if not_found_responses > 0:
            print('ServiceAiohttp.debug_stats(): Not found responses (' + str(HTTP_STATUS_CODE_NOT_FOUND) + '): ' + str(not_found_responses))
        if method_not_allowed_responses > 0:
            print('ServiceAiohttp.debug_stats(): Method not allowed responses (' + str(HTTP_STATUS_CODE_METHOD_NOT_ALLOWED) + '): ' + str(method_not_allowed_responses))

        if server_error_responses > 0:
            print('ServiceAiohttp.debug_stats(): Server error responses (5XX): ' + str(server_error_responses))

        if connection_timeouts > 0:
            print('ServiceAiohttp.debug_stats(): Connection timeouts (by client): ' + str(connection_timeouts))
        if proxy_errors > 0:
            print('ServiceAiohttp.debug_stats(): Proxy errors (by client): ' + str(proxy_errors))
        if ssl_errors > 0:
            print('ServiceAiohttp.debug_stats(): SSL errors (by client): ' + str(ssl_errors))
        if connection_errors > 0:
            print('ServiceAiohttp.debug_stats(): Connections errors (by client): ' + str(connection_errors))
        if read_timeouts > 0:
            print('ServiceAiohttp.debug_stats(): Read timeouts (by client): ' + str(read_timeouts))
        if too_many_redirects > 0:
            print('ServiceAiohttp.debug_stats(): Too many redirects (by client): ' + str(too_many_redirects))
        if timeouts > 0:
            print('ServiceAiohttp.debug_stats(): Timeouts (by client): ' + str(timeouts))
        if server_disconnected_error > 0:
            print('ServiceAiohttp.debug_stats(): Server disconnected (by client): ' + str(server_disconnected_error))
        if client_os_error > 0:
            print('ServiceAiohttp.debug_stats(): Client OS error (by client): ' + str(client_os_error))
        if client_response_error > 0:
            print('ServiceAiohttp.debug_stats(): Client response error (by client): ' + str(client_response_error))

        print('ServiceAiohttp.debug_stats(): Execution time is ' + str(round(t, 2)) + ' s,' + ' speed is ' + str(round(len(results) / t, 2)) + ' r/s')
        print('ServiceAiohttp.debug_stats(): ')
