import base64
from Crypto.Cipher import AES
from Crypto import Random
import hashlib

class AESCipher(object):
    '''
    responsible for the cipher of the messages
    '''

    def __init__(self, key):
        """
        constructor to AESCipher
        :param key: the key to decrypt and encrypt
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        """
        takes a string and encrypts it
        :param raw: the msg
        :return: the msg encrypted
        """
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        """
        gets a msg and decrypts it
        :param enc: encrypted msg (
        :return: decrypted msg
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        """

        :param s: String
        :return: makes it 64 bits
        """
        if type(s) == bytes:
            s = s.decode()

        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]