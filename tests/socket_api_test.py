# -*- coding: UTF -*-

import unittest
import os, sys
import socket
import subprocess
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from simple_backdoor.socket_api import SocketApi
from simple_backdoor.socket_factory import SocketFactory

SERVER_PORT = 9999
MESSAGE = 'connected' # Message sent from server to client when connected.

class SocketApiTest(unittest.TestCase):
    def setUp(self):
        # Set the available server port for each test.
        SERVER_PORT = self.get_available_port()

    def test_send_method(self):
        def serve(server, unittestobj):
            server = SocketApi(server.accept()[0])
            unittestobj.assertEqual(server.recv(), MESSAGE)
            server.close()

        # Create the socket object.
        server = self.create_server(serve, self)

        client = SocketApi(SocketFactory.client('127.0.0.1', SERVER_PORT))
        client.send(MESSAGE)
        client.close()
        server.close()

    def test_recv_method(self):
        def serve(server):
            server = SocketApi(server.accept()[0])
            server.send(MESSAGE)
            server.close()

        # Create the socket object.
        server = self.create_server(serve)

        client = SocketApi(SocketFactory.client('127.0.0.1', SERVER_PORT))
        self.assertEqual(client.recv(), MESSAGE)
        client.close()
        server.close()

    def test_close_method(self):
        # Create the socket object.
        server = self.create_server()

        client = SocketApi(SocketFactory.client('127.0.0.1', SERVER_PORT))
        client.close()
        self.assertFalse(client.is_alive())
        server.close()

    def test_is_alive_method(self):
        # Create the socket object.
        server = self.create_server()

        client = SocketApi(SocketFactory.client('127.0.0.1', SERVER_PORT))
        self.assertTrue(client.is_alive())
        client.close()
        self.assertFalse(client.is_alive())
        server.close()

    def create_server(self, callback = None, args = []):
        # Create the socket object.
        server = SocketFactory.server(SERVER_PORT)

        if not callback:
            def passable(**args): 
                pass
            callback = passable

        # Listen connections on a coroutine.
        threading.Thread(target=callback, args=(server, *args)).start()
        return server

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
