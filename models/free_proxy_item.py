from simplestr import gen_str_repr_eq


@gen_str_repr_eq
class FreeProxyItem:
    ip: str
    port: int
    code: str
    last_checked: str
    extra_check_performed: bool = False
    extra_check_working: bool = False

    def __init__(self, ip: str, port: int, code: str, last_checked: str) -> None:
        self.ip=ip
        self.port=port
        self.code=code
        self.last_checked=last_checked

    def get_proxy_str(self) -> str:
        return 'http://' + self.ip + ':' + str(self.port)
