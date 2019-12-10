import sys
import os
from pathlib import Path
from time import sleep

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
    :return:
    """
    if mode != 'r' and mode != 'rb':
        print("ERROR: incorrect mode : expected \'r\' or \'rb\' given {}\n".format(mode))
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
