#!/usr/bin/env python3
"""
Unit testing module for the RLE project. For learning purposes, a small
unit testing class is defined and used here.

This module needs to use the code in ../src, so it begins by setting
the PYTHONPATH appropriately.

(c) Sandro Seivane, 2022
$$LICENSE(GPL)
"""

# pylint: disable=exec-used, protected-access

import io
import os
import sys
from typing import Any, Callable, Sequence
from os.path import dirname

sys.path.append(f'{dirname(__file__)}/../src')  # (*)
import rle   # pylint: disable=import-error, wrong-import-position

# (*) Note that sys.path.append('../src') would force us to always
# run this script from the 'pycoder/tests' directory because '../src'
# is relative to the current directory.

TEST_ALL = True

################################################################################
#
#           UNIT TEST LIBRARY
#
#           Developed using class style OOP.
#
################################################################################

class TestSuit:
    def __init__(self, verbose: bool):
        self._failed_count = 0
        self._succ_count = 0
        self._verbose = verbose
    #:
    def assert_(self, test_code: str):
        try:
            exec(f'assert {test_code}', None)
        except AssertionError:
            print(f'{test_code:58} --> FAILED!')
            self._failed_count += 1
        else:
            print(f'{test_code:58} : OK')
            self._succ_count += 1
    #:
    def assert_eq(
            self, 
            test_name: str,
            test_fn: Callable[..., Any],
            test_args: Sequence,
            want: Any
    ):
        result = ''
        try:
            result = test_fn(*test_args)
            assert want == result
        except AssertionError:
            print(f'{test_name:58} --> FAILED!')
            if self._verbose:
                print(f'got: {result}\nwant: {want}\n')
            self._failed_count += 1
        else:
            print(f'{test_name:58} : OK')
            self._succ_count += 1
    #:
    def setup_and_assert(
            self, 
            setup_code: str, 
            test_name: str, 
            test_fn: Callable[..., Any], 
            test_args: Sequence, 
            want: Any
    ):
        # pylint: disable=too-many-arguments
        print(setup_code)
        exec(setup_code)
        self.assert_eq(test_name, test_fn, test_args, want)
    #:
    def assert_exception(self, test_code: str, exception: Exception):
        # pylint: disable=broad-except
        try:
            exec(f'assert {test_code}', None)
        except exception:
            msg = f'{test_code} raises {exception.__name__}'
            print(f'{msg:58} : OK')
            self._succ_count += 1
        except Exception as ex:
            msg = f'{test_code} raises {type(ex).__name__} instead of {exception}'
            print(f'{msg:58} --> FAILED')
            self._failed_count += 1
        else:
            msg = f'{test_code} doesn\'t raise any exception'
            print(f'{msg:58} --> FAILED')
            self._failed_count += 1
    #:
    def summary(self):
        print(f"\n\n{15 * '*'} SUMMARY {15 * '*'}\n")
        if self._failed_count == 0:
            print(f"All {self._succ_count} tests passed SUCCESSFULLY!")
        else:
            print(f"{self._failed_count + self._succ_count} TESTS:")
            print(f"        {self._failed_count:>4} FAILED")
            print(f"        {self._succ_count:>4} passed")
        #:
        print()
    #:
#:

def run_tests():
    tester = TestSuit('-v' in sys.argv)

    if TEST_ALL:
        raw_1 = b'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW'
        raw_2 = b'W' * 300 + b'A' * 255 + b'B' * 19
        rle_A1 = b'\x0cW\x01B\x0cW\x03B\x18W\x01B\x0eW'
        rle_A2 = b'\xffW-W\xffA\x13B'
        rle_B1 = b'WW\x0cBWW\x0cBB\x03WW\x18BWW\x0e'
        rle_B2 = b'WW\xffWW-AA\xffBB\x13'

        rle_C1 = open('dadosX.bin.A.rle', 'rb').read()
        rle_C2 = open('dadosX.bin.B.rle', 'rb').read()
        rle_D1 = open('dadosY.bin.A.rle', 'rb').read()
        rle_D2 = open('dadosY.bin.B.rle', 'rb').read()
        rle_E1 = open('dadosZ.bin.A.rle', 'rb').read()
        rle_E2 = open('dadosZ.bin.B.rle', 'rb').read()

        def encode_in_mem(encode, test_data: bytes):
            in_ = io.BytesIO(test_data)
            out = io.BytesIO()
            encode(in_, out)
            return out.getvalue()
        #:

        def decode_in_mem(decode, rle_data: bytes):
            return encode_in_mem(decode, rle_data)
        #:

        def encode_file_and_read(
                method: rle.RLEMethod, 
                in_file_path: str, 
        ):
            out_file_path = f'{in_file_path}.rle'
            rle.encode_rle(method, in_file_path, out_file_path)
            data = open(out_file_path, 'rb').read()
            os.remove(out_file_path)
            return data
        #:

        tests_eq = {       #    test_fn    |        test_args        |  wanted result
            'encode_mA1': (encode_in_mem, (rle._encode_mA, raw_1), rle_A1),
            'encode_mA2': (encode_in_mem, (rle._encode_mA, raw_2), rle_A2),
            # 'decode_mA1': (decode_in_mem, (rle._decode_mA, rle_A1), raw_1),
            # 'decode_mA2': (decode_in_mem, (rle._decode_mA, rle_A2), raw_2),
            'encode_mB1': (encode_in_mem, (rle._encode_mB, raw_1), rle_B1),
            'encode_mB2': (encode_in_mem, (rle._encode_mB, raw_2), rle_B2),
            # 'decode_mB1': (decode_in_mem, (rle._decode_mB, rle_B1), raw_1),
            # 'decode_mB2': (decode_in_mem, (rle._decode_mB, rle_B2), raw_2),
            'encode_file_C1': (encode_file_and_read, (rle.RLEMethod.A, 'dadosX.bin'), rle_C1),
            # 'encode_file_C2': (encode_file_and_read, (rle.RLEMethod.B, 'dadosX.bin'), rle_C2),
            # 'encode_file_D1': (encode_file_and_read, (rle.RLEMethod.A, 'dadosY.bin'), rle_D1),
            # 'encode_file_D2': (encode_file_and_read, (rle.RLEMethod.B, 'dadosY.bin'), rle_D2),
            # 'encode_file_E1': (encode_file_and_read, (rle.RLEMethod.A, 'dadosZ.bin'), rle_E1),
            # 'encode_file_E2': (encode_file_and_read, (rle.RLEMethod.B, 'dadosZ.bin'), rle_E2),

            # 'teste_pateta'   : (sum,           ((1, 2, 3),             ),  7   ),
        }

        for test_name, test in tests_eq.items():
            tester.assert_eq(
                test_name=test_name,
                test_fn=test[0],
                test_args=test[1],
                want=test[2]
            )

        # tester.assert_('1 < 2')
        # tester.assert_('"alberto" == "alberto"')

        tester.summary()
#:

run_tests()
