from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_pi
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import Console
from cloudmesh.common.prettytable import PrettyTable
import subprocess


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
            try:
                try:
                    r = Shell.run('netsh wlan show interfaces').strip().splitlines()
                    ssid = Shell.cm_grep(r, ' SSID')[0].split(':')[1].strip()
                except subprocess.CalledProcessError as e:
                    if "The Wireless AutoConfig Service (wlansvc) is not running" in str(e.output):
                        print("Machine is not configured for wifi")
            except:
                command = "netsh wlan show profiles"
                r = Shell.run(command)  # .splitlines()
                r = Shell.cm_grep(r, "User Profile")
                r = [line.split(":")[1].strip() for line in r]
                x = PrettyTable(["SSIDs"])
                for item in r:
                    x.add_row([item])
                x.align = "l"
                x.align["SSID"] = "l"
                looping = True
                while looping:
                    print(x)
                    ssid = input('Enter ssid from list:\n')
                    if ssid not in r:
                        if not yn_choice(f'The entered SSID is not in the list. Are you sure you want to '
                                         f'use {ssid}? (type Y and press Enter to use {ssid}) '):
                            Console.ok('Showing the list of SSIDs again...\n')
                        else:
                            looping = False
                    else:
                        looping = False
    except:  # noqa
        pass
    return ssid
