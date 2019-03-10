import binascii
import socket as syssock
import struct
import sys
import time

# TODO: implement 0.2 second timeouts for all socket operations

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
        self.version = 1

        # Ignore these two for now. just setting them to zero
        self.opt_ptr = 0
        self.protocol = 0

        # The length of the header in bytes
        self.sock352PktHdrData = '!BBBBHHLLQQLL'

        self.header_struct = struct.Struct(self.sock352PktHdrData)

        # Calculating the header size
        self.header_len = struct.calcsize(self.sock352PktHdrData)

        # Set checksum to 0 for now.
        self.checksum = 0

        # Set ports which are unused for this part
        # so they'll be set to random value
        self.source_port = 0
        self.dest_port = 0

        # Set sequence number to a random number
        self.sequence_no = 0

        # Set ack_num to 1 for now
        self.ack_no = (0)

        # Ignore window for now
        self.window = (0)

        # Each payload will be 64k bytes maximum
        # 64k in bytes is what is listed below
        # It could be less and we should account for that
        self.payload_len = 64000

        # Store address to send to
        # should be tuple of (ip_addr, port)
        self.address = (None, tx_port)

        # Booleans to state whether we are connected and listening
        self.isConnected = False
        self.isListening = False

        # Create a socket using UDP and using IP
        self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        return

    # Bind to a port (from server perspective)
    # Which probably means to set the variable equal to
    # the port.
    def bind(self,address):
        (null_val, self.unusedport) = address

        # Bind to the port
        self.sock.bind(('', rx_port))
        return

    # This function is to create a connection from client perspective
    def connect(self,address):  # fill in your code here
        (self.dest_address, self.unusedport) = address

        self.sock.bind(('', int(rx_port)))

        # 3-way handshake from perspective of client
        payload = (0)

        # Send SYN first
        first_syn_conn = self.header_struct.pack(self.version,SOCK352_SYN,self.opt_ptr,
                                      self.protocol,self.header_len,self.checksum,
                                      self.source_port,12,
                                      12,12,12,12)

        self.sock.sendto(first_syn_conn,(self.dest_address, tx_port))

        # Receive ACK which should be (SYN | ACK) & ACK
        # Also receive SEQ
        # Convert the obtained bytes to ascii
        result_bin, self.dest_address = self.sock.recvfrom(self.header_len)

        # Convert the bytes to struct
        result_struct = self.header_struct.unpack(result_bin)

        # If we get the wrong flag, we do ??????
        # possibly just return -1
        if not result_struct[1] == SOCK352_ACK:
            print "Unable to connect"
            return -1

        # Send SYN again
        second_syn_conn = self.header_struct.pack(self.version, SOCK352_SYN, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port, self.dest_port,self.sequence_no,
                                      self.ack_no,self.window,int(payload))

        self.sock.sendto(second_syn_conn, (self.dest_address, tx_port))


        self.isConnected = True
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        self.isListening = True
        return

    # This function is to create a connection from the server perspective.
    # Here we must implement a 3 way handshake.
    def accept(self):
        # first wait for an incoming input from client
        # which sends the SYN number.
        first_pack, self.dest_address = self.sock.recvfrom(self.header_len)

        # Convert to ASCII
        first_pack_struct = self.header_struct.unpack(first_pack)

        if not first_pack_struct[1] == SOCK352_SYN:
            print "Failed to connect"
            return -1

        # The returned buffer have flag equal to ACK to acknowledge
        first_ack = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port, self.dest_port,self.sequence_no,
                                      self.ack_no,self.window)

        self.sock.sendto(first_ack, (self.dest_address, tx_port))

        # Receive the last acknowledgement
        # Convert to ascii
        last_ack_bin = self.sock.recv(self.header_len)

        # Convert the bytes to struct
        result_struct = self.header_struct.unpack(last_ack_bin)

        # If we don't receive acknowledgement, return with failure
        if not result_struct[1] == SOCK352_ACK:
            print "Failed to connect"
            return -1

        # Have no idea what to return
        (clientsocket, address) = (self.sock, (self.dest_address,tx_port))  # change this to your code
        self.isConnected = True

        return (clientsocket, address)

    # Close connection if last packet received
    # Otherwise, set close variable
    def close(self):   # fill in your code here
        # To close we need to first send a FIN
        # then we should receive an ACK
        # Then, we should receive a FIN a
        # and we should send an ACK

        # Send FIN.
        first_fin = self.header_struct.pack(self.version, SOCK352_FIN, self.opt_ptr,
                                      self.protocol, self.header_len,self.checksum,
                                      self.source_port,self.dest_port,self.sequence_no,
                                      self.ack_no,self.window,0)

        self.sock.sendto(first_fin, (self.dest_address,tx_port))

        # Receive ACK and FIN.
        # first wait for an incoming input from client
        # which sends the ACK or FIN number.
        first_pack, address = self.sock.recvfrom(self.header_len)

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

        second_pack, address = self.sock.recvfrom(self.header_len)

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

        self.sock.sendto(final_ack, (self.dest_address, self.dest_port))

        self.isConnected = False
        self.isListening = False
        return 

    # This function implements go back N.
    # We should use one thread to send the data and one thread to
    # receive the acks.
    # We should also send the length of the file. Return the total number of total
    # bytes. Keep sending data while there are bytes left.
    # We should check if the receiving thread times out. If so,
    # resend the data. While acks are beings sent, we mark for which
    # packets, the acks are received.
    # TODO: Synchronize the SEQ, SYN and ACK values
    def send(self,buffer):

        # function to receive acknowledgments
        # The function receives the buffer and N, as arguments.
        # Return 1 means all acknowledgements received.
        # Return -1 means none received.
        # TODO: Verify that the acks are actually unique and what we should obtain rather then counting the number of received messages as acks
        def recvacks(buffer, n_packets, starting_byte_pos, ending_byte_pos):
            ack_list = []
            num_bytes = ending_byte_pos - starting_byte_pos
            counter = starting_byte_pos
            num_acks = 0
            while num_acks < n_packets and counter < ending_byte_pos:
                if counter + 64000 < ending_byte_pos:
                    ack_recv = self.sock.recv(self.header_len + 64000)
                    ack_pack = self.header_struct.unpack(ack_recv)
                    ack_list.append(ack_pack[9])
                    num_acks += 1
                else:
                    ack_recv = self.sock.recv(self.header_len + (ending_byte_pos-counter))
                    ack_pack = self.header_struct.unpack(ack_recv)
                    ack_list.append(ack_pack[9])
                    num_acks += 1

            if num_acks < n_packets:
                return -1

            ack_list.sort()
            ack_list = [(x-starting_byte_pos) for x in ack_list]
            if not ack_list[ack_list.__len__() - 1] == num_bytes:
                return -1

            return 1

        # get the length of the buffer and split it according to the
        # the size of the packets (65k bytes + header). The value of N
        # should be the size of the buffer divided by 65 k. Maybe this will change.
        lenbuff = len(buffer)

        # A "pointer" which holds which part of the buffer
        # we are sending currently.
        ptr = 0

        # Variable to count the number of bytes sent.
        bytessent = 0     # fill in your code here
        sequence_no = 0
        ack_no = 1

        while not bytessent == lenbuff:
            packets_sent = 0

            # A pointer that will be useful if we have to resend the N packets.
            ptr_go_back = ptr

            while not packets_sent == N_PACKETS_LIMIT:

                header = self.header_struct.pack(self.version, SOCK352_SYN, self.opt_ptr,
                                          self.protocol,self.header_len,
                                          self.checksum,
                                          self.source_port,self.dest_port,
                                          sequence_no,ack_no,
                                          self.window,self.payload_len)

                # send a 64k bytes payload if we can
                if self.header_len + 64000 < lenbuff:
                    packet = header + binascii.a2b_hex(buffer[ptr:(ptr + 64000)])
                    bytessent += 64000
                else:
                    # otherwise send the remaining
                    payload_len = int(lenbuff - ptr - 1)
                    header = self.header_struct.pack(self.version, SOCK352_SYN, self.opt_ptr,
                                                     self.protocol, self.header_len,self.checksum,
                                                     self.source_port, self.dest_port,
                                                     sequence_no, ack_no,
                                                     self.window, payload_len)
                    packet = header + buffer[ptr:lenbuff-1]
                    bytessent += (lenbuff - ptr - 1)

                self.sock.sendto(packet, address=(self.dest_address, self.dest_port))
                packets_sent += 1

                if ptr > lenbuff - 64000:
                    break
                else:
                    ptr += 64000

                sequence_no += bytessent


            # when we send we want to get an acknowledgement back for all N packets
            did_recv_all = recvacks(buffer, N_PACKETS_LIMIT, ptr_go_back, bytessent)

            # Otherwise,resend N packets
            # To do this, we just set the ptr to the beginning ptr we had when we started sending N packets
            if did_recv_all == -1:
                ptr = ptr_go_back
                packets_sent -= N_PACKETS_LIMIT

        return bytessent

    def closing_handler(self):
        # SEND ACK first
        final_ack = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, self.ack_no,
                                            self.window, 0)

        self.sock.sendto(final_ack, (self.dest_address, self.dest_port))

        # SEND FIN SECOND
        final_fin = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, self.ack_no,
                                            self.window, 0)

        self.sock.sendto(final_fin, (self.dest_address, self.dest_port))

        # Receive last ACK
        last_ack, address = self.sock.recvfrom(self.header_len_int)

        # Convert to ASCII
        last_ack_struct = self.header_struct.unpack(last_ack)

        # WHAT DO WE DO WHEN DON'T RECEIVE ACK????
        if not last_ack_struct[1] == SOCK352_ACK:
            return -1

        self.isConnected = False
        self.isListening = False

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
            header = self.header_struct.unpack(data_recv[:self.header_len])
            data = data_recv[self.header_len:]
            packet_list.append((header, data))

            # iterate the amount of bytes we received
            bytesreceived += sys.getsizeof(data)

            # ack_no should be sequence_no + sizeof(data)
            ack_no = header[8] + sys.getsizeof(data)

            # send acknowledgement, which should be SYN + sizeof(Data) ????
            new_header = self.header_struct.pack(self.version, SOCK352_ACK, self.opt_ptr,
                                            self.protocol, self.header_len, self.checksum, self.source_port,
                                            self.dest_port, self.sequence_no, ack_no,
                                            self.window, 0)

            self.sock.sendto(new_header,(self.dest_address,tx_port))

        packet_list = self.reorder(packet_list)

        # Get the bytes only and make it into a list
        bytes_list = [x[1] for x in packet_list]

        # Join all of the bytes together and return
        bytesreceived = bytes_list.join()
        return bytesreceived

    def reorder(self, packet_list):
        # Sort the list by the sequence_no
        return packet_list.sort(key=lambda x: x[0][8])
