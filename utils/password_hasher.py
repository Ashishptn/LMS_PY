import os
import hashlib
import base64

def hash_password_aspnet_core(password):
    version = 0x01
    prf = 0x0001  # HMACSHA256
    iter_count = 10000
    salt_length = 16
    subkey_length = 32

    salt = os.urandom(salt_length)
    subkey = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iter_count, dklen=subkey_length)

    output = bytearray()
    output.append(version)
    output.extend(prf.to_bytes(4, byteorder='little'))
    output.extend(iter_count.to_bytes(4, byteorder='little'))
    output.extend(salt_length.to_bytes(4, byteorder='little'))
    output.extend(salt)
    output.extend(subkey)

    return base64.b64encode(output).decode('utf-8')
