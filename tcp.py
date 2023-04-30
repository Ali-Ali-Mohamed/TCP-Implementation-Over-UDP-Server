import random
import struct
import threading
import time

class TCP:
    def __init__(self) -> None:
        self.src_port = None
        self.dst_port = None
        self.seq_num = 0
        self.ack_num = 0
        self.last_seq_num = 0
        self.last_message = None
        self.checksum = 0
        self.bytes_to_send = None
        self.syn = 0
        self.ack = 0
        self.fin = 0
        self.x = 0
        self.y = 0
        self.data = None

    def check_received(self, data):
        self.packet_decode()
        if self.validate_checksum() and self.seq_num == self.last_seq_num:
            self.stop_timer()
            self.last_seq_num = not self.last_seq_num
            self.data = "1111"
            self.start_timer()
        else:
            print("duplicate packet or wrong seq number")

    def handle(self, data, address):
        self.packet_decode(data)

        if self.validate_checksum(data) and self.seq_num == self.last_seq_num:
            self.stop_timer()
            if self.syn == 1:
                self.send(1)
                print("start connection")
            elif self.ack == 1:
                print("confirming start of connection")
            elif self.fin == 1:
                print("closing connection")
            else:
                print("normal packet")

        else:
            pass    #wait for uncorrupted message

    def stop_timer(self):
        pass

    def timeout(self, data, address):
        pass

    def start_timer(self):
        pass

    def send(self, type):
        if type == 1:   #respond to start connection
            self.ack = 1
            self.syn = 1
            #self.x = 0
            #self.y = 0
            #self.last_seq_num = self.seq_num
            #self.seq_num = 1  # random number
            #get checksum
            #self.bytes_to_send = 1

        elif type == 2:
            pass

        #elif type == 3:

        #elif type == 4:

    def get_flags(self):
        binary = bin(self.flags)
        ack = binary[14]
        rst = binary[16]
        syn = binary[17]
        fin = binary[18]

        return ack, rst, syn, fin

    def divide(self, message: bytes):
        packets = []
        for i in range(0, len(message), 4):
            packet = message[i: i + 4]
            packets.append(packet)
        return packets

    def str_to_bytes(self, message: str) -> bytes:
        return message.encode()

    def str_to_bin(self, message: str) -> str:
        return ''.join(format(ord(char), '08b') for char in message)

    def bytes_to_str(self, encoded: bytes) -> str:
        return encoded.decode()

    def bin_to_str(self, binary: str):
        str_data = ''

        for i in range(0, len(binary), 8):
            temp_data = binary[i:i + 8]
            decimal = int(temp_data, 2)
            str_data += chr(decimal)

        return str_data

    def bin_to_bytes(self, binary: str) -> bytes:
        return int(''.join(binary), 2).to_bytes(len(''.join(binary)) // 8, byteorder='big')

    def calc_checksum(self, packet: str) -> str:
        # Divide each packet into 4 partitions of 8 bits
        c1 = packet[0:8]
        c2 = packet[8:8 * 2]
        c3 = packet[8 * 2:8 * 3]
        c4 = packet[8 * 3:8 * 4]

        # Calculating the binary sum of packets
        Sum = bin(int(c1, 2) + int(c2, 2) + int(c3, 2) + int(c4, 2))[2:]

        # Adding the overflow bits
        if len(Sum) > 8:
            x = len(Sum) - 8
            Sum = bin(int(Sum[0:x], 2) + int(Sum[x:], 2))[2:]
        if len(Sum) < 8:
            Sum = '0' * (8 - len(Sum)) + Sum

        # Calculating the complement of sum
        checksum = ''
        for i in Sum:
            if i == '1':
                checksum += '0'
            else:
                checksum += '1'
        return checksum

    def validate_checksum(self, received: str, checksum: str):
        # Divide each packet into 4 partitions of length 8 bits
        c1 = received[0:8]
        c2 = received[8:8 * 2]
        c3 = received[8 * 2:8 * 3]
        c4 = received[8 * 3:8 * 4]

        # Calculating the binary sum of packets + checksum
        ReceiverSum = bin(int(c1, 2) + int(c2, 2) + int(checksum, 2) +
                          int(c3, 2) + int(c4, 2) + int(checksum, 2))[2:]

        # Adding the overflow bits
        if len(ReceiverSum) > 8:
            x = len(ReceiverSum) - 8
            ReceiverSum = bin(int(ReceiverSum[0:x], 2) + int(ReceiverSum[x:], 2))[2:]

        # Calculating the complement of sum
        ReceiverChecksum = ''
        for i in ReceiverSum:
            if i == '1':
                ReceiverChecksum += '0'
            else:
                ReceiverChecksum += '1'

        final_sum = bin(int(checksum, 2) + int(ReceiverChecksum, 2))[2:]

        final_comp = ''
        for i in final_sum:
            if i == '1':
                final_comp += '0'
            else:
                final_comp += '1'

        if int(final_comp, 2) == 0:
            return True
        return False

    def generate_false_checksum(self, checksum: str) -> str:
        ind = random.choice(range(len(checksum)))
        false_checksum = list(checksum)
        false_checksum[ind] = '1' if false_checksum[ind] == '0' else '0'
        return ''.join(false_checksum)

    def corrupt_packet(self, packet: str) -> str:
        ind = random.choice(range(len(packet)))
        false_packet = list(packet)
        false_packet[ind] = '1' if false_packet[ind] == '0' else '0'
        return int(''.join(false_packet), 2).to_bytes(len(''.join(false_packet)) // 8, byteorder='big')

    def check_bytes(self, x: int, y: int, data: str) -> str:
        if x == 0 and y == 0:
            return data
        elif x == 0 and y == 1:
            data = data[0] + data [1] + data[2]
            return data
        elif x == 1 and y == 0:
            data = data[0] + data[1]
            return data
        elif x == 1 and y == 1:
            data = data[0]
            return data

    # x and y are used to mark the useless bytes in databytes
    def packet_encode(self, seq_num: str, ack_num: str, checksum: str, ack: str, fin: str,
                      x: str, y: str, data:str) -> bytes:
        segment = struct.pack('hhhhhhhhh4s', self.src_port, self.dst_port, seq_num, ack_num, checksum,
                              ack, fin, x, y, data.encode())
        return segment

    def packet_decode(self, packet: bytes) -> str:
        self.src_port, self.dst_port, self.seq_num, self.ack_num, self.checksum, self.syn, self.ack,\
            self.fin, x, y, data = struct.unpack('hhhhhhhhhhh4s', packet)
        data = data.decode()
        #print(src_port, dst_port, seq_num, ack_num, checksum, ack, fin, x, y, data)

    def packet_len(self, packet: str) -> [str, str]:
        if len(packet) == 4:
            return [0, 0]
        elif len(packet) == 3:
            return [0, 1]
        elif len(packet) == 2:
            return [1, 0]
        elif len(packet) == 1:
            return [1, 1]


t = TCP(1, 2)

packet = 'wsgh'
x = t.packet_len(packet)[0]
y = t.packet_len(packet)[1]
t.packet_decode(t.packet_encode(0000, 1, 11, 1, 0, x, y, packet))
packet_bin = t.str_to_bin(packet)
sum = t.calc_checksum(packet_bin)
print(sum)
