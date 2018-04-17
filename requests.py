# -*- coding: UTF -*-

"""
The request classes module.
======================

Request classes to handle messages using Protocol on protocol module.

:Example:

>>> from requests import Request
>>> Request('Hello world', params={'foo': 'bar'}).get_raw()
b'\x07\r\nHello world\r\nfoo=bar\r\n\r\n'

Create request message with content and parameters.

>>> from requests import Request
>>> FileRequest('test.txt').get_raw()
b'\x06\r\nHello world\r\nname=test.txt\r\n\r\n'

Create request from file.
"""

import sys
import abc
from protocol import Protocol

# Abstract class.
abstract = abc.ABCMeta if sys.version_info[0] < 3 else abc.ABC

class BaseRequest(abstract):
    """ BaseRequest class."""

    def __init__(self, *args):
        """Instantiate request with data and parameters."""
        raise Exception('ABC class can not be instantiated.')

    @abc.abstractproperty
    def content(self):
        """Get request content as bytes."""
        pass

    @abc.abstractproperty
    def params(self):
        """Get the request parameters."""
        pass

    @abc.abstractmethod
    def get_raw(self):
        """Get raw content to be sent over socket."""
        pass

class Request(BaseRequest):
    def __init__(self, content, params={}, code=None):
        self.__content = content
        self.__params = params 
        self.__code = code if code else Protocol.MSG

    @property
    def content(self):
        """Get request content as bytes."""
        return self.__content

    @property
    def params(self):
        """Get the request parameters."""
        return self.__params

    def get_raw(self):
        """Get raw content to be sent over socket."""
        return Protocol.to_request(self.__code, self.__content, self.__params)

class FileRequest(BaseRequest):
    def __init__(self, file, params={}):
        """
         Instantiate request with data and parameters.

        :param file: The file path.
        :param params: Params to be sent with request.
        :return: The request class.
        """
        self.__file = file
        self.__content = self.__get_content()
        self.__params = self.__parse_params(params) 

    @property
    def content(self):
        """Get request content as bytes."""
        return self.__content   

    @property
    def params(self):
        """Get the request parameters."""
        self.__params['name'] = self.__file.split('\\' if sys.platform.startswith('win32') else '/').pop()
        return self.__params

    def get_raw(self):
        """Get raw content to be sent over socket."""
        return Protocol.to_request(Protocol.UPLOAD, self.__content, self.__params)

    def __get_content(self):
        """
        Get content as bytes of a given file.

        :param file: Path to file.
        :return: The file content.
        """
        with open(self.__file, 'rb') as handler:
            return handler.read()

    def __parse_params(self, params={}):
        """
        Parse parameters of request.

        :param params: Set of key:value params.
        :return: The new parameters.
        """
        if 'name' not in params:
            params['name'] = self.__file
        return params

print(Request('Hello world', params={'foo': 'bar'}).get_raw())