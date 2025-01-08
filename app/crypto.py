import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AESCipher:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, data.encode(), None)
        return nonce + ct

    def decrypt(self, data):
        aesgcm = AESGCM(self.key)
        nonce = data[:12]
        ct = data[12:]
        return aesgcm.decrypt(nonce, ct, None).decode("utf-8")
