import tcp
import socket

clientIP = "127.0.0.1"
clientPort = 20002

serverIP = "127.0.0.1"
serverPort = 20001

msgFromClient = "Doneeeeeeee"
bytesToSend = str.encode(msgFromClient)

bufferSize = 1024

# Create a tcp socket at client side
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
t = tcp.TCP(clientPort, serverPort, clientIP, serverIP, bufferSize, 50)

print("Preparing to send message")
t.sender(msgFromClient)
print("Message Sent")