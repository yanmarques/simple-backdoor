# -*- coding: UTF -*-

"""
The socket_factory module.
======================

Socket factories.

:Example:

>> from socket_factory import SocketFactory
>> SocketFactory.build(4444, '192.168.0.105')
<socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('192.168.0.105', 4444)>

This return a new socket instance.

>> from socket_factory import SocketFactory
>> SocketFactory.build(4444, '192.1rr.0.105')
...socket_factory.InvalidIPv4Exception: The IP 0.0.0.0 is not a valid IPv4.

An InvalidIPv4Exception will be raised in case that the 'listen' argument is not a valid IPv4.

"""

import socket

class SocketFactory(object):
    """A socket factory to build sockets."""

    # The default socket buffer size.
    BUFFER_SIZE_SND = 4096
    BUFFER_SIZE_RCV = 4096

    @staticmethod
    def server(port, listen=None, family=None, s_type=None, max_connections=1):
        """
        Build a socket with passed arguments.

        :param port: Port number.
        :param listen: Address to listen connection.
        :param family: Socket family.
        :param s_type: Socket type.
        :param max_connections: Number of maximium of accepted connections.
        :return: The binded socket.
        """
        # Create socket object.
        sock = SocketFactory.__make_socket(family=family, s_type=s_type)

        # Check wheter the listen IP is a valid IPv4
        if listen:
            try:
                socket.inet_aton(listen)
            except OSError:
                raise InvalidIPv4Exception('The IP {} is not a valid IPv4.'.format(listen))

        # Bind socket address.
        sock.bind((listen if listen is not None else '0.0.0.0', int(port)))

        # Determine the max of connections the socket will accept.
        sock.listen(max_connections)
        return sock

    @staticmethod
    def client(host, port, family=None, s_type=None):
        """
        Connects the socket to a host.

        :param host: The host IP.
        :param port: The opened port.
        :param family: Socket family.
        :param s_type: Socket type.
        :return: The socket object.
        """
         # Create socket object.
        sock = SocketFactory.__make_socket(family=family, s_type=s_type)

        # Connects the socket to host:port.
        sock.connect((host, int(port)))

        return sock

    @staticmethod
    def __make_socket(family=None, s_type=None):
        """
        Configurate the socket.

        :param family: Socket family.
        :param s_type: Socket type.
        """
        # Get socket instance with socket family(default=IPv4) and type(default=TCP).
        sock = socket.socket(family=socket.AF_INET if family is None else family,
            type=socket.SOCK_STREAM if s_type is None else s_type)

        # Configurate socket to release address and port on close.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        # Configurate the default buffer size of the socket.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, SocketFactory.BUFFER_SIZE_RCV)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SocketFactory.BUFFER_SIZE_SND)

        return sock

class InvalidIPv4Exception(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return str(self.message)
