import logging
import inspect
import sys
from urllib.request import urlopen, Request
import socket
import uuid
import os
import time
import threading
import functools

def log(info, level='debug'):
    logging.basicConfig(level=logging.DEBUG, handlers=[])
    
    file_name = inspect.stack()[1].filename
    logger = logging.getLogger(file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    getattr(logger, level if hasattr(logger, level) else 'debug')(str(info))


def public_ip():
    return urlopen('http://api.ipify.org').read().decode()


def local_ip():
    return socket.gethostbyname(socket.gethostname())


def mac_address():
    return ':'.join(hex(uuid.getnode()).strip('0x').strip('L')[i:i+2] for i in range(0,11,2)).upper()


def username():
    return os.getenv('USER', os.getenv('USERNAME', 'user'))

