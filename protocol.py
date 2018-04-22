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

def build_fragments(function):
    """ Append EOF delimiter on result function."""
    def wraper(*args):
        result = Protocol.DELIMITER.join(function(*args))
        if result[-2:] == Protocol.DELIMITER:
            result = result[:-2] + Protocol.EOF
        else:
            result += Protocol.EOF
        return result.encode()
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
    EXIT         = '\x04'
    ACK          = '\x06'
    DOWNLOAD     = '\x05'
    UPLOAD       = '\x03'
    MSG          = '\x07'
    SYN          = '\x16'

    # Response codes.
    SUCCESS_CODE = '2'
    ERROR_CODE   = '4'

    @staticmethod
    @build_fragments
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
            
        # Parse params as HTTP query string.
        params = Protocol.query_parameters(params)

        if content:
            # Encode the request content.
            content = Protocol.encode(content)
        else:
            # Transform content as NULL content.
            content = Protocol.NULL
        
        return (code, content, params)

    @staticmethod
    @build_fragments
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
        
        if content:
            # Encode the response content.
            content = Protocol.encode(content)
        else:
            # Transform content as NULL content.
            content = Protocol.NULL
    
        return (code, content)

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
    def query_parameters(parameters={}):
        """
        Build query parameters to send with request.

        :param parameters: Set with key:value params.
        :return: String representation.
        """
        return '&'.join(['{}={}'.format(key, parameters[key]) for key in parameters])
    
    @staticmethod
    def encode(data, encoding='utf-8'):
        """ 
        Encode the data to string. If data returned starts with base64,
        then this means an error ocurred when trying to encode with default encoding
        and the data was encoded using base64.

        :param data: The data as string.
        :param encoding: The encoding to be used.
        :return: The encoded data.
        """
        try:
            if type(data) is str:
                # Try to encode using default encoding.
                data.encode(encoding=encoding)
            elif type(data) is bytes:
                return data.decode(encoding=encoding)
        except UnicodeDecodeError:
            # Preppend informational data to content and 
            # encode it using base64.  
            return (b'base64:' + b64encode(data)).decode()
        return data

    @staticmethod
    def decode(content):
        """ 
        Decode to string representation. If object starts with base64,
        then this means we will decode it using base64.

        :param data: The data as bytes.
        :return: The decoded data.
        """
        if type(content) is str:
            content = content.encode()

        if content[:7] == b'base64:':
            return b64decode(content[:7])
        return content.decode()