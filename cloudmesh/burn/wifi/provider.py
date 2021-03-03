"""
Implementation of a function the set the WIFI configuration.
This function is primarily developed for a Raspberry PI
"""

from cloudmesh.burn.wifi.raspberryos import Wifi as WifiRaspberryOs
from cloudmesh.burn.wifi.ubuntu import Wifi as WifiUbuntu


# noinspection PyPep8Naming
def Wifi(card_os="raspberry"):
    if card_os == "raspberry":
        return WifiRaspberryOs
    else:
        return WifiUbuntu
