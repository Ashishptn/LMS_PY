import base64
import hashlib
import hmac

def verify_aspnet_password(password, hashed_password):
    try:
        # Decode base64 hash
        decoded = base64.b64decode(hashed_password)
        print(decoded)
        # Check if Identity v3
        if decoded[0] != 0x01:
            print("Unsupported Identity version.")
            return False

        # Identity v3 layout:
        # 1 byte format marker + 3 bytes version/reserved + 4 bytes PRF + 4 bytes iter count +
        # 4 bytes salt length + salt + subkey length + subkey

        salt_length = 16
        subkey_length = 32
        iterations = 10000

        # The salt starts from byte index 13
        salt = decoded[13:13 + salt_length]
        stored_subkey = decoded[13 + salt_length:13 + salt_length + subkey_length]
        print(stored_subkey)
        # Generate a subkey from the provided password
        derived_subkey = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=subkey_length
        )

        # Securely compare
        return hmac.compare_digest(stored_subkey, derived_subkey)

    except Exception as e:
        print("Password verification failed:", e)
        return False
