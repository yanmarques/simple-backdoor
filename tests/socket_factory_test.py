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
        socksocket = SocketFactory.server(port=self.get_available_port())
        self.assertIsInstance(socksocket, socket.socket)
        socksocket.close()
        
    def test_client_method(self):
        port = self.get_available_port()
        self.create_server(port)
        socksocket = SocketFactory.client('127.0.0.1', port)
        self.assertEqual(socksocket.recv(len(CONNECTED)), CONNECTED)
        self.assertIsInstance(socksocket, socket.socket)
        socksocket.close()
    
    def create_server(self, port):
        """Create a server on localhost to listen for connections on localhost."""
        def serve(socksocket):
            sock = socksocket.accept()[0]
            sock.send(CONNECTED)
            sock.close()
            socksocket.close()
        threading.Thread(target=serve, args=(SocketFactory.server(port),)).start()

    def get_available_port(self):
        def check_availability(port):
            try:
                subprocess.check_output('netstat -nl | grep :{}'.format(port), shell=True)
                return False
            except subprocess.CalledProcessError as e:
                if e.returncode > 0:
                    return True
                return False
        port = SERVER_PORT
        while not check_availability(port):
            port -= 1
        return port

if __name__ == '__main__':
    unittest.main()
