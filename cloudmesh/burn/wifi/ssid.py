from cloudmesh.common.Shell import Shell
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_windows

def get_ssid():
    ssid = ""
    try:
        if os_is_mac():
            command = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
            r = Shell.run(command).replace("\t", "").splitlines()
            ssid = Shell.cm_grep(r, " SSID:")[0].split(":")[1].strip()
        elif os_is_linux():
            command = "iwgetid -r"
            ssid = Shell.run(command).strip()
        elif os_is_pi():
            command = "iwgetid -r"
            ssid = Shell.run(command).strip()
        elif os_is_windows():
            command = "netsh wlan show interfaces"
            r = Shell.run(command).replace("\t", "").splitlines()
            ssid = Shell.cm_grep(r, " SSID ")[0].split(":")[1].strip()
    except:
        pass

    return ssid

