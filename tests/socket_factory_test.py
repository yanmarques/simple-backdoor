# -*- coding: UTF -*-

import unittest
import os, sys
import socket
import threading
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from simple_backdoor.socket_factory import SocketFactory

SERVER_PORT = 9999
CONNECTED = b'connected'

class SocketFactoryTest(unittest.TestCase):
    def test_server_method(self):
        socksocket = SocketFactory.server(port=SERVER_PORT)
        self.assertIsInstance(socksocket, socket.socket)
        socksocket.close()
        
    def test_client_method(self):
        self.create_server(self.get_available_port())
        socksocket = SocketFactory.client('127.0.0.1', SERVER_PORT)
        self.assertEqual(socksocket.recv(len(CONNECTED)), CONNECTED)
        self.assertIsInstance(socksocket, socket.socket)
        socksocket.close()
    
    def create_server(self, port):
        """Create a server on localhost to listen for connections on localhost."""
        def serve(port):
            socksocket = SocketFactory.server(port)
            sock = socksocket.accept()[0]
            sock.send(CONNECTED)
            sock.close()
            socksocket.close()
        threading.Thread(target=serve, args=(port)).start()

    def get_available_port(self):
        def check_availability(port):
            return subprocess.check_output('netstat -nl | grep :{}'.format(port), shell=True) == ''
        port = SERVER_PORT
        while not check_availability(port):
            port -= 1
        return port

if __name__ == '__main__':
    unittest.main()
