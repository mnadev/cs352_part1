
import binascii
import socket as syssock
import struct
import sys
from threading import Thread
import time

# Acknowledgement number
ACK_NO = 1

# Synchronization number
SYN = 1

# Defining N for Go Back N, randomly assigned right now
N_PACKETS_LIMIT = 5


# creating the port variables for receiving and sending processes
global UDPportTx
global UDPportRx

UDPportRx_global = 80
UDPportTx_global = 80

# these functions are global to the class and
# define the UDP ports all messages are sent
# and received from

# basically only set the port numbers
def init(UDPportTx,UDPportRx):   # initialize your UDP socket here
    global UDPportTx_global
    global UDPportRx_global

    UDPportRx_global = UDPportRx
    UDPportTx_global = UDPportTx

    
class socket:
    # should use the struct to initialize an object
    def __init__(self):  # fill in your code here
        self.sockets = []
        return

    # Bind to a port
    # Which probably means to set the variables equal tp
    # the port and the address to the address give.
    def bind(self,address):
        try:
            self.sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
        except syssock.error:
            print "Error with creating socket."
            return
        return 

    # This function is to create a connection from client perspective
    # For the server, we will bind in this function.
    def connect(self,address):  # fill in your code here
        (self.address, self.port) = address
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        return

    # This function is to create a connection from the server perspective.
    def accept(self):
        try:
            sock = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)
            return (sock, address)
        except syssock.error:
            print "Error with creating socket."
            return (None, None)
        (clientsocket, address) = (1,1)  # change this to your code 
        return (sock,address)

    # Close connection if last packet received
    # Otherwise, set close variable
    def close(self):   # fill in your code here
        # To close we need to first send a FIN
        # then we should recieve a FIN and an ACK
        # finally we should send an ACK
        return 

    # This function implements go back N.
    # We should use one thread to send the data and one thread to
    # receive the acks.
    # We should also send the length of the file. Return the total number of total
    # bytes. Keep sending data while there are bytes left.
    # We should check if the receiving thread times out. If so,
    # resend the data. While acks are beings sent, we mark for which
    # packets, the acks are received.
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
            packet = struct.pack(fmt='i',str=self.header)
            if packet + 65000 < lenbuff:
                packet += "\n" + buffer[ptr:(ptr+65000)]
            else:
                packet += "\n" + buffer[ptr:lenbuff-1]

            thread_send = Thread(target=self.sock.send, args=(buffer))
            thread_send.start()

            ack_no = thread_recv.join(timeout=100)
            if ptr > lenbuff - 65000:
                pass
            else:
                ptr += 65000

        thread_recv = Thread(target=recvacks, args=(buffer, N_PACKETS_LIMIT))
        thread_recv.start()
            # when we send we want to get an acknowledgement back
        return bytessent

    # For this function, we just receive data and send an acknowledgement.
    # That part should be easy.
    # But, the harder part is to rearrange all of the packets in the order they should
    # be in. A solution I was thinking of is to sort by SYN values.
    def recv(self,nbytes):
        bytesreceived = ""     # fill in your code here
        packet_list = []
        while not bytesreceived == nbytes:
            thread_recv = Thread(target=self.sock.recv, args=(nbytes))
            #recv
            thread_recv.start()
            data_recv = thread_recv.join(timeout=0.1)
            bytesreceived += + sys.getsizeof(data_recv)
            packet_list.append(data_recv)

            # send acknowledgement
            self.sock.send(ACK_NO)

        return self.reorder()
        # return bytesreceived

    def reorder(self, packet_list):
        packet_list.sort()
    


