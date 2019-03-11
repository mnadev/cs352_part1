For this project, we chose to make the sending and receiving ports global because they were universal to
all of the socket objects we choose to make. We also chose to make the flags a constant and global for the same reason
as well.

Second, we had to create the socket class. For the socket class, we chose to give a socket object attributes
that would be used by all functions in the object. These attributes involved the version number, the opt_ptr,
the protocol, the header data as a string, the header struct, the length of the header (since this is constant),
the ack_no, the sequence_no, the source and destination port, the window, the payload len, the address, booleans
that state if the socket is connected and if it is listening, and finally, and most importantly the socket. A lot
of these attributes are not used for part 1 of the project. But, it was far easier to implement the project
using default values for these attributes rather than leaving them out.

Inside our bind function, all we do is obtain the port number and the destination address. We then have the socket
bind to the port using bind.

For connect, what we did was implement the 3 way handshake. First, the client sends a SYN
as a flag. Then, we recieve an ACK from the server. Then, we send a SYN again.

For accept, we connect from the perspective of the client. We wait for the SYN packet from the client.
Then, we send an ACK. Then, we wait for a SYN packet from the client again.

For listen, we do not do much but set isListening to True.

For close, we implemented the four way termination handshake between the client and server. In recv(), for each packet
we receive, we check if the flag is equal to FIN. If so, there is a function called closing handler that is called
which sends a FIN and an ACk and waits for the FINAL FIN.

For send, we used a dynamic window with an upper limit of 20. We keep sending packets until we hit the window.
Then, we wait for all the acks. We created a seperate function to receive the acknowledgements. It used
to be an inner function inside send but we found that it was better not to make it an inner function because of
multithreading. Rather, it was easier to have a boolean that stated whether packets had to be resent. There was
no benefit from keeping it an inner function. For recvacks(), we have a timeout of 0.2 seconds. If we do not receive a
packet in 0.2 seconds or we do not receive all N packets, then we resend the packets by changing the boolean.

For recv(), we just keep receiving packets until we have received nbytes. The timeout for this function is set to
None. For each packet, we send an acknowledgement packet back. Then, we sort the packets by sequence number, obtain
the bytes and concatenate them together. We return this in the end.

We chose to make our program multithreaded because we felt that it prevented us from losing any acknowledgements received.
If we were sending data, it is possible we could receive acknowledgements before we send all the packets in our window
we wanted to send.
