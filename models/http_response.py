from typing import Dict, Any
from simplestr import gen_str_repr_eq


@gen_str_repr_eq
class HttpResponse:
    status_code: int
    json: Dict[str, Any]
    content: bytes

    def __init__(self, status_code: int, json: Dict[str, Any], content: bytes):
        self.status_code = status_code
        self.json = json
        self.content = content
