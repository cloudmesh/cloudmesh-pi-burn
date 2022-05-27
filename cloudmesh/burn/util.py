import hashlib
import os
import platform
import sys

from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile

# import mmap

BUF_SIZE = 65536


def sha1sum(filename=None):
    Console.info("Verifying sha1")
    h = hashlib.sha1()
    with open(filename, 'rb') as f:
        # with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
        #     h.update(mm)
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def sha256sum(filename=None):
    Console.info("Verifying sha256")
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        # with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
        #     h.update(mm)
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            h.update(data)
    return h.hexdigest()
