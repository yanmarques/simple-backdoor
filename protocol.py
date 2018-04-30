# -*- coding: UTF -*-

"""
The protocol module.
======================

The module to create protocol messages. A message is basically composed
of a code, the message content and aditional parameters.

:Example:

>> import protocol
>> packet = protocol.build_packet(MSG, 'Hello World', {'python': True})
b'\x07\r\nHello World\r\npython=True\r\n\r\n'

Create a raw message with aditional parameters.

>> protocol.from_packet(packet)
('\x07', 'Hello World', {'python': ['True']})

Parse the packet content and return the values of the request.

"""

from base64 import b64decode, b64encode
import urllib.parse

# Content separator.
DELIMITER    = '\r\n'

# End of file.
EOF          = '\r\n\r\n'

# None value.
NULL         = '\x00'

# Request codes.
GET_INFO     = '\x01'
PWD          = '\x03'
DOWNLOAD     = '\x05'
UPLOAD       = '\x06'
MSG          = '\x07'

# Response codes.
SUCCESS_CODE = '\x02'
ERROR_CODE   = '\x04'

# Reserved communication codes.
ACK          = 0x006
SYN          = 0x026
EXIT         = 0x004

def encode(data, encoding='utf-8'):
    """
    Encode the data to bytes. If data returned starts with base64, then this means an error ocurred when trying to encode
    with default encoding and the data was encoded using base64.

    :param data: Data to be encoded.
    :param encoding: The encoding to be used.
    :return: The bytes-like object.
    """
    try:
        if type(data) is bytes:
            data.decode(encoding=encoding)
        else:
            # Try to encode using default encoding.
            data = data.encode(encoding=encoding)
    except UnicodeDecodeError:
        # Preppend informational data to content and encode it using base64.
        return b'base64:' + b64encode(data if type(data) is bytes else data.encode())
    return data

def decode(content):
    """
    Decode to bytes-like object representation. If object starts with base64,
    then this means we will decode it using base64.

    :param content: The content as bytes.
    :return: The decoded content.
    :rtype: bytes or str.
    """
    if content[:7] == b'base64:':
        return b64decode(content[7:])
    return content.decode()

def build_fragments(function):
    """ Append EOF delimiter on result function."""
    def wraper(*args, **kwargs):
        result = DELIMITER.join(function(*args, **kwargs))
        if result[-2:] == DELIMITER:
            result += NULL + EOF
        else:
            result += EOF
        return encode(result)
    return wraper

@build_fragments
def build_packet(code, content=None, params={}):
    """
    Create a packet message to sent over socket. The packet is built from a code,
    the content of the request and the parameters.

    :param code: The name code of request.
    :param content: The content of request.
    :param params: A list with key-value parameter
    :return: The data encoded.
    """
    if not __is_code_valid(code):
        raise TypeError('Invalid code for packet.')

    # Parse params as HTTP query string.
    params = urllib.parse.urlencode(params)

    if type(content) is bytes:
        # Encode the data content
        content = encode(content).decode()

    if not content:
        # Transform content as NULL content.
        content = NULL

    return (code, content, params)

def from_packet(content):
    """
    Parse the content from a packet request, returning the code, content and request parameters.

    :param content: The raw request content.
    :return: Code, content and parameters.
    """
    if not content.endswith(EOF.encode()):
        # Invalid end of file on request.
        raise MalformedPacketException('The packet is malformed. No EOF found on packet content.')

    # Split request by delimiter removing the end of file flag from end of request content.
    code, data, params = content[:-len(EOF)].split(DELIMITER.encode())

    # Decode the data if base64 encoded.
    data = decode(data)

    if data is NULL:
        # Null content.
        data = None

    if params is NULL:
        # Null parameters
        params = {}

    return (code.decode(), data, urllib.parse.parse_qs(params.decode()))

def __is_code_valid(code):
    """
    Determine wheter a code is valid for packet.

    :param code: The code.
    :return: A boolean indicating validation.
    """
    return code in [GET_INFO, PWD, DOWNLOAD, UPLOAD, MSG, SUCCESS_CODE, ERROR_CODE]

class MalformedPacketException(Exception):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return str(self.message)
