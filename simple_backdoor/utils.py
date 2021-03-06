# -*- coding: utf-8 -*-

"""
The utils module.
======================

Utility functions.

"""

import abc
import sys

 # Reset
NULL = '\033[0m'

# Transparent color.
TRANSPARENCY = '\033[8m'

# Colors
WHITE    = '\033[01m'
RED      = '\033[31m'
GREEN    = '\033[32m'
YELLOW   = '\033[33m'
BLUE     = '\033[34m'
ORANGE   = '\033[91m'

def red(message, end=True):
    """
    Returns a red formated message.

    :param message: The message to format.
    :para end: Determine whether the color message should stop on message.
    :return: The formated message.
    """
    return _format(RED, message, end=end)

def green(message, end=True):
    """
    Returns a green formated message.

    :param message: The message to format.
    :para end: Determine whether the color message should stop on message.
    :return: The formated message.
    """
    return _format(GREEN, message, end=end)

def yellow(message, end=True):
    """
    Returns a yellow formated message.

    :param message: The message to format.
    :para end: Determine whether the color message should stop on message.
    :return: The formated message.
    """
    return _format(YELLOW, message, end=end)

def blue(message, end=True):
    """
    Returns a blue formated message.

    :param message: The message to format.
    :para end: Determine whether the color message should stop on message.
    :return: The formated message.
    """
    return _format(BLUE, message, end=end)

def orange(message, end=True):
    """
    Returns a orange formated message.

    :param message: The message to format.
    :para end: Determine whether the color message should stop on message.
    :return: The formated message.
    """
    return _format(ORANGE, message, end=end)

def _format(color, message, end=True):
    """
    Format a given message to a color string.

    :param color: The color string.
    :param message: The message.
    :param end: Reset color on end of message.
    :return: The formated string.
    """
    return '{}{}{}'.format(color, message, NULL if end else '')

def to_bytes(object):
    """
    Convert an object to bytes-like object.

    :param object:<object> The object to be converted.
    :return:<bytes> A bytes-like object.
    """
    if type(object) is str:
        return object.encode()

    return bytes(object)

class DataInterface(abc.ABCMeta if sys.version_info[0] < 3 else abc.ABC):
    """Base class to handle incomming/outgoing data through socket connections."""
    def __init__(self, content=None, params={}, code=None):
        """Instantiate request with data and parameters."""
        raise NotImplementedError('Can not instantiate an abstract class.')

    @abc.abstractproperty
    def content(self):
        """Get content."""
        pass

    @abc.abstractproperty
    def params(self):
        """Get the parameters as dictionary."""
        pass

    @abc.abstractmethod
    def get_raw(self):
        """Get raw packet to be sent over socket."""
        pass

    def __len__(self):
        """The length of the packet in bytes."""
        return len(self.get_raw())

    def __repr__(self):
        """Return the bytes representation of the class."""
        return self.__bytes__

    def __bytes__(self):
        """Return the bytes-like object representation of the packet."""
        return self.get_raw()
