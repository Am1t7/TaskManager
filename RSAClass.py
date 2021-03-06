from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
class RSAClass:
    '''
    responsible for the keys of the server and the client
    '''
    def __init__(self):
        self._keyPair = None
        self._generate_keys()

    def _generate_keys(self):
        '''
        no input.
        generate the RSA couple keys
        :return:
        '''
        self._keyPair = RSA.generate(3072)

    def get_public_key_pem(self):
        '''
        gets the public key
        :return:
        '''
        pubkey = self._keyPair.publickey()
        pubkeyPEM = pubkey.exportKey()
        return pubkeyPEM

    def decrypt_msg(self, encdata):
        '''
        decrypt an encrypted mag
        :param encdata: the encrypted msg
        :return:
        '''
        private_key = PKCS1_OAEP.new(self._keyPair)
        return private_key.decrypt(encdata)




def encrypt_msg(data, pubkeyPEM):
    '''
    encrypt message with the given public key
    :param data: the plain text in string
    :param pubkey: the public key
    :return: encrypted message
    '''
    result = None
    try:
        pubkey = RSA.import_key(pubkeyPEM)
    except Exception as e:
        print(e)
    else:
        encryptor = PKCS1_OAEP.new(pubkey)
        result = encryptor.encrypt(data.encode())
    return result