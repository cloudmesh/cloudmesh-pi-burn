"""
Implementation of a function the set the WIFI configuration.
This function is primarily developed for a Raspberry PI
"""
import textwrap

from cloudmesh.common.console import Console
from cloudmesh.common.util import writefile
from cloudmesh.common.sudo import Sudo
from cloudmesh.burn.wifi.ubuntu import Wifi as WifiUbuntu
from cloudmesh.burn.wifi.raspberryos import Wifi as WifiRaspberryOs


def Wifi(os="raspberry"):
    if os == "raspberry":
        WifiRaspberryOs
    else:
        WifiUbuntu
