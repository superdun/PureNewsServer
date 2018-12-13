from pyDes import *
import base64


def encrypt_str(key,iv, data):

    method = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    k = method.encrypt(data)
    return base64.b64encode(k)


def decrypt_str(key,iv,data):
    method = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    k = base64.b64decode(data)
    return method.decrypt(k)