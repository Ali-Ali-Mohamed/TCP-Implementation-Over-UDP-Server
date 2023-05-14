from tcp import TCP


class TCPServer:
    def __init__(self, host='127.0.0.1', port=9999):
        self.hhost = host
        self.pport = port

    def start(self):
        s = TCP(20001, 20002, 'localhost', 'localhost', 1024, 50)
        print('Server is Listening')
        while True:
            data = s.receiver()
            print("data: ", data)

            response = self.handle_request(data)

            print(response)
            s.sender(response.decode())
            print()

    def handle_request(self, data):
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data

