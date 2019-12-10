import sys
import os
from pathlib import Path

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
        print( f"ERROR: incorrect mode : expected \'r\' or \'rb\' given {mode}\n")
    else:
        with open(Path(os.path.expanduser(filename)), mode)as f:
            content = f.read()
            f.close()
        return content
    
def check_root():
    
    uid = os.getuid()
    if uid == 0:
        print("you are executing a a root user")
    else:
        print("you dont have root user permissions")
       
