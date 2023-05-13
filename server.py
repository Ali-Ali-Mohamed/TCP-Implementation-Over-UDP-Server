import tcp
import socket

clientIP = "127.0.0.1"
clientPort = 20002

serverIP = "127.0.0.1"
serverPort = 20001

bufferSize = 1024

# Create a tcp socket at server side
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# t = tcp.TCP(serverPort, clientPort, serverIP, clientIP, bufferSize, 50)
t = tcp.TCP(clientPort, serverPort, clientIP, serverIP, bufferSize, 50)

print("TCP server up and listening")
t.receiver()
print("Message Received")