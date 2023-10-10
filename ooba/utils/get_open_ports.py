import socket

def get_open_ports(start_port=0, end_port=10000, host='localhost'):
    open_ports = []
    for port in range(start_port, end_port+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            socket.setdefaulttimeout(1)
            result = s.connect_ex((host, port))  # returns 0 if the connection was successful
            if result == 0:
                open_ports.append(port)
    return open_ports