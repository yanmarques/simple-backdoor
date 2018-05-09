# -*- coding: UTF -*-

import unittest
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from simple_backdoor import protocol

class TestProtocol(unittest.TestCase):
    def test_encode_with_bytes(self):
        encode = protocol.encode(b'\x81')
        self.assertTrue(encode.startswith(b'base64'))
        encode = protocol.encode(b'\x081')
        self.assertFalse(encode.startswith(b'base64'))

    def test_encode_with_string(self):
        value = 'a incredible str'
        encode = protocol.encode(value)
        self.assertEqual(encode, value)

    def test_decode_with_bytes(self):
        value = b'\x81'
        decode = protocol.decode(protocol.encode(value))
        self.assertEqual(value, decode)

    def test_decode_with_string(self):
        value = 'a incredible str'
        decode = protocol.decode(protocol.encode(value))
        self.assertEqual(value, decode)

    def test_build_fragments(self):
        one = ['test']
        many = ['test', 'test2', 'test3']

        def fragment_one():
            return one

        def fragment_many():
            return many

        wraper = protocol.build_fragments(fragment_one)
        self.assertEqual(wraper(), one[0] + protocol.EOF)

        wraper = protocol.build_fragments(fragment_many)
        self.assertEqual(wraper(), protocol.DELIMITER.join(many) + protocol.EOF)

    def test_build_packet_with_all_params(self):
        code = protocol.CMD
        content = 'test'
        params = {'foo': 'bar'}
        qs_params = 'foo=bar'
        packet = protocol.build_packet(code, content, params)
        self.assertEqual(packet, protocol.DELIMITER.join([code, content, qs_params]) + protocol.EOF)

    def test_build_packet_without_content(self):
        code = protocol.CMD
        params = {'foo': 'bar'}
        qs_params = 'foo=bar'
        packet = protocol.build_packet(code, None, params)
        self.assertEqual(packet, protocol.DELIMITER.join([code, protocol.NULL, qs_params]) + protocol.EOF)

    def test_build_packet_without_params(self):
        code = protocol.CMD
        content = 'no params'
        packet = protocol.build_packet(code, content)
        self.assertEqual(packet, protocol.DELIMITER.join([code, content, protocol.NULL]) + protocol.EOF)

    def test_build_packet_with_code(self):
        code = protocol.CMD
        packet = protocol.build_packet(code)
        self.assertEqual(packet, protocol.DELIMITER.join([code, protocol.NULL, protocol.NULL]) + protocol.EOF)

    def test_build_packet_with_invalid_code(self):
        with self.assertRaises(protocol.InvalidPacketCode):
            protocol.build_packet(protocol.ACK)

if __name__ == '__main__':
    unittest.main()
