# -*- coding: UTF -*-

"""

>>from socket_factory import SocketFactory
>>SocketFactory.build(4444, '192.168.0.105')

This return a new socket instance. An InvalidIPv4Exception will be
raised in case that the 'listen' argument is not a valid IPv4.

"""

import socket

class SocketFactory(object):
    """A socket factory to build sockets."""
    
    @staticmethod
    def build(port, listen=None, family=None, s_type=None, max_connections=1):
        """
        Build a socket with passed arguments.
        
        :param port: Port number.
        :param listen: Address to listen connection.
        :param family: Socket family. 
        :param s_type: Socket type.
        :param max_connections: Number of maximium of accepted connections.
        """

        # Get socket instance with socket family(default=IPv4) and type(default=TCP).
        sock = socket.socket(family=socket.AF_INET if family is None else family, 
            type=socket.SOCK_STREAM if s_type is None else s_type)

        # Configurate socket to release address and port on close.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

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
        
class InvalidIPv4Exception(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return str(self.message)