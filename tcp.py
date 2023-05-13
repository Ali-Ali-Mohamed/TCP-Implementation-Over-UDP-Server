import os
import threading
import time
import random
import struct
from PyQt5.QtCore import QTimer
import socket

gdgdf
class TCP:
    def __init__(self, src_port: int, dst_port: int, src_ip: str, dst_ip: str, buffer_size: int,
                 timeout: int) -> None:
        self.dst_ip = dst_ip
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_port = dst_port

        self.seg = None
        self.resent_msg = None
        self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        self.buffer_size = buffer_size - 10
        self.timeout = timeout

        self.ack_timer = QTimer(None)
        self.ack_timer.timeout.connect(lambda: self.resend(self.resent_msg, self.last_seq_num))

    def bin_to_str(self, binary: str):
        str_data = ''
        for i in range(0, len(binary), 8):
            temp_data = binary[i:i + 8]
            decimal = int(temp_data, 2)
            str_data += chr(decimal)
        return str_data

    def encode_flags(self, ack_num, seq_num, syn, ack, fin):
        flags = '000'
        flags += '1' if ack_num else '0'
        flags += '1' if seq_num else '0'
        flags += '1' if syn else '0'
        flags += '1' if ack else '0'
        flags += '1' if fin else '0'
        return int(flags, 2)

    def decode_flags(self, flags):
        return bool(16 & flags), bool(8 & flags), bool(4 & flags), bool(2 & flags), bool(1 & flags)

    def get_checksum(self, data, inplace=True):
        sum = 0
        for char in data:
            sum += ord(char)
            sum = bin(sum)[2:]
            if len(sum) > 8:
                sum = bin(int(sum[1:], 2) + 1)
            elif len(sum) < 8:
                sum = '0' * (8 - len(sum)) + sum
            sum = int(sum, 2)

        sum = bin(sum)[2:]

        checksum = ''
        for i in sum:
            if i == '1':
                checksum += '0'
            else:
                checksum += '1'
        if inplace:
            self.checksum = int(checksum, 2)
        else:
            return int(checksum, 2)

    def divide(self, message: str) -> list[str]:
        packets = []
        for i in range(0, len(message), self.buffer_size):
            if i + self.buffer_size <= len(message):
                packet = message[i: i + self.buffer_size]
                packets.append(packet)
            else:
                packet = message[i:]
                packets.append(packet)
        return packets

    def validate_checksum(self, received: str, checksum: int):
        received_sum = self.get_checksum(received, inplace=False)
        return received_sum == checksum

    def generate_false_checksum(self, checksum: int) -> int:
        checksum = bin(checksum)[2:]
        ind = random.choice(range(len(checksum)))
        false_checksum = list(checksum)
        false_checksum[ind] = '1' if false_checksum[ind] == '0' else '0'
        return int(''.join(false_checksum), 2)

    def corrupt_packet(self, packet: str) -> str:
        bits = ''
        for char in packet:
            char = bin(ord(char))[2:]
            char = '0' * (8 - len(char)) + char
            bits += char
        ind = random.choice(range(len(bits)))
        false_packet = list(bits)
        false_packet[ind] = '1' if false_packet[ind] == '0' else '0'
        word = self.bin_to_str(''.join(false_packet))
        return word

    def packet_encode(self, checksum: int, data: str, ack_num, seq_num, syn, ack, fin) -> bytes:
        flags = self.encode_flags(ack_num, seq_num, syn, ack, fin)
        segment = struct.pack('hhhh' + str(self.buffer_size) + 's', self.src_port, self.dst_port, checksum, flags,data.encode())
        return segment

    def packet_decode(self, packet: bytes):
        dst_port, src_port, checksum, flags, data = struct.unpack('hhhh' + str(self.buffer_size) + 's', packet)
        data = data.decode()
        data = self.crop(data.encode())
        ack_num, seq_num, syn, ack, fin = self.decode_flags(flags)
        return dst_port, src_port, checksum, ack_num, seq_num, syn, ack, fin, data

    def crop(self, data: bytes):
        count = 0
        for byte in data:
            if byte == 0:
                break
            count += 1
        data = data.decode()
        data = data[:count]
        return data

    def resend(self, resent: str, num=0):
        if resent.lower() == 'seg':
            self.connection.sendto(self.seg, (self.dst_ip, self.dst_port))
        elif resent.lower() == 'syn':
            self.connection.sendto(self.packet_encode(0, '', 0, 0, 1, 0, 0), (self.dst_ip, self.dst_port))
        elif resent.lower() == 'ack':
            self.connection.sendto(self.packet_encode(0, '', 0, num, 0, 1, 0), (self.dst_ip, self.dst_port))
        elif resent.lower() == 'synack':
            self.connection.sendto(self.packet_encode(0, '', 0, 0, 1, 1, 0), (self.dst_ip, self.dst_port))
        elif resent.lower() == 'fin':
            self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 0, 1), (self.dst_ip, self.dst_port))
        elif resent.lower() == 'finack':
            self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 1, 1), (self.dst_ip, self.dst_port))

    def sender(self, message: str):
        print('Send SYN')
        self.seg = self.packet_encode(0, '', 0, 0, 1, 0, 0)
        self.connection.sendto(self.seg, (self.dst_ip, self.dst_port))
        self.ack_timer.start(self.timeout)
        print('SYN Sent')

        print('Waiting For SYNACK')
        received_msg, address = self.connection.recvfrom(self.buffer_size + 10)
        self.ack_timer.stop()
        dst_port, src_port, received_checksum, received_ack_num, received_seq_num, received_syn, received_ack, received_fin, received_data = self.packet_decode(received_msg)
        if received_syn and received_ack:
            print('SYNACK Received')
        else:
            print('Error')
            raise RuntimeError('Error in Handshaking')

        print('Send ACK')
        self.seg = self.packet_encode(0, '', 0, 0, 0, 1, 0)
        self.connection.sendto(self.seg, address)
        self.ack_timer.start(self.timeout)
        print('ACK Sent')

        packets = self.divide(message)
        i = 0
        ack_num = 0
        seq_num = 0
        while i < len(packets):
            message = packets[i]
            checksum = self.get_checksum(message)
            self.seg = self.packet_encode(self.checksum, message, ack_num, seq_num, 0, 0, 0)
            self.connection.sendto(self.seg, address)
            #self.resent_msg = 'seg'
            self.ack_timer.start(self.timeout)
            received_msg, address = self.connection.recvfrom(self.buffer_size + 10)
            self.ack_timer.stop()
            dst_port, src_port, received_checksum, received_ack_num, received_seq_num, received_syn, received_ack, received_fin, received_data = self.packet_decode(received_msg)
            if received_ack_num != seq_num or not received_ack:
                continue
            seq_num = 1 if received_seq_num == 0 else 0
            i += 1

        print("Closing the Connection")
        print("Send FIN")
        self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 0, 1), address)
        print("FIN sent")

        print("Receive FINACK")
        received_fin_ack, address = self.connection.recvfrom(self.buffer_size + 10)
        dst_port, src_port, checksum, ack_num, seq_num, syn, ack, fin, data = self.packet_decode(received_fin_ack)
        if fin and ack:
            print("FINACK Received")
        else:
            print('Error')
            raise RuntimeError('Error in Closing')

        print("Send ACK to close connection")
        self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 1, 1), address)
        print("Ack to close connection sent")
        print("Connection Closed")

    def receiver(self):
        self.connection.bind((self.dst_ip, self.dst_port))
        received_syn, address = self.connection.recvfrom(self.buffer_size + 10)
        dst_port, src_port, checksum, ack_num, seq_num, syn, ack, fin, data = self.packet_decode(received_syn)
        if syn:
            print('SYN Received')
        else:
            print('Error')
            raise RuntimeError('Error in Handshaking')

        print("Send SYNACK")
        self.seg = self.packet_encode(0, '', 0, 0, 1, 1, 0)
        self.connection.sendto(self.seg, address)
        print('SYNACK Sent')
        print("Receive ACK")
        received_ack, address = self.connection.recvfrom(self.buffer_size + 10)
        dst_port, src_port, checksum, ack_num, seq_num, syn, ack, fin, data = self.packet_decode(received_ack)
        if ack:
            print('ACK Received')
        else:
            print('Error')
            raise RuntimeError('Error in Handshaking')

        message = ''
        while True:
            packet, address = self.connection.recvfrom(self.buffer_size + 10)
            dst_port, src_port, checksum, ack_num, seq_num, syn, ack, fin, data = self.packet_decode(packet)

            if fin and not ack:
                print("FIN Received")
                print("Send FINACK")
                self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 1, 1), address)
                print("FINACK Sent")

            if fin and ack:
                print("ACK to close connection is received")
                break

            # if not self.validate_checksum(data, checksum):
            #     print("Error in the message")
            #     print("Waiting the sender to send it again")
            #     continue

            if seq_num:
                self.connection.sendto(self.packet_encode(0, '', 1, 1, 0, 1, 0), address)
            elif not seq_num:
                self.connection.sendto(self.packet_encode(0, '', 0, 0, 0, 1, 0), address)

            message += data
        print("Message { " + message + " }")
