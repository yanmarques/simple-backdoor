#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The packets module.
======================

These modules is intented to complement protocol module. The packets are especial classes
to create protocol packets.

"""

import sys
import protocol
from utils import DataInterface

class Packet(DataInterface):
    def __init__(self, content, params={}, code=None):
        """
        Create the packet object.

        :param content: The packet content.
        :param params: The packet optional parameters.
        :param code: The packet status code.
        :return: The Packet object.
        """
        self._content = content
        self._params = params
        self._code = code if code else protocol.MSG

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
    def __init__(self, file, params={}):
        """
        Create a file packet to send files through socket.
        The default status code is the UPLOAD protocol code.

        :param file: The file path.
        :param params: Params to be sent with request.
        :return: The FileUploadPacket object.
        """
        self.file = file
        Packet.__init__(self, content=self.__get_content(), params=self.__parse_params(params), code=protocol.UPLOAD)

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
    def __init__(self, content, params={}):
        """
        Create a file packet to send files through socket.
        The default status code is the DOWNLOAD protocol code.

        :param content: The file content as bytes.
        :param params: Parameters of the file.
        :return: The FileDownloadPacket object.
        """
        Packet.__init__(self, content=content, params=params, code=protocol.DOWNLOAD)

    def to_file(self, path=None):
        """
        Make file from the packet content.

        :param path: The path to file. Use the default parameter on packet.
        :return: The path of the created file.
        """
        # Get the name of the downloaded file from packet parameters.
        path = path if path else self.params['name']

        if type(self.content) is bytes:
            # Specifies to mode in which the file will be opened.
            # Set to write bytes to file when the content is bytes-like object.
            mode = 'w+b'
        else:
            # Normal write mode.
            mode = 'w'

        with open(path, mode) as handler:
            # Write content to file.
            handler.write(self.content)
        return path
