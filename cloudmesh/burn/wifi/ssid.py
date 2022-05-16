from cloudmesh.common.Shell import Shell
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_windows
from cloudmesh.common.Printer import Printer
import subprocess



def get_ssid():
    ssid = ""
    r = ""
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
            r = ''
            try:
                command = " netsh wlan show profiles"
                r = Shell.run(command)#.splitlines()
                r = Shell.cm_grep(r, "User Profile")
                r = [line.split(":")[1].strip() for line in r]
                print('Found ssids:',r)
                ssid = input('Enter ssid from list:')
            except subprocess.CalledProcessError as e:
                if "The Wireless AutoConfig Service (wlansvc) is not running" in str(e.output):
                    print("Machine is not configured for wifi")
    except:  # noqa
        pass
    return ssid
