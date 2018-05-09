#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The protocol responses module.
======================

Handle protocol packet responses. The protocol responses have a simple response code
indicating whether the client understood the packet been sent. The handler also construct
a Packet object from packet content.

"""

import protocol
from packets import Packet

class ResponseHandler(object):
    """The handler of response packets."""
    def __init__(self, on_error=None):
        """
        Construct a ResponseHandler object.

        :param on_error: The function to execute when packet had error on response.
        :return: The ResponseHandler object.
        """
        self._on_error = None

    def on_error(self, on_error):
        """
        Register a on_error callback event.

        :param on_error: The function to execute when packet had error on response.
        """
        if not callable(on_error):
            raise TypeError('The on_error argument must be a callback, not {}'.format(on_error.__class__.__name__))
        self._on_error = on_error

    def handle(self, packet):
        """
            Handle a raw protocol packet and return the constructed packet. Since it follows the protocol codes,
            the only allowed response codes are the protocols response codes, any other code will raise a InvalidPacketCode
            exception.

            :param packet: The packet content.
            :return: The packet object or None.
        """
        # Decode the packet fragments.
        code, data, params = protocol.from_packet(packet)

        if code is protocol.SUCCESS_CODE:
            # The packet was succesfull understood by the client.
            return Packet(content=data, params=params, code=code)
        elif code is protocol.ERROR_CODE:
            # The packet had errors or not had been understood by the client.
            if self._on_error is not None:

                # Execute the on error event with the packet data.
                self._on_error(data)
            return None
        else:
            raise protocol.InvalidPacketCode('Invalid response code. Code: {}'.format(code))
