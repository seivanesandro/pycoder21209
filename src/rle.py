"""
This module implements a RLE compressor and decompressor. Two RLE
methods are implemented here:

    A - Each ocurrence of a new byte is replaced by a counter with the 
        number of consecutive occurrences and the byte itself.
        Examples: 
            1) b'LLLLARRB' -> b'\x04L\x01A\x02R\x01B'.
            2) b'ABC'      -> b'\x01A\x01B\x01C'

    B - Only series with repetition (two or more consecutive occurrences
        of the same byte) are replaced by a double ocurrence of the
        byte and a counter. Bytes that don't repeat are passed directly
        to the output stream. 
        Examples: 
            1) b'LLLLARRB' -> b'LL\x04ARR\x02B'.
            2) b'ABC'      -> b'ABC'
        A double occurrence of the encoded byte "tells" the decoder that
        the next byte is a counter, whereas a byte that doesn't repeat 
        is copied directly to the output stream.

Please consult Wikipedia to obtain more information about RLE in general
and these specific methods.

(c) Sandro Seivane, 2022
$$LICENSE(GPL)
"""

from enum import Enum
import io
from msilib.schema import Binary
from typing import BinaryIO
import time
from datetime import datetime

class RLEMethod(Enum):
    A = b'\x21'      # 33 or b'!'
    B = b'\x8a'      # 138
#:

def encode_rle(method: RLEMethod, in_file_path: str, out_file_path: str):
    encode_fn = {
        RLEMethod.A: _encode_mA,
        RLEMethod.B: _encode_mB,
    }[method]
    with open(in_file_path, 'rb') as in_file:
        with open(out_file_path, 'wb') as out_file:
            out_file.write(method.value)
            out_file.write(int(time.time()).to_bytes(4,'big'))
            encode_fn(in_file, out_file)
#:

def _encode_mA(in_file: BinaryIO, out_file: BinaryIO):
    def write_fn(curr_byte: bytes, count: int):
        out_file.write(_int_to_byte(count))
        out_file.write(curr_byte)
    #:
    _do_encode(in_file, write_fn)
#:

def _encode_mB(in_file: BinaryIO, out_file: BinaryIO):
    def write_fn(curr_byte: bytes, count: int):
        out_file.write(curr_byte)
        if count > 1:
            out_file.write(curr_byte)
            out_file.write(_int_to_byte(count))
    #:
    _do_encode(in_file, write_fn)
#:

def _do_encode(in_: BinaryIO, write_fn):
    """
    This is the outline of the algorithm:
        1. curr_byte = 1st byte in 'in_'.
        2. count = 1
        3. For each byte in 'in_':
            3.1 If next_byte equals curr_byte:
                3.1.1 Increment count
            3.2 Else: (série de bytes consecutivos chegou ao fim)
                3.2.1 Write curr_byte and count
                3.2.2 count = 1
                3.2.3 curr_byte = next_byte
        4. Write last curr_byte and count
    NOTE: This outline ignores what happens when count > 255
    """
    curr_byte = in_.read(1)
    count = 1
    for next_byte in iter(lambda: in_.read(1), b''):
        if next_byte == curr_byte:
            count += 1
            if count == 256:
                write_fn(curr_byte, count - 1)
                count = 1
        else:
            write_fn(curr_byte, count)
            count = 1
            curr_byte = next_byte
    #:
    if curr_byte:
        write_fn(curr_byte, count)
    #:
#:

def decode_rle(in_file_path: str, out_file_path: str):
    with open(in_file_path, 'rb') as in_file:
        method = RLEMethod(in_file.read(1))
        decode_fn = {
            RLEMethod.A: _decode_mA,
            RLEMethod.B: _decode_mB,
        }[method]
        timestamp = int.from_bytes(in_file.read(4), 'big')
        with open(out_file_path, 'wb') as out_file:
            decode_fn(in_file, out_file)
    print ("Decompressed", in_file_path, "into", out_file_path, 'using method', method)
    print('Compression date/time:', datetime.fromtimestamp(timestamp))
#:

def _decode_mA(in_file: BinaryIO, out_file: BinaryIO):

    for count, next_byte_int in iter(lambda: in_file.read(2), b''):
        out_file.write(count* _int_to_byte(next_byte_int))
 #:       


def _decode_mB(in_file: BinaryIO, out_file: BinaryIO):
    """
    1. Em ciclo,  ler dois bytes de cada vez
        1.1 if not byte1:
            1.1.1. Fim ficheiro logo fim ciclo
        1.2 Se byte1=byte2 então
            1.2.1 Ler 3º byte com a contagem (count)
            1.2.2 Colocar na saída byte 1 count vezes
        1.3 Senão (ou seja, se byte1 != byte2)
            1.3.1. Escrever byte1
            1.3.2 Se houver byte2, então voltar a colocar na entrada byte2 (para que a próxima iteração começa a partir deste byte2)
    """
    
    for byte1, byte2 in iter(lambda: in_file.read(2), b''):
        if not byte1:
            break
        elif byte1 == byte2:
            count = in_file.read(1)
            out_file.write(count * _int_to_byte(byte1))
        else:
            out_file.write(_int_to_byte(byte1))
            if byte2:
                byte1=byte2
#:    


def _byte_to_int(byte: bytes):
    return int.from_bytes(byte)

#:
def _int_to_byte(byte: int) -> bytes:
  
    """
    This functions converts an integer between 0 and 255 to bytes.

    >>> int_to_byte(15)
    b'\x0f'
    >>> int_to_byte(254)
    b'\xfe'
    """
    return bytes([byte])
#:

 
# if __name__ == '__main__':
#     dados0_in = b''
#     dados0_A_out = b''
#     dados0_B_out = b''

#     dados1_in = b'WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWBWWWWWWWWWWWWWW'
#     dados1_A_out = b'\x0cW\x01B\x0cW\x03B\x18W\x01B\x0eW'
#     dados1_B_out = b'WW\x0cBWW\x0cBB\x03WW\x18BWW\x0e'

#     dados2_in = b'W' * 300 + b'A' * 255 + b'B' * 19
#     dados2_A_out = b'\xffW-W\xffA\x13B'
#     dados2_B_out = b'WW\xffWW-AA\xffBB\x13'

#     def _encode_in_mem(encode_fn, dados_in: bytes) -> bytes:
#         file_in = io.BytesIO(dados_in)
#         file_out = io.BytesIO()
#         encode_fn(file_in, file_out)
#         return file_out.getvalue()
    

#     def _test(dados_out_esperados: bytes, dados_out_obtidos: bytes):
#         if dados_out_esperados == dados_out_obtidos:
#             print('OK')
#         else:
#             print('NOK')
#             print(dados_out)
#     #:

#     #######

#     print('*** A ****')

#     dados_out = _encode_in_mem(_encode_mA, dados0_in)
#     _test(dados0_A_out, dados_out)

#     ########

#     dados_out = _encode_in_mem(_encode_mA, dados1_in)
#     _test(dados1_A_out, dados_out)

#     ########

#     dados_out = _encode_in_mem(_encode_mA, dados2_in)
#     _test(dados2_A_out, dados_out)

#     #######

#     print('\n*** B ****')

#     dados_out = _encode_in_mem(_encode_mB, dados0_in)
#     _test(dados0_B_out, dados_out)

#     ########

#     dados_out = _encode_in_mem(_encode_mB, dados1_in)
#     _test(dados1_B_out, dados_out)

#     ########

#     dados_out = _encode_in_mem(_encode_mB, dados2_in)
#     _test(dados2_B_out, dados_out)

 