import socket

localIP = "127.0.0.1"
localPort = 20001
bufferSize = 1024
msgFromServer = "Hello UDP Client"
to_be_sent_bytes = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")

SYN, address = UDPServerSocket.recvfrom(bufferSize)
print(SYN)
print(SYN.decode())
if SYN.decode() == 'SYN':
    print('SYN Received')
else:
    print('Error')
    raise RuntimeError('Error in Handshaking')

SYNACK = 'SYNACK'
UDPServerSocket.sendto(SYNACK.encode(), address)
print('SYNACK Sent')

ACK, address = UDPServerSocket.recvfrom(bufferSize)
if ACK.decode() == "ACK":
    print('ACK Received')
else:
    print('Error')
    raise RuntimeError('Error in Handshaking')


# Listen for incoming datagrams
while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0]

    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP = "Client IP Address:{}".format(address)

    print(clientMsg)
    print(clientIP)

    # Sending a reply to client
    UDPServerSocket.sendto(to_be_sent_bytes, address)
