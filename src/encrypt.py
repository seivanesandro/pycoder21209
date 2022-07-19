"""
Extends pycoder with methods do secure compression of data. There's
a generic interface based around two functions: 'encrypt' and 'decrypt'.
These two functions take a method ID, source, destination and password,
as well as extra options ('*args' and '**kargs').

This modules requires the cryptography library.

"""

from enum import Enum
import base64
import os
from io import BytesIO
from typing import BinaryIO
from string import ascii_letters
from random import sample

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


__all__ = [
    'CryptMethod',
    'encrypt_file',
    'encrypt',
    'decrypt_file',
    'decrypt',
]

################################################################################
##
##      GENERIC INTERFACE:
##
##      encrypt_file/encrypt and decrypt_file/decrypt are generic functions
##      that dispatch to the appropriate function based on the method 
##      ID (specified in the enumeration CryptMethod).
##
################################################################################

class CryptMethod(Enum):
    FERNET_SMALL = b'\x01'
    AES_CRYPTOGRAPHY = b'\x02'
#:

# Em alternativa:
#
# CryptMethod = Enum('CryptMethod', {
#     'FERNET_SMALL': b'\x01',
#     'AES_CRYPTOGRAPHY': b'\x02',
# })

def encrypt_file(
        method: CryptMethod, 
        file_path: str, 
        password: str, 
        *args,
        **kargs,
):
    temp_file_name = ''.join(sample(ascii_letters, 10))
    try:
        with open(file_path, 'rb') as in_:
            with open(temp_file_name, 'wb') as out:
                encrypt(method, in_, out, password.encode(), *args, **kargs)
        os.replace(temp_file_name, file_path)
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
    #:
#:

def encrypt(
        method_id: CryptMethod, 
        in_: BinaryIO,
        out: BinaryIO,
        password: bytes,
        *args,
        **kargs,
):
    encrypt_fn = {
        CryptMethod.FERNET_SMALL: encrypt_fernet_small,
        CryptMethod.AES_CRYPTOGRAPHY: encrypt_aes_cryptography,
    }[method_id]
    encrypt_fn(in_, out, password, *args, **kargs)
#:

def decrypt_file(
        method: CryptMethod, 
        file_path: str,
        password: str,
        *args,
        **kargs,
):
    temp_file_name = ''.join(sample(ascii_letters, 10))
    try:
        with open(file_path, 'rb') as in_:
            with open(temp_file_name, 'wb') as out:
                decrypt(method, in_, out, password.encode(), *args, **kargs)
        os.replace(temp_file_name, file_path)
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
    #:
#:

def decrypt(
        method_id: CryptMethod, 
        in_: BinaryIO,
        out:  BinaryIO,
        password: bytes,
        *args,
        **kargs,
):
    decrypt_fn = {
        CryptMethod.FERNET_SMALL: decrypt_fernet_small,
        CryptMethod.AES_CRYPTOGRAPHY: decrypt_aes_cryptography,
    }[method_id]
    decrypt_fn(in_, out, password, *args, **kargs)
#:

################################################################################
##
##      FERNET SMALL FILES
##
################################################################################

_FERNET_DEFAULT_SALT = b'0' * 16
_FERNET_KEY_SIZE = 32       # bytes (32B -> 256b)

def encrypt_fernet_small(
        in_: BinaryIO, 
        out: BinaryIO, 
        password: bytes, 
        salt: bytes=_FERNET_DEFAULT_SALT,
):
    """
    Taken from here: 
        https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_FERNET_KEY_SIZE,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(in_.read())
    out.write(token)
#:

def decrypt_fernet_small(
        in_: BinaryIO,
        out: BinaryIO,
        password: bytes,
        salt: bytes=_FERNET_DEFAULT_SALT,
):
    """
    Taken from here: 
        https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_FERNET_KEY_SIZE,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.decrypt(in_.read())
    out.write(token)
#:

################################################################################
##
##      AES CRYPTOGRAPHY
##
################################################################################

_AES_DEFAULT_SALT = b'0' * 16
_AES_KEY_SIZE = 32      # bytes (32B -> 256b)
_NONCE_SIZE = 16        # bytes
_BLOCK_SIZE = 65536     # bytes (65536 -> 64KB)

def encrypt_aes_cryptography(
        in_: BinaryIO, 
        out: BinaryIO, 
        password: bytes, 
        salt: bytes=_AES_DEFAULT_SALT,
):
    """
    Symmetric encryption using the AES algorithm from the cryptography
    library.

    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#cryptography.hazmat.primitives.ciphers.CipherContext
    https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/#algorithms
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_AES_KEY_SIZE,
        salt=salt,
        iterations=390000,
    )
    key = kdf.derive(password)
    nonce = os.urandom(_NONCE_SIZE)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()
    out.write(nonce)
    for block in iter(lambda: in_.read(_BLOCK_SIZE), b''):
        out.write(encryptor.update(block))
    out.write(encryptor.finalize())
#:

def decrypt_aes_cryptography(
        in_: BinaryIO,
        out: BinaryIO,
        password: bytes,
        salt: bytes=_AES_DEFAULT_SALT,
):
    """
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_AES_KEY_SIZE,
        salt=salt,
        iterations=390000,
    )
    key = kdf.derive(password)
    nonce = in_.read(_NONCE_SIZE)
    if not nonce or len(nonce) < _NONCE_SIZE:
        raise ValueError('Unable to decrypt stream: invalid nonce!')
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    decryptor = cipher.decryptor()
    for block in iter(lambda: in_.read(_BLOCK_SIZE), b''):
        out.write(decryptor.update(block))
    out.write(decryptor.finalize())
#:

################################################################################
##
##      QUICK TESTS (more tests should be added to tests/)
##
################################################################################

def _quick_tests():
    pwd = b'Kxy203#$'
    test_small_data = b'Bom dia, Alberto!\n' * 10000

    print(f"{'FERNET SMALL FILES':30s} : ", end='')
    in_stream = BytesIO(test_small_data)
    out_stream = BytesIO()
    encrypt_fernet_small(in_stream, out_stream, pwd)

    in_stream = BytesIO(out_stream.getvalue())
    out_stream = BytesIO()
    decrypt_fernet_small(in_stream, out_stream, pwd)
    assert out_stream.getvalue() == test_small_data
    print("OK")

    print(f"{'CRYPTOGRAPHY AES':30s} : ", end='')
    in_stream = BytesIO(test_small_data)
    out_stream = BytesIO()
    encrypt_aes_cryptography(in_stream, out_stream, pwd)

    in_stream = BytesIO(out_stream.getvalue())
    out_stream = BytesIO()
    decrypt_aes_cryptography(in_stream, out_stream, pwd)
    assert out_stream.getvalue() == test_small_data
    print("OK")
#:

if __name__ == '__main__':
    _quick_tests()
