import binascii
import socket as syssock
import struct
import sys
from threading import Thread
import time
import random
from collections import namedtuple

# Acknowledgement number
ACK_NO = 1

# Synchronization number
SYN = 1

# Defining N for Go Back N, randomly assigned right now
N_PACKETS_LIMIT = 5


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
    '''
    class cs352struct:
        def __init__(self):
            # Version 1 of RDP.
            self.version = b'x\01'

            # Set flags to what they are given as in the prompt
            self.flags = dict(
                [("SYN", b'\x01'), ("FIN", b'\x02'), ("ACK", b'\x04'), ("RESET", b"\x08"), ("HAS_OPT", b"\xA0")])

            # Ignore these two for now. just setting them to zero
            self.opt_ptr = b"\x00"
            self.protocol = b"\x00"

            # The length of the header in bytes
            self.header_len = b'\x00'

            # Set checksum to 0 for now.
            self.checksum = b'\x00'

            # Set receiving port and destination port.
            self.source_port = tx_port
            self.dest_port = rx_port

            # Set sequence number to a random number
            self.sequence_no = random.randrange(1, 10).to_bytes()
            # Set ack_num to SYN?????
            self.ack_no = self.flags["SYN"]

            # Ignore window for now
            self.window = b'\x00'

            # Each payload will be 65k bytes maximum
            self.payload_len = (65000).to_bytes()

            # Create CS352 Struct
            self.sock352PktHdrData = '!BBBBHHLLQQLL'
            self.cs352struct = struct.Struct(self.sock352PktHdrData)
    '''

    # should use the struct to initialize an object
    def __init__(self):  # fill in your code here
        # Version 1 of RDP.
        self.version = b'x\01'

        # Set flags to what they are given as in the prompt
        self.flags = dict(
            [("SYN", b'\x01'), ("FIN", b'\x02'), ("ACK", b'\x04'), ("RESET", b"\x08"), ("HAS_OPT", b"\xA0")])

        # Ignore these two for now. just setting them to zero
        self.opt_ptr = b"\x00"
        self.protocol = b"\x00"

        # The length of the header in bytes
        self.header_len = b'\x00'

        # Set checksum to 0 for now.
        self.checksum = b'\x00'

        # Set receiving port and destination port.
        self.source_port = tx_port
        self.dest_port = rx_port

        # Set sequence number to a random number
        self.sequence_no = random.randrange(1, 10).to_bytes()

        # Set ack_num to SYN?????
        self.ack_no = self.flags["SYN"]

        # Ignore window for now
        self.window = b'\x00'

        # Each payload will be 65k bytes maximum
        self.payload_len = (65000).to_bytes()

        cs352struct = namedtuple('CS352 Struct', 'version flags opt_ptr protocol header_len checksum source_port dest_port sequence_no ack_no window payload_len')

        self.sock352PktHdrData = '!BBBBHHLLQQLL'

        self.header_struct = cs352struct()
        # Store address to send to
        self.address = None

        # Booleans to state whether we are connected and listening
        self.isConnected = None
        self.isListening = None

        # Create a socket
        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        return

    # TODO: fix this
    def __pack_struct__(self, payload_length, cs352tuple):
        return struct.pack(self.version, binascii.a2b_hex(self.flags.__str__()), self.opt_ptr, self.protocol
                              , self.header_len, self.checksum, binascii.a2b_hex(self.source_port),
                              binascii.a2b_hex(self.dest_port), self.sequence_no, self.ack_no, self.payload_len)

    # TODO: fix this
    def __unpack_struct__(self):
        return self.cs352struct._make(struct.unpack(self.sock352PktHdrData, ))

    # Bind to a port (from server perspective)
    # Which probably means to set the variables equal to
    # the port.
    def bind(self,address):
        (null_val, self.Rxport) = address
        return self.Rxport

    # This function is to create a connection from client perspective
    def connect(self,address):  # fill in your code here
        (self.address, self.Rxport) = address

        # 3-way handshake from perspective of client

        # Send SYN first
        self.sock.send(self.flags["SYN"])

        # Receive ACK which should be SYN + 1
        # Also receive SEQ
        # Convert the obtained bytes to ascii
        result_bin = self.sock.recv()

        # Convert the bytes to ascii
        result_ascii = binascii.b2a_hex(result_bin)

        # Split the obtained result by a comma since that is
        # how it is sent in accept(). The first value is ACK,
        # the second is SEQ
        [ack, seq] = result_ascii.split(",")

        # If we get the wrong ack, we do ??????
        # possibly just return -1
        if not ack == self.flags["SYN"] + 1:
            return -1

        # Send SEQ + 1 as the acknowledgement
        buffer = seq + 1
        self.sock.send(buffer)
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        return

    # This function is to create a connection from the server perspective.
    # Here we must implement a 3 way handshake.
    def accept(self):
        # first wait for an incoming input from server
        # which sends the SYN number.
        syn_bin = self.sock.recv()

        # Convert to ASCII
        syn_ascii = int(binascii.b2a_hex(syn_bin))

        # ACK = syn + 1
        syn_ascii += 1

        # sequence number is random
        self.sequence_no = random.randrange(1, 20)

        # The returned buffer should be of the form
        # "ack, syn" where ack = syn + 1 and sequence number is just random
        buffer = syn_ascii + "," + self.sequence_no
        binary_buff = binascii.a2b_hex(buffer)

        self.sock.send(binary_buff)

        # Receive the last acknowledgement
        # Convert to ascii
        last_ack_bin = self.sock.recv()
        last_ack_ascii = int(binascii.b2a_hex(last_ack_bin))

        if not last_ack_ascii == self.sequence_no + 1:
            return -1

        # Have no idea what to return
        (clientsocket, address) = (1,1)  # change this to your code 
        return (self.sock,address)

    # Close connection if last packet received
    # Otherwise, set close variable
    # TODO: implement the TCP termination 4- way handshake here
    def close(self):   # fill in your code here
        # To close we need to first send a FIN
        # then we should receive an ACK
        # Then, we should receive a FIN a
        # and we should send an ACK

        # Send FIN based on the flags value

        # Receive ACK. It should be FIN + 1?

        # Receive FIN. It should be

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
    def send(self,buffer):
        # get the length of the buffer and split it according to the
        # the size of the packets (65k bytes + header). The value of N
        # should be the size of the buffer divided by 65 k. Maybe this will change.
        lenbuff = len(buffer)
        N_PACKETS_LIMIT = lenbuff/65000

        # A "pointer" which holds which part of the buffer
        # we are sending currently.
        ptr = 0

        # function to receive acknowledgments
        # The function receives the buffer and N, as arguments.
        def recvacks(buffer, n_packets):
            num_acks = 0
            start_time = time.time()
            while num_acks < n_packets and (time.time() - start_time) < 100:
                ack = self.sock.recv()


            return

        # Variable to count the number of bytes sent.
        bytessent = 0     # fill in your code here


        while not bytessent == lenbuff:
            packet = struct.pack(fmt='i',)
            if packet + 65000 < lenbuff:
                packet += "\n" + buffer[ptr:(ptr+65000)]
            else:
                packet += "\n" + buffer[ptr:lenbuff-1]

            self.sock.send()

            if ptr > lenbuff - 65000:
                pass
            else:
                ptr += 65000

        thread_recv = Thread(target=recvacks, args=(buffer, N_PACKETS_LIMIT))
        thread_recv.start()
            # when we send we want to get an acknowledgement back

        start_time = time.time()
        thread_recv.join(timeout=100)
        if time.time() - start_time >= 100:
            return self.send(buffer)

        return bytessent

    # For this function, we just receive data and send an acknowledgement.
    # That part should be easy.
    # But, the harder part is to rearrange all of the packets in the order they should
    # be in. A solution I was thinking of is to sort by SYN values.
    # TODO: convert from ascii to binary and back
    def recv(self,nbytes):
        # Store the bytes into this buffer
        bytesreceived = 0     # fill in your code here

        # This list stores all of the packets received.
        # In the end, we can sort this list and put the packets in order
        packet_list = []

        # Keep receiving packets until we reach the number of bytes
        # we want to obtain
        start_time = time.time()

        # Keep obtaining packets until we
        while (not sys.getsizeof(bytesreceived) == nbytes) and time.time()-start_time < 100:
            #recieve data from the server
            data_recv = self.sock.recv(nbytes)

            # iterate the amount of bytes we received
            bytesreceived += + sys.getsizeof(data_recv)
            packet_list.append(data_recv)

            # send acknowledgement
            self.sock.send(ACK_NO)

        if time.time() - start_time >= 100:
            self.recv(nbytes)

        return self.reorder()
        # return bytesreceived

    # TODO: Sort by received ACK number
    def reorder(self, packet_list):
        packet_list.sort()
    


