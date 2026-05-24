from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json

import sqlite3
import gzip
import os

from base64 import b16decode, urlsafe_b64encode

def load_config(filepath):
    config = None
    with open(filepath, "rb") as f:
        config = json.loads(f.read())
    for key in config:
        if isinstance(config[key], str):
            config[key] = b16decode(config[key])
    return config

def key_creation(password, salt):
    kdf=PBKDF2HMAC(algorithm = hashes.SHA256(), salt=salt, iterations=1024, length=32, backend=default_backend())
    key=Fernet(urlsafe_b64encode(kdf.derive(password)))
    return key

def encryption(b, password, salt):
    f=key_creation(password, salt)
    safe=f.encrypt(b)
    return safe

def decryption(safe, password, salt):
    f=key_creation(password, salt)
    b=f.decrypt(safe)
    return b

def open_cdb(filename, password, salt):
    if not os.path.exists(filename):
        con = sqlite3.connect(':memory:')
        return con
    f=gzip.open(filename,'rb')
    safe=f.read()
    f.close()
    content=decryption(safe,password,salt)
    content=content.decode('utf-8')
    con=sqlite3.connect(':memory:')
    con.executescript(content)
    return con

def decrypt_cdb(filename, password, salt):
    f=gzip.open(filename,'rb')
    safe=f.read()
    f.close()
    content=decryption(safe,password,salt)
    fp=gzip.open(filename+".decoded.db",'wb')
    fp.write(content)
    fp.close()

def save_cdb(con, filename, password, salt):
    fp=gzip.open(filename,'wb')
    b=b''
    for line in con.iterdump():
        b+=bytes('%s\n','utf8') % bytes(line,'utf8')
    b=encryption(b,password, salt)
    fp.write(b)
    fp.close()
