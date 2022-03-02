from typing import List
import requests
from bs4 import BeautifulSoup
from models.free_proxy_item import FreeProxyItem
from omoide_cache import omoide_cache, RefreshMode
from injectable import injectable


@injectable
class ServiceFreeProxy:
    def _get_proxies(self, url: str) -> List[FreeProxyItem]:
        response = requests.get(url)
        response_content = str(response.content)[2:-1]

        results = []

        soup = BeautifulSoup(response_content, 'html.parser')
        soup_table = soup.find_all("table")[0]
        soup_table_rows = soup_table.find_all("tr")
        for soup_table_row in soup_table_rows:
            soup_table_cols = soup_table_row.find_all("td")
            values = [c.text for c in soup_table_cols]
            if len(values) > 0:
                p = FreeProxyItem(values[0], int(values[1]), values[2], values[7])
                results.append(p)

        return results

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=120)
    def get_new(self) -> List[FreeProxyItem]:
        return self._get_proxies("https://free-proxy-list.net/")

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=120)
    def get_us(self) -> List[FreeProxyItem]:
        return self._get_proxies("https://www.us-proxy.org/")

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=120)
    def get_uk(self) -> List[FreeProxyItem]:
        return self._get_proxies("https://free-proxy-list.net/uk-proxy.html")

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=120)
    def get_ssl(self) -> List[FreeProxyItem]:
        return self._get_proxies("https://www.sslproxies.org/")

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=120)
    def get_anonymous(self) -> List[FreeProxyItem]:
        return self._get_proxies("https://free-proxy-list.net/anonymous-proxy.html")

    @omoide_cache(refresh_mode=RefreshMode.INDEPENDENT, refresh_period_s=60)
    def get_all(self) -> List[FreeProxyItem]:
        #proxies_new = self.get_new()
        #proxies_us = self.get_us()
        #proxies_uk = self.get_uk()
        proxies_ssl = self.get_ssl()
        #proxies_anonymous = self.get_anonymous()

        proxies_all = []
        #proxies_all.extend(proxies_new)
        #proxies_all.extend(proxies_us)
        #proxies_all.extend(proxies_uk)
        proxies_all.extend(proxies_ssl)
        #proxies_all.extend(proxies_anonymous)

        # Filter out dublicates
        ip_set = set()
        results = []
        for p in proxies_all:
            if p.ip not in ip_set:
                results.append(p)
                ip_set.add(p.ip)

        return results


