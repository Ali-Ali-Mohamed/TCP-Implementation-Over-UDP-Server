import socket

msgFromClient = "Hello ana seif"

bytesToSend = str.encode(msgFromClient)

serverAddressPort = ("127.0.0.1", 20001)

bufferSize = 1024

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

print('Send SYN')
SYN = 'SYN'.encode()
UDPClientSocket.sendto(SYN, serverAddressPort)
print('SYN Sent')

print('Wait For SYNACK')
SYNACK = UDPClientSocket.recvfrom(bufferSize)[0]
if SYNACK.decode() == 'SYNACK':
    print('SYNACK Received')
else:
    print('Error')
    raise RuntimeError('Error in Handshaking')

print('Send ACK')
ACK = 'ACK'
UDPClientSocket.sendto(ACK.encode(), serverAddressPort)
print('ACK Sent')
# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)
