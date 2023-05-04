from tcp_server import TCPServer
from tcp import TCP
import datetime
import os


class HTTPServer(TCPServer):
    status_codes = {
        200: 'OK',
        400: 'Bad Request',
        404: 'Not Found',
    }
    Server = "myServer"

    def __init__(self):
        self.method = None
        self.uri = None
        self.http_version = None
        self.host = None
        self.req_body = None
        self.response_body = None
        self.response = None
        self.blank = b"\r\n"

    def parse_request(self, data):
        lines = data.split(b"\r\n")
        request = lines[0]
        header_line1 = lines[1]
        request_words = request.split(b" ")
        header_line1_words = header_line1.split(b" ")

        self.req_body = lines[2]
        self.method = request_words[0].decode()
        self.uri = request_words[1].decode()
        self.http_version = request_words[2].decode()
        self.host = header_line1_words[1].decode()
        ''' 
        http request format:
            
                GET /wanted_file.html HTTP/1.1\r\n
                Host: www-net.cs.umass.edu\r\n
                ...body..
                ...body...\r\n
        
        '''

    def handle_request(self, data):
        print("received request: ", data)
        self.parse_request(data)
        if self.method == "GET":
            return self.handle_get()
        elif self.method == "POST":
            return self.handle_post()
        else:
            return self.handle_invalid_method(400)

    def handle_get(self):
        file = self.uri.strip('/')
        print(file)

        if os.path.exists(file):
            code = 200
            with open(file, 'rb') as f:
                self.response_body = f.read()
        else:
            code = 404
            self.response_body = b"<h1>File Not Found</h1>"

        status = "{} {} {}\r\n".format(self.http_version, code, self.status_codes[code])
        status = status.encode()
        now = datetime.datetime.now()
        date = "Date: " + now.strftime("%a, %d %b %Y %H:%M:%S")
        date = date.encode()
        myserver = "Server: " + self.Server
        myserver = myserver.encode()
        response = b"".join([status, date, self.blank, myserver, self.blank, self.response_body])
        return response

    def handle_post(self):
        file = self.uri.strip('/')
        print(file)

        if os.path.exists(file):
            code = 200
            with open(file, 'w') as f:
                f.write(self.req_body.decode())
                self.response_body = b"<h1>File updated successfully</h1"
        else:
            code = 404
            self.response_body = b"<h1>File Not Found</h1>"

        status = "{} {} {}\r\n".format(self.http_version, code, self.status_codes[code])
        status = status.encode()
        now = datetime.datetime.now()
        date = "Date: " + now.strftime("%a, %d %b %Y %H:%M:%S")
        date = date.encode()
        myserver = "Server: " + self.Server
        myserver = myserver.encode()
        response = b"".join([status, date, self.blank, myserver, self.blank, self.response_body])
        return response

    def handle_invalid_method(self, code):
        status = "{} {} {}\r\n".format(self.http_version, code, self.status_codes[code])
        status = status.encode()
        now = datetime.datetime.now()
        date = "Date: " + now.strftime("%a, %d %b %Y %H:%M:%S")
        date = date.encode()
        myserver = "Server: " + self.Server
        myserver = myserver.encode()
        self.response_body = b"<h1>Bad Request</h1>"
        response = b"".join([status, date, self.blank, myserver, self.blank, self.response_body])
        return response


if __name__ == '__main__':
    server = HTTPServer()
    server.start()
