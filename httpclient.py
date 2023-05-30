import socket
from tcp import TCP


class HTTPClient:
    def __init__(self):
        self.method = None
        self.uri = None
        self.http_version = None
        self.host = None
        self.req_body = None
        self.response_body = None
        self.response = None
        self.blank = b"\r\n"

    def get_request(self, path, host, http_version):
        status = "GET {} HTTP/{}\r\n".format(path, http_version)
        status = status.encode()
        host = "Host: {}\r\n".format(host)
        host = host.encode()
        body = b"\r\n"
        blank = b"\r\n"

        return b"".join([status, host, body, blank])

    def post_request(self, path, host, http_version, message):
        status = "POST {} HTTP/{}\r\n".format(path, http_version)
        status = status.encode()
        host = "Host: {}\r\n".format(host)
        host = host.encode()
        body = message.encode()
        blank = b"\r\n"

        return b"".join([status, host, body, blank])


HOST = "localhost"
PATH = "/helo.html"
HTTP_V = "1.1"
POST_Message = "<html>" \
               "<head><title>POST</title></head>" \
               "<body><h1>POST changed this!!</h1><p>This is the updated hello page.</p></body>" \
               "</html>"

if __name__ == '__main__':
    client = HTTPClient()
    request = client.post_request(PATH, HOST, HTTP_V, POST_Message)

    c = TCP(20003, 20004, 'localhost', 'localhost', 1024, 50)
    sock = c.connection
    c.sender(request.decode())
    # sock.sendall(request)
    received = c.receiver()

    print("Sent:     {}".format(str(request)))
    print("Received: \n{}".format(received))
