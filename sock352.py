import binascii
import socket as syssock
import struct
import sys
import random
from threading import Thread
import time
import math

# Mohammad Nadeem and Gregory Mellilo
# constants defined here
SOCK352_SYN = 0x01
SOCK352_FIN = 0x02
SOCK352_ACK = 0x04
SOCK352_RESET = 0x08
SOCK352_HAS_OPT = 0xA0

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

    # convert to int
    rx_port = int(UDPportRx)
    tx_port = int(UDPportTx)


class socket:
    # should use the struct to initialize an object
    def __init__(self):  # fill in your code here
        # Version 1 of RDP.
        self.version = 1

        # Ignore these two for now. just setting them to zero
        self.opt_ptr = 0
        self.protocol = 0

        # The length of the header in bytes
        self.sock352PktHdrData = '!BBBBHHLLQQLL'

        self.header_struct = struct.Struct(self.sock352PktHdrData)

        # Calculating the header size
        self.header_len = int(struct.calcsize(self.sock352PktHdrData))

        # Set checksum to 0 for now.
        self.checksum = 0

        # Set ports which are unused for this part
        # so they'll be set to random value
        self.source_port = 0
        self.dest_port = 0

        # Set sequence number to a random number
        self.sequence_no = 0

        # Set ack_num to 1 for now
        self.ack_no = 0

        # Ignore window for now
        self.window = 0

        # Each payload will be 64k bytes maximum
        # 64k in bytes is what is listed below
        # It could be less and we should account for that
        self.payload_len = 64000

        # Booleans to state whether we are connected and listening
        self.isConnected = False
        self.isListening = False

        # Create a socket using UDP and using IP
        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0',rx_port))

        self.didReceiveSizeFile = False

        self.resend = False

    # Bind to a port (from server perspective)
    # Which probably means to set the variable equal to
    # the port.
    def bind(self,address):
        return

    # This function is to create a connection from client perspective
    def connect(self,address):  # fill in your code here
        self.address = (address[0], tx_port)
        self.sock.settimeout(None)

        # 3-way handshake from perspective of client
        payload = (0)

        # Send SYN first
        first_syn_conn = self.header_struct.pack(self.version,SOCK352_SYN,self.opt_ptr,
                                      self.protocol,self.header_len,self.checksum,
                                      self.source_port,self.dest_port,
                                      self.sequence_no,self.ack_no,self.window,0)

        self.sock.sendto(first_syn_conn,self.address)

        # Receive ACK which should be ACK
        # Also receive SEQ
        # Convert the obtained bytes to ascii
        result_bin, addr = self.sock.recvfrom(self.header_len)

        # Convert the bytes to struct
        result_struct = self.header_struct.unpack(result_bin)

        # If we get the wrong flag, we do ??????
        # possibly just return -1
        if not result_struct[1] == SOCK352_ACK:
            print "Unable to connect"
            return -1

        # Send ACK
        second_syn_conn = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port, self.dest_port,self.sequence_no,
                                      self.ack_no,self.window,int(payload))

        self.sock.sendto(second_syn_conn, self.address)

        self.isConnected = True
        print "Connection Established"
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        self.isListening = True
        return

    # This function is to create a connection from the server perspective.
    # Here we must implement a 3 way handshake.
    def accept(self):
        self.sock.settimeout(None)

        # first wait for an incoming input from client
        # which sends the SYN number.

        first_pack, self.address = self.sock.recvfrom(self.header_len)

        # Convert to ASCII
        first_pack_struct = self.header_struct.unpack(first_pack)

        if not first_pack_struct[1] == SOCK352_SYN:
            print "Failed to connect"
            return -1

        # The returned buffer have flag equal to ACK to acknowledge
        first_ack = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port, self.dest_port,self.sequence_no,
                                      self.ack_no,self.window,0)

        self.sock.sendto(first_ack, self.address)

        # Receive the last acknowledgement
        # Convert to ascii
        last_ack_bin, self.dest_address = self.sock.recvfrom(self.header_len)

        # Convert the bytes to struct
        result_struct = self.header_struct.unpack(last_ack_bin)

        # If we don't receive acknowledgement, return with failure
        if not result_struct[1] == SOCK352_ACK:
            print "Failed to connect"
            return -1

        # Have no idea what to return
        (clientsocket, address) = (self,self.address)  # change this to your code
        self.isConnected = True
        print "Connection Established"

        return (self, address)

    # Close connection if last packet received
    # Otherwise, set close variable
    def close(self):   # fill in your code here
        # To close we need to first send a FIN
        # then we should receive an ACK
        # Then, we should receive a FIN a
        # and we should send an ACK
        self.sock.settimeout(1)

        # Send FIN.
        first_fin = self.header_struct.pack(self.version, SOCK352_FIN, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port,self.dest_port,self.sequence_no,
                                      self.ack_no,self.window,0)
        while True:
            try:
                self.sock.sendto(first_fin, self.address)
                break
            except syssock.timeout:
                continue

        # Receive ACK and FIN.
        # first wait for an incoming input from client
        # which sends the ACK or FIN number.
        while True:
            try:
                first_pack, address = self.sock.recvfrom(self.header_len)
            except syssock.timeout:
               continue

        # Convert to ASCII
        first_pack_struct = self.header_struct.unpack(first_pack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK or FIN ????
        if not (first_pack_struct[1] == SOCK352_ACK or first_pack_struct[1] == SOCK352_FIN):
            return -1

        recievedFIN = False
        receivedACK = False

        if first_pack_struct[1] == SOCK352_ACK:
            receivedACK = True
        else:
            recievedFIN = True

        try:
            second_pack, address = self.sock.recvfrom(self.header_len)
        except syssock.timeout:
            print "Connection terminated"
            return -1

        # Convert to ASCII
        second_pack_struct = self.header_struct.unpack(second_pack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK or FIN ????
        if not (second_pack_struct[1] == SOCK352_ACK or second_pack_struct[1] == SOCK352_FIN):
            return -1

        # Check which flag we recieved based on what we alreday recieved. If we recieved an ACK, then
        # check for FIN. Otherwise, check for ACK.
        if receivedACK:
            if not second_pack_struct[1] == SOCK352_FIN:
                return -1
        else:
            if not second_pack_struct[1] == SOCK352_ACK:
                return -1

        # SEND ACK
        final_ack = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                      self.protocol,self.header_len,self.checksum,self.source_port,
                                      self.dest_port,self.sequence_no, self.ack_no,
                                      self.window,0)

        try:
            self.sock.sendto(final_ack,self.address)
        except syssock.timeout:
            print "Failed to send Final ACK"
            return -1

        self.isConnected = False
        self.isListening = False
        return

    def closing_handler(self):
        self.sock.settimeout(1)

        # SEND ACK first
        final_ack = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, self.ack_no,
                                            self.window, 0)

        while True:
            try:
                self.sock.sendto(final_ack, self.address)
                break
            except syssock.timeout:
                continue

        # SEND FIN SECOND
        final_fin = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, self.ack_no,
                                            self.window, 0)

        while True:
            try:
                self.sock.sendto(final_fin, self.address)
                break
            except syssock.timeout:
                continue

        # Receive last ACK
        try:
            last_ack, address = self.sock.recvfrom(self.header_len)
        except syssock.timeout:
            print "Connection terminated"
            return -1


        # Convert to ASCII
        last_ack_struct = self.header_struct.unpack(last_ack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK????
        if not last_ack_struct[1] == SOCK352_ACK:
            return -1

        self.isConnected = False
        self.isListening = False

    # function to receive acknowledgments
    # The function receives the buffer and N, as arguments.
    # Return 1 means all acknowledgements received.
    # Return -1 means none received.
    def recvacks(self, buffer, n_packets,):
        # set timeout to recv acks
        print "Receiving Acks"

        self.sock.settimeout(0.2)

        # Ptr to where we are in the
        num_acks = 0

        start_time = time.time()
        while num_acks < n_packets and time.time() - start_time < 0.2:
            try:
                ack_recv = self.sock.recvfrom(self.header_len + 64000)
            except syssock.timeout:
                self.resend = True
                return

            num_acks += 1

        if time.time() - start_time > 0.2:
            self.resend = True

        if num_acks < n_packets:
            self.resend = True

        return 1

    # This function implements go back N.
    # We should use one thread to send the data and one thread to
    # receive the acks.
    # We should also send the length of the file. Return the total number of total
    # bytes. Keep sending data while there are bytes left.
    # We should check if the receiving thread times out. If so,
    # resend the data. While acks are beings sent, we mark for which
    # packets, the acks are received.
    def send(self,buffer):
        print "Sending buffer now"

        self.sock.settimeout(None)

        '''
        ptr = 0

        while ptr < len(buffer):
            if ptr + 64000:
                self.sock.sendto(buffer[ptr:ptr+64000].encode("hex"),self.address)
                ptr += 64000
            else:
                self.sock.sendto(buffer[ptr:len(buffer)].encode("hex"),self.address)
                return
        '''

        # get the length of the buffer and split it according to the
        # the size of the packets (65k bytes + header). The value of N
        # should be the size of the buffer divided by 65 k. Maybe this will change.
        lenbuff = len(buffer)

        print "lenbuff: %d"%lenbuff

        # A "pointer" which holds which part of the buffer
        # we are sending currently.
        ptr = 0

        # Variable to count the number of bytes sent.
        bytessent = 0     # fill in your code here

        N_PACKETS_LIMIT = int(lenbuff/64000) + 1
        sequence_no = random.randint(1,100)
        ack_no = 1
        packets_sent = 0

        while packets_sent < N_PACKETS_LIMIT:
            prev_seq = sequence_no
            prev_ack = ack_no

            recvacks_thread = Thread(target=self.recvacks,args=(self,buffer, N_PACKETS_LIMIT))

            recvacks_thread.start()

            header = self.header_struct.pack(self.version, SOCK352_SYN, self.opt_ptr,
                                             self.protocol, self.header_len,
                                             self.checksum,
                                             self.source_port, self.dest_port,
                                             sequence_no, ack_no,
                                             self.window, self.payload_len)

            # send a 64k bytes payload if we can
            if self.header_len + 64000 < lenbuff:
                print "hi"
                print "eh"
                print "buffer %s"%buffer[ptr:(ptr + 64000)]
                packet = header + binascii.a2b_hex(buffer[ptr:(ptr + 64000)])
                print "Sending packet %d" % sequence_no

                self.sock.sendto(packet, self.address)
            else:
                # otherwise send the remaining
                payload_len = int(lenbuff - ptr)
                print "hi2"
                header = self.header_struct.pack(self.version, SOCK352_SYN, self.opt_ptr,
                                                 self.protocol, self.header_len,self.checksum,
                                                 self.source_port, self.dest_port,
                                                 sequence_no, ack_no,
                                                 self.window, payload_len)
                print "len %s" % len(buffer[ptr:lenbuff])
                packet = header + buffer[ptr:lenbuff].strip().encode("hex")
                print "Sending packet %d" % sequence_no

                self.sock.sendto(packet, self.address)
                print "lotr"
                print "len %s" % len(packet)

            if self.header_len + 64000 < lenbuff:
                bytessent += 64000
            else:
                bytessent += (lenbuff - ptr)

            packets_sent += 1

            if ptr > lenbuff - 64000:
                break
            else:
                ptr += 64000

            sequence_no += bytessent
            print "bytessent%d"%bytessent

            print "receiving acks"
            # when we send we want to get an acknowledgement back for all N packets
            recvacks_thread.join()

            # Otherwise,resend N packets
            # To do this, we just set the ptr to the beginning ptr we had when we started sending N packets
            if self.resend:
                ptr = 0
                packets_sent = 0
                sequence_no = prev_seq
                ack_no = prev_ack
                self.resend = False

        return bytessent

    # For this function, we just receive data and send an acknowledgement.
    # That part should be easy.
    # But, the harder part is to rearrange all of the packets in the order they should
    # be in. A solution I was thinking of is to sort by SYN values.
    def recv(self,nbytes):
        self.sock.settimeout(None)

        # If nbytes is 4 we are receiving the size of the file.
        if nbytes == 4 and not self.didReceiveSizeFile:
            data_recv, address = self.sock.recvfrom(nbytes)

            # Split up packet into header and data
            header = self.header_struct.unpack(data_recv[0:self.header_len - 1])
            data = data_recv[self.header_len:]
            # data = data_recv

            # send acknowledgement, which should be SYN + sizeof(Data) ????
            new_header = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                                 self.protocol, self.header_len, self.checksum, self.source_port,
                                                 self.dest_port, self.sequence_no, 1,
                                                 self.window, 0)

            self.sock.sendto(new_header, self.address)
            self.didReceiveSizeFile = True

            return data

        # Store the bytes into this buffer
        bytesreceived = 0     # fill in your code here

        # This list stores all of the packets received.
        # In the end, we can sort this list and put the packets in order
        packet_list = []

        # Keep obtaining packets until we have recieved n bytes
        while sys.getsizeof(bytesreceived) < nbytes:
            # receive data from the server

            data_recv, address = self.sock.recvfrom(nbytes)

            # Split up packet into header and data
            header = self.header_struct.unpack(data_recv[:self.header_len - 1])
            data = data_recv[self.header_len:]
            packet_list.append((header, data))

            # What to do if we receive a FIN
            if header[1] == SOCK352_FIN:
                return self.closing_handler()

            # iterate the amount of bytes we received
            bytesreceived += sys.getsizeof(data)

            # ack_no should be sequence_no + sizeof(data)
            ack_no = header[8] + sys.getsizeof(data)

            # send acknowledgement, which should be SYN + sizeof(Data) ????
            new_header = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, ack_no,
                                            self.window, 0)


            self.sock.sendto(new_header, self.address)


        packet_list = self.reorder(packet_list)

        # Get the bytes only and make it into a list
        bytes_list = [x[1] for x in packet_list]

        # Join all of the bytes together and return
        bytesreceived = bytes_list.join()
        return bytesreceived

    def reorder(self, packet_list):
        # Sort the list by the sequence_no
        return packet_list.sort(key=lambda x: x[0][8])
