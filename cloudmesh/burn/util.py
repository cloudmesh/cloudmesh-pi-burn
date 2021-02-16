import os
import platform
import sys

from cloudmesh.common.util import readfile

import hashlib
# import mmap

BUF_SIZE = 65536


def sha1sum(filename):
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


def sha256sum(filename):
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


def os_is_windows():
    """
    Checks if the os is windows

    :return: True is windows
    :rtype: bool
    """
    return platform.system() == "Windows"


def os_is_linux():
    """
    Checks if the os is linux

    :return: True is linux
    :rtype: bool
    """
    try:
        content = readfile('/etc/os-release')
        return platform.system() == "Linux" and "raspbian" not in content
    except:
        return False


def os_is_mac():
    """
    Checks if the os is macOS

    :return: True is macOS
    :rtype: bool
    """
    return platform.system() == "Darwin"


def os_is_pi():
    """
    Checks if the os is Raspberry OS

    :return: True is Raspberry OS
    :rtype: bool
    """
    try:
        content = readfile('/etc/os-release')
        return platform.system() == "Linux" and "raspbian" in content
    except:
        return False


def check_root(dryrun=False, terminate=True):
    """
    check if I am the root user. If not simply exist the program.

    TODO: should probably move to cloudmesh.common

    :param dryrun: if set to true, does not terminate if not root user
    :type dryrun: bool
    :param terminate: terminates if not root user and dryrun is False
    :type terminate: bool
    """
    uid = os.getuid()
    if uid == 0:
        print("You are executing a a root user")
    else:
        print("You do not run as root")
        if terminate and not dryrun:
            sys.exit()
