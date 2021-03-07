import os
import sys

from cloudmesh.burn.burner.raspberryos import Burner as RaspberryOsBurner
from cloudmesh.burn.gui import Gui
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.usb import USB
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_windows
from cloudmesh.common.JobScript import JobScript
from cloudmesh.common.Shell import windows_not_supported
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand


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

    @staticmethod
    def gui(arguments=None):

        if os_is_windows():
            Console.error("Only supported on Pi and Linux. On Mac you will "
                          "need to have ext4 write access.")
            return ""

        g = Gui(hostnames=arguments.hostnames, ips=arguments.ips)

        g.run()

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
            script = \
                """
                wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
                chmod +x pishrink.sh
                sudo mv pishrink.sh /usr/local/bin
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

    def firmware(self,action="check"):
        self.burner.firmware(action=action)

    def check(self,device=None):
        self.burner.check(device=device)

    def configure_wifi(self,ssid, psk=None, country=None, host=None):
        self.burner.configure_wifi(ssid, psk=psk, country=country, host=host)

    def mac(self, hostnames=None):
        self.burner.mac(hostnames=hostnames)

    def set_hostname(self, hostname):
        self.burner.set_hostname(hostname)

    def set_static_ip(self, ip):
        self.burner.set_static_ip(ip)

    def set_key(self, key):
        self.burner.set_key(key)

    def keyboard(self, country=None):
        self.burner.keyboard(country=country)

    def enable_ssh(self):
        self.burner.enable_ssh()

    def cluster(self, arguments=None):
        self.burner.cluster(arguments=arguments)

    @windows_not_supported
    def info(self,
             print_os=True,
             print_fdisk=True,
             print_stdout=True,
             output="table"):
        """
        Finds out information about USB devices

        TODO: should we rename print_stdout to debug? seems more in
              line with cloudmesh

        :param print_os:
        :type print_os:
        :param print_fdisk:
        :type print_fdisk:
        :param print_stdout: if set to True prints debug information
        :type print_stdout: bool
        :param output:
        :type output:
        :return: dict with details about the devices
        :rtype: dict
        """

        if print_os and print_stdout:
            if os_is_pi():
                banner("This is  Raspberry PI")
            elif os_is_mac():
                banner("This is Mac")
            elif os_is_windows():
                banner("This is a Windows Computer")
            elif os_is_linux():
                banner("This is a Linux Computer")
            else:
                Console.error("unkown OS")
                sys.exit(1)

        if os_is_pi() and print_fdisk and print_stdout:
            result = USB.fdisk("/dev/mmcblk0")
            if print_stdout:
                banner("Operating System SD Card")
                print(result)

        details = USB.get_from_usb()

        if print_stdout:
            banner("USB Device Probe")
            print(Printer.write(
                details,
                order=["address",
                       "bus",
                       "idVendor",
                       "idProduct",
                       "hVendor",
                       "hProduct",
                       "iManufacturer",
                       "iSerialNumber",
                       "usbVersion",
                       "comment"],
                header=["Adr.",
                        "bus",
                        "Vendor",
                        "Prod.",
                        "H Vendor",
                        "H Prod.",
                        "Man.",
                        "Ser.Num.",
                        "USB Ver.",
                        "Comment"],
                output=output)
            )

        # devices = USB.get_devices()

        # banner("Devices found")

        # print ('\n'.join(sorted(devices)))

        if os_is_mac():

            names = USB.get_dev_from_diskutil()

            details = USB.get_from_diskutil()
        else:
            details = USB.get_from_dmesg()

        if print_stdout:
            banner("SD Cards Found")

            if os_is_mac():
                print("We found the follwing cards:")
                print("  - /dev/" + "\n  - /dev/".join(names))
                print()
                print("We found the follong file systems on these disks:")
                print()

            print(Printer.write(details,
                                order=[
                                    "dev",
                                    "info",
                                    "formatted",
                                    "size",
                                    "active",
                                    "readable",
                                    "empty",
                                    "direct-access",
                                    "removable",
                                    "writeable"],
                                header=[
                                    "Path",
                                    "Info",
                                    "Formatted",
                                    "Size",
                                    "Plugged-in",
                                    "Readable",
                                    "Empty",
                                    "Access",
                                    "Removable",
                                    "Writeable"],
                                output=output)
                  )

            # lsusb = USB.get_from_lsusb()
            # from pprint import pprint
            # pprint (lsusb)

            # endors = USB.get_vendor()
            # print(vendors)

            # udev = subprocess.getoutput("udevadm info -a -p  $(udevadm info -q path -n /dev/sda)")
            #
            # attributes = ["vendor","model", "model", "version", "manufacturer",
            #     "idProduct", "idVendor"]
            # for line in udev.splitlines():
            #    if any(word in line for word in attributes):
            #        print(line)

        if print_stdout:

            if os_is_linux():
                card = SDCard()
                m = card.ls()

                banner("Mount points")
                if len(m) != 0:
                    print(Printer.write(m,
                                        order=["name", "path", "type", "device", "parameters"],
                                        header=["Name", "Path", "Type", "Device", "Parameters"],
                                        output=output))
                else:
                    Console.warning("No mount points found. Use cms burn mount")
                    print()

        # Convert details into a dict where the key for each entry is the device
        details = {detail['dev']: detail for detail in details}

        return details


# multi_self.burner.burn_inventory
