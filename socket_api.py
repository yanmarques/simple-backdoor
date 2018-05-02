# -*- coding: utf-8 -*-

"""
The socket api module.
======================

The module has the SocketApi class, that is a underlying class for socket.socket object.

"""

import socket
import struct
import protocol

class SocketApi(object):
    """
    The api to handle socket operations, as:
        * properly sending/receiving data.
        * properly close the connection.
        * verify if connection is alive.
        * receive data with timeout.
    """

    def __init__(self, sock):
        """
        Instantiate the api.

        :param sock: The socket underlay.
        """
        if type(sock) is not type(socket.socket()):
            raise TypeError('Argument socket must be a socket, not {}'.format(sock.__class__.__name__))
        self.__socket = sock

    def send(self, data):
        """
        Send data through socket.

        :param data: The data content as bytes-like object.
        """
        # Get the total length in bytes of the request.
        lenght = struct.pack('>Q', len(data))

        # Send the length of the request.
        self.__socket.sendall(lenght)

        # Actually send the request.
        self.__socket.send(data)

        # Receive socket ACk.
        self.__recv_ack()

    def recv(self, timeout=None):
        """
        Receive response from socket.

        :param timeout: The max time in seconds the socket will listen.
        :return: The response class.
        """
        def reader():
            """
            Read data from socket and return the result.

            :return: The content in bytes.
            """
            is_syn_request = True

            while is_syn_request:

                # Read the lenght in bytes of the response.
                (lenght,) = struct.unpack('>Q', self.__socket.recv(8))

                # The amount of data in bytes.
                data = b''

                while lenght > len(data):
                    # Bytes left.
                    to_read = lenght - len(data)

                    # Append data to socket. The buffer size of the data received depends on how
                    # much data we have to receive. Once the data to receive is lower than the
                    # default buffer size, we will only receive the remaining data.
                    data += self.__socket.recv(to_read if to_read < self.getsocket_bufer()[1] else None)

                if data.decode() != protocol.SYN:
                    # The request is not SYN.
                    is_syn_request = False

                # Send ACk to socket.
                self.__socket.sendall(struct.pack('>Q', protocol.ACK))

            return data

        if timeout:

            # Attempt to read content from socket with a timeout set.
            content = self._wrap_timeout(reader, timeout)

            # Socket has timedout.
            if not content:
                return False
        else:
            # Read the content.
            content = reader()
        
        return content

    def getsocket_bufer(self):
        """
        Return the lenght of the buffer.

        :return: A tuple with the send and receive buffer size.
        """
        return (self.__socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF),
            self.__socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))

    def close(self):
        """Close the socket connection."""
        self.__socket.close()

    def is_alive(self):
        """
        Determine whether the socket connetion is alive.

        :return: A boolean value.
        """
        def checker():
            """
            Verify whether the socket connection is good.
            """
            # SYN request.
            syn = Protocol.SYN.encode()

            # Get the total lenght of NULL request
            lenght = struct.pack('>Q', len(syn))

            try:
                # Send the lenght of the request.
                self.__socket.sendall(lenght)

                # Actually send the request content.
                self.__socket.send(syn)

                # Receive acknoledge.
                self.__recv_ack()
            except (BrokenPipeError, ConnectionError, AcknoledgeNotReceivedExecption):
                return False
            return True

        return self._wrap_timeout(checker, 5)

    def _wrap_timeout(self, function, timeout):
        """
        Execute a socket operation with timeout.

        :param function: The function to call.
        :param timeout: The socket timeout in seconds.
        :return: The content of operation. Returns false if socket timed out.
        """
        self.__socket.settimeout(timeout)
        try:
            content = function()
        except (socket.timeout, struct.error):
            # Socket has timed out.
            content = False

        # Adjust socket to no timeout.
        self.__socket.settimeout(None)

        return content

    def __recv_ack(self):
        """Receive acknoledge from socket."""
        # Receive socket acknoledge.
        (ack,) = struct.unpack('>Q', self.__socket.recv(8))

        if ack is not protocol.ACK:
            raise AcknoledgeNotReceivedExecption('Socket returned invalid ACK.')

class AcknoledgeNotReceivedExecption(socket.error):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return str(self.message)
