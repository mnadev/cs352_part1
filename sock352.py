import binascii
import socket as syssock
import struct
import sys
from threading import Thread
import time
import random
from collections import namedtuple

# constants defined here
SOCK352_SYN = b'\x01'
SOCK352_FIN = b'\x02'
SOCK352_ACK = b'\x04'
SOCK352_RESET = b'\x08'
SOCK352_HAS_OPT = b'\xA0'

# Defining N for Go Back N, randomly assigned right now
N_PACKETS_LIMIT = 10

# creating the port variables for receiving and sending processes
global tx_port
global rx_port

# default values for ports
rx_port = 1111
tx_port = 1111

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

# basically only set the port numbers
def init(UDPportTx,UDPportRx):   # initialize your UDP socket here
    global tx_port
    global rx_port

    rx_port = UDPportRx
    tx_port = UDPportTx


class socket:
    # should use the struct to initialize an object
    def __init__(self):  # fill in your code here
        # Version 1 of RDP.
        self.version = b'x\01'

        # Ignore these two for now. just setting them to zero
        self.opt_ptr = b"\x00"
        self.protocol = b"\x00"

        # The length of the header in bytes
        self.sock352PktHdrData = '!BBBBHHLLQQLL'

        self.header_struct = struct.Struct(self.sock352PktHdrData)

        # By my calculations, header should be 36 bytes
        # Anyways, we store both the int version and the bytes version here.
        # It's annoying to convert back and forth.
        self.header_len_int = struct.calcsize(self.sock352PktHdrData)
        self.header_len = str(self.header_len_int).strip().decode("hex")

        # Set checksum to 0 for now.
        self.checksum = b'\x00\x00'

        # Set receiving port and destination port.
        # Converted to bytes
        self.source_port = tx_port
        self.dest_port = rx_port

        # Set sequence number to a random number
        self.sequence_no = b'\x00\x00\x00\x00\x00\x00\x00\xAD'

        # Set ack_num to SYN?????
        self.ack_no = b'\x00\x00\x00\x00\x00\x00\x00\x01'

        # Ignore window for now
        self.window = b'\x00\x00\x00\x00'

        # Each payload will be 64k bytes maximum
        # 64k in bytes is what is listed below
        self.payload_len_int = 64000
        self.payload_len = b'\x00\x00\xFA\x00'

        self.cs352struct = namedtuple('cs352_struct', 'version flags opt_ptr protocol header_len checksum source_port dest_port sequence_no ack_no window payload_len')

        # Store address to send to
        # should be tuple of (ip_addr, port)
        self.address = None

        # Booleans to state whether we are connected and listening
        self.isConnected = None
        self.isListening = None

        # Create a socket
        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        return

    # TODO: fix this
    def __pack_struct__(self, cs352tup, payload_length=64000):
        return struct.pack(cs352tup.version, cs352tup.flags, cs352tup.opt_ptr, cs352tup.protocol
                              , cs352tup.header_len, cs352tup.checksum, binascii.a2b_hex(cs352tup.source_port),
                              binascii.a2b_hex(cs352tup.dest_port), cs352tup.sequence_no, cs352tup.ack_no, cs352tup.payload_len)


    def __unpack_struct__(self, buffer):
        return self.cs352struct._make(struct.unpack(self.sock352PktHdrData, buffer))

    # Bind to a port (from server perspective)
    # Which probably means to set the variables equal to
    # the port.
    def bind(self,address):
        (null_val, self.Rxport) = address
        self.sock.bind((null_val, rx_port))
        return

    # This function is to create a connection from client perspective
    def connect(self,address):  # fill in your code here
        (self.dest_address, self.unusedport) = address

        self.sock.bind((self.address, rx_port))

        # 3-way handshake from perspective of client

        # Send SYN first
        send_tuple = self.cs352struct(version=self.version,flags=SOCK352_SYN,opt_ptr=self.opt_ptr,
                                      protocol=self.protocol,header_len=self.header_len,
                                      checksum=self.checksum,
                                      source_port=self.source_port,dest_port=self.dest_port,
                                      sequence_no=self.sequence_no,ack_no=self.ack_no,
                                      window=self.window,payload_len=0)

        self.sock.send(self.__pack_struct__(send_tuple))

        # Receive ACK which should be (SYN | ACK) & ACK
        # Also receive SEQ
        # Convert the obtained bytes to ascii
        result_bin, self.dest_address = self.sock.recvfrom(self.header_len_int)

        # Convert the bytes to struct
        result_struct = self.__unpack_struct__(result_bin)

        # If we get the wrong flag, we do ??????
        # possibly just return -1
        if not result_struct.flags == SOCK352_ACK:
            print "Unable to connect"
            return -1

        # Send SYN first
        send_tuple = self.cs352struct(version=self.version, flags=SOCK352_SYN, opt_ptr=self.opt_ptr,
                                      protocol=self.protocol, header_len=self.header_len,
                                      checksum=self.checksum,
                                      source_port=self.source_port, dest_port=self.dest_port,
                                      sequence_no=self.sequence_no, ack_no=self.ack_no,
                                      window=self.window, payload_len=0)

        self.sock.send(self.__pack_struct__(send_tuple))
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        return

    # This function is to create a connection from the server perspective.
    # Here we must implement a 3 way handshake.
    def accept(self):
        # first wait for an incoming input from client
        # which sends the SYN number.
        first_pack, self.dest_address = self.sock.recvfrom(self.header_len_int)

        # Convert to ASCII
        first_pack_struct = self.__unpack_struct__(first_pack)

        if not first_pack_struct.flags == SOCK352_SYN:
            print "Failed to connect"
            return -1

        # The returned buffer have flag equal to ACK to acknowledge
        send_tuple = self.cs352struct(version=self.version, flags=SOCK352_ACK, opt_ptr=self.opt_ptr,
                                      protocol=self.protocol, header_len=self.header_len,
                                      checksum=self.checksum,
                                      source_port=self.source_port, dest_port=self.dest_port,
                                      sequence_no=self.sequence_no, ack_no=self.ack_no,
                                      window=self.window, payload_len=0)

        binary_buff = self.__pack_struct__(send_tuple)

        self.sock.sendto(binary_buff, (self.dest_address, self.dest_port))

        # Receive the last acknowledgement
        # Convert to ascii
        last_ack_bin = self.sock.recv(self.header_len_int)

        # Convert the bytes to struct
        result_struct = self.__unpack_struct__(last_ack_bin)

        # If we don't receive acknowledgement
        if not result_struct.flags == SOCK352_ACK:
            print "Failed to connect"
            return -1

        # Have no idea what to return
        (clientsocket, address) = (self.sock, self.dest_address)  # change this to your code
        return (clientsocket, address)

    # Close connection if last packet received
    # Otherwise, set close variable
    # TODO: implement the TCP termination 4- way handshake here
    def close(self):   # fill in your code here
        # To close we need to first send a FIN
        # then we should receive an ACK
        # Then, we should receive a FIN a
        # and we should send an ACK

        # Send FIN.
        send_tuple = self.cs352struct(version=self.version, flags=SOCK352_FIN, opt_ptr=self.opt_ptr,
                                      protocol=self.protocol, header_len=self.header_len,
                                      checksum=self.checksum,
                                      source_port=self.source_port, dest_port=self.dest_port,
                                      sequence_no=self.sequence_no, ack_no=self.ack_no,
                                      window=self.window, payload_len=0)

        binary_buff = self.__pack_struct__(send_tuple)
        self.sock.sendto(binary_buff)

        # Receive ACK and FIN.
        # first wait for an incoming input from client
        # which sends the ACK or FIN number.
        first_pack, address = self.sock.recvfrom(self.header_len_int)

        # Convert to ASCII
        first_pack_struct = self.__unpack_struct__(first_pack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK or FIN ????
        if not (first_pack_struct.flags == SOCK352_ACK || first_pack_struct.flags == SOCK352_FIN):
            return -1

        recievedFIN = False
        receivedACK = False

        if first_pack_struct.flags == SOCK352_ACK:
            receivedACK = True
        else:
            recievedFIN = True

        second_pack, address = self.sock.recvfrom(self.header_len_int)

        # Convert to ASCII
        second_pack_struct = self.__unpack_struct__(second_pack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK or FIN ????
        if not (second_pack_struct.flags == SOCK352_ACK || second_pack_struct.flags == SOCK352_FIN):
            return -1

        # Check which flag we recieved based on what we alreday recieved. If we recieved an ACK, then
        # check for FIN. Otherwise, check for ACK.
        if receivedACK:
            if not second_pack_struct.flags == SOCK352_FIN:
                return -1
        else:
            if not second_pack_struct.flags == SOCK352_ACK:
                return -1

        # SEND ACK
        send_tuple = self.cs352struct(version=self.version, flags=SOCK352_ACK, opt_ptr=self.opt_ptr,
                                      protocol=self.protocol, header_len=self.header_len,
                                      checksum=self.checksum,
                                      source_port=self.source_port, dest_port=self.dest_port,
                                      sequence_no=self.sequence_no, ack_no=self.ack_no,
                                      window=self.window, payload_len=0)

        binary_buff = self.__pack_struct__(send_tuple)
        self.sock.sendto(binary_buff, address=(self.dest_address, self.dest_port))
        return 

    # This function implements go back N.
    # We should use one thread to send the data and one thread to
    # receive the acks.
    # We should also send the length of the file. Return the total number of total
    # bytes. Keep sending data while there are bytes left.
    # We should check if the receiving thread times out. If so,
    # resend the data. While acks are beings sent, we mark for which
    # packets, the acks are received.
    # TODO: convert from ascii to binary and back
    # TODO: Synchronize the SEQ, SYN and ACK values
    def send(self,buffer):

        # function to receive acknowledgments
        # The function receives the buffer and N, as arguments.
        # Return 1 means all acknowledgements received.
        # Return -1 means none received.
        # TODO: Verify that the acks are actually unique and what we should obtain rather then counting the number of received messages as acks
        def recvacks(buffer, n_packets):
            num_acks = 0
            start_time = time.time()
            while num_acks < n_packets and (time.time() - start_time) < 100:
                ack = self.sock.recv(self.header_len + 64000)
                num_acks += 1

            if num_acks < n_packets or time.time() - start_time >= 100:
                return -1

            return 1


        # get the length of the buffer and split it according to the
        # the size of the packets (65k bytes + header). The value of N
        # should be the size of the buffer divided by 65 k. Maybe this will change.
        lenbuff = len(buffer)

        # the buffer in bytes
        bin_buff = binascii.a2b_hex(buffer)

        N_PACKETS_LIMIT = 10

        # A "pointer" which holds which part of the buffer
        # we are sending currently.
        ptr = 0

        # Variable to count the number of bytes sent.
        bytessent = 0     # fill in your code here


        while not bytessent == lenbuff:
            packets_sent = 0
            while not packets_sent == N_PACKETS_LIMIT:
                header = self.cs352struct(version=self.version,flags=SOCK352_SYN,opt_ptr=self.opt_ptr,
                                          protocol=self.protocol,header_len=self.header_len,
                                          checksum=self.checksum,
                                          source_port=self.source_port,dest_port=self.dest_port,
                                          sequence_no=self.sequence_no,ack_no=self.ack_no,
                                          window=self.window,payload_len=0)

                # send a 64k bytes payload if we can
                if self.header_len + 64000 < lenbuff:
                    header = self.__pack_struct__(header)
                    packet = header + buffer[ptr:(ptr + 64000)]
                else:
                    # otherwise send the remaining
                    header.payload_len = (str(int(lenbuff - ptr - 1)).encode('hex'), 16)
                    header = self.__pack_struct__(header)
                    packet = header + buffer[ptr:lenbuff-1]

                self.sock.sendto(packet, address=(self.dest_address, self.dest_port))
                packets_sent += 1

                if ptr > lenbuff - 64000:
                    break
                else:
                    ptr += 64000


            # when we send we want to get an acknowledgement back for all N packets
            did_recv_all = recvacks(buffer, N_PACKETS_LIMIT)
            if did_recv_all == -1:
                return self.send(buffer)


        return bytessent

    # For this function, we just receive data and send an acknowledgement.
    # That part should be easy.
    # But, the harder part is to rearrange all of the packets in the order they should
    # be in. A solution I was thinking of is to sort by SYN values.
    # TODO: Synchronize the SEQ, SYN and ACK values
    # TODO: Implement a way to check if we are receiving FIN
    def recv(self,nbytes):
        # Store the bytes into this buffer
        bytesreceived = 0     # fill in your code here

        # This list stores all of the packets received.
        # In the end, we can sort this list and put the packets in order
        packet_list = []

        # Keep receiving packets until we reach the number of bytes
        # we want to obtain
        start_time = time.time()

        # Keep obtaining packets until we have recieved n bytes
        while sys.getsizeof(bytesreceived) < nbytes and time.time()-start_time < 1:
            # receive data from the server
            data_recv = self.sock.recv(nbytes)

            # Split up packet into header and data
            header = self.__unpack_struct__(data_recv[:self.header_len])
            data = data_recv[self.header_len:]
            packet_list.append((header, data))

            # iterate the amount of bytes we received
            bytesreceived += sys.getsizeof(data)

            # send acknowledgement, which should be SYN + sizeof(Data) ????
            new_header = header
            new_header.ack_no = new_header.flags + sys.getsizeof(data)
            new_header.payload_len = 0

            self.sock.send(self.__pack_struct__(new_header))

        packet_list = self.reorder(packet_list)

        # Get the bytes only and make it into a list
        bytes_list = [x[1] for x in packet_list]

        # Join all of the bytes together and return
        bytesreceived = bytes_list.join()
        return bytesreceived

    def reorder(self, packet_list):
        # Sort the list by the ack_num
        return packet_list.sort(key=lambda x: x[0].ack_no)

