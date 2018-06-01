# -*- coding: UTF -*-

import unittest
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from simple_backdoor.packets import Packet, FileDownloadPacket, FileUploadPacket
from simple_backdoor.protocol import build_packet, encode, CMD, UPLOAD, DOWNLOAD

class PacketsTest(unittest.TestCase):
    def test_packet_class(self):
        content = 'bar'
        params = {'foo': 'baz'}
        packet = Packet(content=content, params=params)
        self.assertEqual(packet.content, content)
        self.assertEqual(packet.params, params)
        self.assertEqual(build_packet(CMD, content, params), packet.__bytes__())

    def test_file_upload_packet_class(self):
        filename = os.path.abspath('tests/resources/foo.txt')
        with open(filename, 'rb') as buffer:
            content = buffer.read()
        packet = FileUploadPacket(filename)
        self.assertEqual(packet.content, content)
        self.assertEqual(packet.params, {'name': 'foo.txt'})
        self.assertEqual(build_packet(UPLOAD, content, {'name': 'foo.txt'}), bytes(packet))

    def test_file_download_packet_class(self):
        filename = 'foo.bar'
        packet = FileDownloadPacket(filename)
        self.assertIsNone(packet.content)
        self.assertEqual(packet.params, {'filename': filename})
        self.assertEqual(build_packet(DOWNLOAD, params={'filename': filename}), bytes(packet))

    def test_null_packet_class(self):
        params = {'foo': 'baz'}
        packet = Packet(params=params)
        self.assertIsNone(packet.content)
        self.assertEqual(build_packet(CMD, None, params), packet.__bytes__())

    def test_packet_with_another_code_class(self):
        packet = Packet(code=UPLOAD)
        self.assertEqual(build_packet(UPLOAD, None), packet.__bytes__())

    def test_file_upload_packet_with_non_unicode_char_class(self):
        filename = os.path.abspath('tests/resources/foo.txt')
        with open(filename, 'rb') as buffer:
            original = buffer.read()
        content = original + b'\x81'
        with open(filename, 'wb') as buffer:
            buffer.write(content)
        packet = FileUploadPacket(filename)
        self.assertEqual(build_packet(UPLOAD, content, {'name': 'foo.txt'}), packet.__bytes__())
        with open(filename, 'wb') as buffer:
            buffer.write(original)

if __name__ == '__main__':
    unittest.main()
