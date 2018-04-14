# -*- coding: UTF -*-

"""
The protocol module.
======================

Create messages with specific content using procotol.

:Example:

>> from protocol import Protocol
>> Protocol.to_request(Protocol.ACK, 'Acknolodge received')
'\x04\r\nAcknolodge received\r\n\r\n\r\n'

Create a acknolodge request to be sent over socekt.

>> Protocol.to_response(Protocol.SUCCESS_CODE)
'2\r\n\x00\r\n\r\n'

Create a success response.

"""

from base64 import b64decode, b64encode

def append_eof(function):
    """ Append EOF delimiter on result function."""
    def wraper(*args, **kwargs):
        return function(*args) + Protocol.EOF
    return wraper

class Protocol(object):
    """
    The class to create protocol messages. A message is basically composed
    of a code, the message content and aditional parameters.
    """

    # Content separator.
    DELIMITER    = '\r\n'

    # End of file.
    EOF          = '\r\n\r\n'

    # None value.
    NULL         = '\x00'

    # Request codes.
    GET_INFO     = '\x01'
    PWD          = '\x02'
    EXIT         = '\x03'
    ACK          = '\x04'
    DOWNLOAD     = '\x05'
    UPLOAD       = '\x06'
    MSG          = '\x07'

    # Response codes.
    SUCCESS_CODE = '2'
    ERROR_CODE   = '4'

    @staticmethod
    @append_eof
    def to_request(code, content='', params={}):
        """
        Create a message for request operation with the given
        arguments to be decoded on client.

        :param code: The name code of request.
        :param content: The content of request.
        :param params: A list with key-value parameter
        :return: The data encoded.
        """
        if not Protocol.__is_code_for_request(code):
            raise TypeError('Invalid code for request.')
        
        if type(content) is bytes:

            # Encode the request content.
            content = Protocol.__encode(content)
            
        # Parse params as HTTP query string.
        params = '&'.join(['{}={}'.format(key, params[key]) for key in params])

        if not content:

            # Transform content as NULL content.
            content = Protocol.NULL
    
        return Protocol.DELIMITER.join([code, content, params])

    @staticmethod
    @append_eof
    def to_response(code, content=''):
        """
        Create a message for response operation with the given
        arguments to be decoded on server.

        :param code: The name code of response.
        :param content: The content of response.
        :return: The data decoded.
        """
        if not Protocol.__is_code_for_response(code):
            raise TypeError('Invalid code for request.')
        
        if type(content) is bytes:

            # Encode the response content.
            content = Protocol.__encode(content)

        if not content:

            # Transform content as NULL content.
            content = Protocol.NULL
    
        return Protocol.DELIMITER.join([code, content])

    @staticmethod
    def __is_code_for_request(code):
        """
        Determine wheter a code is valid for request.
        
        :param code: The response code.
        :return: A boolean indicating validation.
        """
        return code in [
            Protocol.GET_INFO, Protocol.PWD, Protocol.EXIT, 
            Protocol.ACK, Protocol.DOWNLOAD, Protocol.UPLOAD,
            Protocol.MSG
        ]

    @staticmethod
    def __is_code_for_response(code):
        """
        Determine wheter a code is valid for response.
        
        :param code: The response code.
        :return: A boolean indicating validation.
        """
        return code in [
            Protocol.SUCCESS_CODE, Protocol.ERROR_CODE
        ]

    @staticmethod
    def __encode(data, encoding='utf-8'):
        """ 
        Encode the bytes of data to str. If data returned starts with base64,
        then this means an error ocurred when trying to encode with default encoding
        and the data was encoded using base64.

        :param data: The data as bytes.
        :param encoding: The encoding to be used.
        :return: The encoded data.
        """
        try:

            # Try to encode using default encoding.
            return data.encode(encoding=encoding)
        except UnicodeDecodeError:

            # Preppend informational data to content and 
            # encode it using base64.  
            return 'base64:{}'.format(b64encode(data))