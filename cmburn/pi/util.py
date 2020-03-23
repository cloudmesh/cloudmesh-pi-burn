import sys
import os
from pathlib import Path

import requests
import urllib3

# noinspection PyPep8
if True:
    ##############################################
    #
    # Ignore on pi:  DH KEY TOO SMALL
    #
    # see: https://stackoverflow.com/questions/38015537/python-requests-exceptions-sslerror-dh-key-too-small
    #

    requests.packages.urllib3.disable_warnings()
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'AES128-SHA'
    try:
        # noinspection PyPep8
        requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST = 'AES128-SHA'
    except AttributeError:
        # no pyopenssl support used / needed / available
        pass

    #
    ##############################################


# noinspection PyPep8Naming
def WARNING(*args, **kwargs):
    print("WARNING:", *args, file=sys.stderr, **kwargs)


def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    with open(Path(os.path.expanduser(filename)), 'w') as outfile:
        outfile.write(content)


def readfile(filename, mode='r'):
    """
    returns the content of a file
    :param filename: the filename
    :param mode:

    :return:
    """
    if mode != 'r' and mode != 'rb':
        print(f"ERROR: incorrect mode : expected 'r' or 'rb' given {mode}\n")
    else:
        with open(Path(os.path.expanduser(filename)), mode)as f:
            content = f.read()
            f.close()
        return content


def check_root(dryrun=False, terminate=True):
    uid = os.getuid()
    if uid == 0:
        print("You are executing a a root user")
    else:
        print("You do not run as root")
        if terminate and not dryrun:
            sys.exit()
