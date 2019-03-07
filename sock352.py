
import binascii
import socket as syssock
import struct
import sys
from threading import Thread

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
    def bind(self,address):
        return 

    # This function is to create a connection from client perspective
    # For the server, we will bind in this function.
    def connect(self,address):  # fill in your code here 
        return 

    # ignore this function
    # or use is to create a list of sockets.
    def listen(self,backlog):
        return

    # This function is to create a connection from the server perspective.
    def accept(self):
        # clientsocket = self.socket[0]
        (clientsocket, address) = (1,1)  # change this to your code 
        return (clientsocket,address)

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

        # function to receive acknowledgments
        def recvacks(self, buffer):
            self.sock.recv()
            return

        bytessent = 0     # fill in your code here

        sizeofBuffer = sys.getsizeof(buffer)

        while not bytessent == sizeofBuffer:
            thread_send = Thread(target=self.sock.send, args=(buffer))
            thread_send.start()


            thread_recv = Thread(target=syssock._realsocket.recv, )
            thread_recv.start()
            ack_no = thread_recv.join(timeout=100)
            # when we send we want to get an acknowledgement back
        return bytessent

    # For this function, we just receive data and send an acknowledgement.
    # That part should be easy.
    # But, the harder part is to rearrange all of the packets in the order they should
    # be in. A solution I was thinking of is to sort by SYN values.
    def recv(self,nbytes):
        bytesreceived = 0     # fill in your code here
        while not bytesreceived == nbytes:
            thread_recv = Thread(target=self.sock.recv, args=(nbytes))
            #recv
            thread_recv.start()
            data_recv = thread_recv.join(timeout=0.1)
            bytesreceived += sys.getsizeof(data_recv)

            # send acknowledgement
            thread_send = Thread(target=self.sock.send,args=(ACK_NO))
            thread_send.start()
            thread_send.join(timeout=0.1)
        return bytesreceived


    


