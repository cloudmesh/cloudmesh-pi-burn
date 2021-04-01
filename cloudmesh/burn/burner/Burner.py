import os
# import wget

from cloudmesh.burn.burner.raspberryos import Burner as RaspberryOsBurner
from cloudmesh.burn.usb import USB
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.common.JobScript import JobScript
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand


# class Burner(AbstractBurner):
class Burner:

    def __init__(self, card_os="raspberryos"):
        if "raspberry" in card_os:
            self.burner = RaspberryOsBurner()
        else:
            Console.error("Card OS not supported")

    def get(self):
        return self.burner

    @staticmethod
    def detect():
        if os_is_mac():
            details = USB.get_from_diskutil()
        else:
            details = USB.get_from_dmesg()
        return details

    def shrink(self, image=None):
        if image is None:
            Console.error("Image must have a value")
        image = path_expand(image)
        command = f"sudo /usr/local/bin/pishrink.sh {image}"
        print(command)
        os.system(command)

    def install(self):
        """
        Installs /usr/local/bin/pishrink.sh
        Installs parted
        :return:
        :rtype:
        """

        if os_is_mac():
            Console.error("This command is not supported on MacOS")
            return ""
        else:
            banner("Installing pishrink.sh into /usr/local/bin")
            script_name = Shell.download(
                'https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh', 'pishrink.sh', provider='system')
            script = \
                f"""
                chmod +x {script_name}
                sudo mv {script_name} /usr/local/bin
                """

            result = JobScript.execute(script)
            print(Printer.write(result,
                                order=["name", "command", "status", "stdout", "returncode"]))

            if os_is_linux() or os_is_pi():
                banner("Installing pishrink.sh into /usr/local/bin")
                script = \
                    """
                    sudo apt install parted -y > $HOME/tmp.log
                    """

                result = JobScript.execute(script)
                print(Printer.write(result,
                                    order=["name", "command", "status", "stdout", "returncode"]))

    def firmware(self, action="check"):
        self.burner.firmware(action=action)

    def check(self, device=None):
        self.burner.check(device=device)

    def configure_wifi(self, ssid, psk=None, country=None, host=None):
        self.burner.configure_wifi(ssid, psk=psk, country=country, host=host)

    def mac(self, hostnames=None):
        self.burner.mac(hostnames=hostnames)

    def set_hostname(self, hostname):
        self.burner.set_hostname(hostname)

    def set_static_ip(self, ip):
        self.burner.set_static_ip(ip)

    def set_cmdline(self, cmdline):
        self.burner.set_cmdline(cmdline)

    def set_key(self, key):
        self.burner.set_key(key)

    def keyboard(self, country=None):
        self.burner.keyboard(country=country)

    def enable_ssh(self):
        self.burner.enable_ssh()

    def cluster(self, arguments=None):
        self.burner.cluster(arguments=arguments)


# multi_self.burner.burn_inventory
