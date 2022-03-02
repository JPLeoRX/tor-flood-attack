import socket
from typing import List, Dict


def check_port(target_ip_address: str, target_port: int, timeout: float = 0.5) -> bool:
    ''' Try to connect to a specified host on a specified port.
    If the connection takes longer then the TIMEOUT we set we assume
    the host is down. If the connection is a success we can safely assume
    the host is up and listing on port x. If the connection fails for any
    other reason we assume the host is down and the port is closed.'''

    # Create and configure the socket.
    sock = socket.socket()
    sock.settimeout(timeout)

    # the SO_REUSEADDR flag tells the kernel to reuse a local
    # socket in TIME_WAIT state, without waiting for its natural
    # timeout to expire.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Like connect(address), but return an error indicator instead
    # of raising an exception for errors returned by the C-level connect()
    # call (other problems, such as “host not found,” can still raise exceptions).
    # The error indicator is 0 if the operation succeeded, otherwise the value of
    # the errnovariable. This is useful to support, for example, asynchronous connects.
    connected = sock.connect_ex((target_ip_address, target_port)) == 0

    # Mark the socket closed.
    # The underlying system resource (e.g. a file descriptor)
    # is also closed when all file objects from makefile() are closed.
    # Once that happens, all future operations on the socket object will fail.
    # The remote end will receive no more data (after queued data is flushed).
    sock.close()

    # return True if port is open or False if port is closed.
    return connected


def check_ports_sequential(target_ip_address: str, list_of_target_ports: List[int], timeout: float = 0.5) -> Dict[int, bool]:
    results = {}
    for target_port in list_of_target_ports:
        results[target_port] = check_port(target_ip_address, target_port, timeout)
    return results


con = check_port('178.62.102.230', 443)
print(con)

all = check_ports_sequential('178.62.102.230', [22, 443, 80, 8000, 8080, 9000])
print(all)