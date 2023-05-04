import socket


class TCPServer:
    def __init__(self, host='127.0.0.1', port=9999):
        self.hhost = host
        self.pport = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', 9999))
        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()
            print("Connected by", addr)
            data = conn.recv(50000)
            print("data: ", data)

            response = self.handle_request(data)

            print(response)

            conn.sendall(response)
            conn.close()

    def handle_request(self, data):
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data
