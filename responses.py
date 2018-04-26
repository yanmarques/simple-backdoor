#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The socket responses module.
======================

The constructed responses will be handled by client. The client socket will act like a server,
receiving requests and properly sending responses. The protocol code responses will be followed
by protocol module response codes.
The normal response codes will be of sucess and error. Althought the socket is able to send FileResponse,
that will be handled with a diferent response code, as it must be stored on file system or in memory for
short use case.

The responses uses BaseResponse as base class. The BaseResponse helps you to create responses and is
used to instruct socket to handle response/requests.

"""

from protocol import Protocol

class BaseResponse(abstract):
    """BaseResponse class."""

    def __init__(self, content, code):
        """
        Create response object with content and response code. No parameters allowed so far.

        :param content: The response content.
        :param code: The significant response code.
        :return: The BaseResponse object.
        """
        self.__content = content
        self.__code = code

    @property
    def content(self):
        """Get response content as bytes."""
        return self.__content

    def get_raw(self):
        """Get raw content to be sent over socket."""
        return Protocol.to_response(self.__code, self.__content)

class Response(BaseResponse):
    """The normal response with the content."""
    def __init__(self, content, code=None):
        """
        Create a content response.

        :param content: The response content.
        :param code: The significant response code.
        :return: Class object.
        """
        BaseResponse.__init__(content, code if code else Protocol.SUCCESS_CODE)
