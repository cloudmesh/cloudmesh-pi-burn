import os
from pathlib import Path
from cloudmesh.common.console import Console

import requests
# TODO: fin out if this is still needed by simply outcommenting it
# import cloudmesh.burn.requests_ssl_key_fix

import sys

# noinspection PyPep8

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
