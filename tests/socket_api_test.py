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
ON_CONNECTED = 'connected' # Message sent from server to client when connected.
ON_CLIENT_CLOSE = 'finish' # Message sent client to server.

class SocketApiTest(unittest.TestCase):
    def setUp(self):
        SERVER_PORT = self.get_available_port()

    def test_send_method(self):
        def serve(unittestobj, server):
            server = SocketApi(server.accept()[0])
            unittestobj.assertEqual(server.recv(), ON_CONNECTED)
            server.close()

        # Create the socket object.
        server = SocketFactory.server(SERVER_PORT)

        # Listen connections on a coroutine.
        threading.Thread(target=serve, args=(self, server,)).start()

        client = SocketApi(SocketFactory.client('127.0.0.1', SERVER_PORT))
        client.send(ON_CONNECTED)
        client.close()
        server.close()

    # def test_recv_method(self):

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
