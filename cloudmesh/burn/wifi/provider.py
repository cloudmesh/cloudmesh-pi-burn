"""
Implementation of a function the set the WIFI configuration.
This function is primarily developed for a Raspberry PI
"""

from cloudmesh.burn.wifi.raspberryos import Wifi as WifiRaspberryOs
from cloudmesh.burn.wifi.ubuntu import Wifi as WifiUbuntu


def Wifi(os="raspberry"):
    if os == "raspberry":
        WifiRaspberryOs
    else:
        WifiUbuntu
