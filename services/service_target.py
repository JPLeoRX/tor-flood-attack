from typing import List
import requests
from pydantic import parse_obj_as
from injectable import injectable


@injectable
class ServiceTarget:
    def get_targets_from_file(self, filepath: str) -> List[str]:
        with open(filepath) as f:
            lines = f.readlines()
            lines = [l.strip() for l in lines]
            lines = [l for l in lines if len(l) > 0]
            return lines

    def get_targets_from_url(self, url: str, timeout: int = 10) -> List[str]:
        response = requests.get(url, timeout=timeout)
        response_json = response.json()
        return parse_obj_as(List[str], response_json)
