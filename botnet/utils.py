import logging
import inspect
from urllib.request import urlopen
import socket
import uuid
import os
import random

def log(info, level='debug'):
    logging.basicConfig(level=logging.DEBUG, handlers=[])
    
    file_name = inspect.stack()[1].filename
    logger = logging.getLogger(file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    getattr(logger, level if hasattr(logger, level) else 'debug')(str(info))

def computer_name():
    return os.getenv('COMPUTERNAME', 'unknown')


def public_ip():
    return urlopen('http://api.ipify.org').read().decode()


def local_ip():
    return socket.gethostbyname(socket.gethostname())


def mac_address():
    mac_num = hex(uuid.getnode()).replace('0x', '').zfill(12)
    mac = ':'.join(mac_num[i:i+2] for i in range(0, 11, 2)).upper()
    return mac


def username():
    return os.getenv('USER', os.getenv('USERNAME', 'user'))

def variable(length=6):
    return ''.join(random.choice([chr(n) for n in range(97,123)] + [chr(i) for i in range(48,58)] + [chr(z) for z in range(65,91)]) for _ in range(length))


