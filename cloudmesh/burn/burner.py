import crypt
import os
import random
import re
import string
import subprocess
import sys
import textwrap
import time

import humanize
from cloudmesh.burn.image import Image
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.usb import USB
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_windows
from cloudmesh.common.JobScript import JobScript
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import sudo_readfile
from cloudmesh.common.util import sudo_writefile
from cloudmesh.common.util import writefile
from cloudmesh.common.util import yn_choice


# def dmesg():
#    return subprocess.getoutput(f"dmesg")


def gen_strong_pass():
    """
    Generates a password from letters, digits and punctuation

    :return: password
    :rtype: str
    """
    length = random.randint(10, 15)
    password_characters = \
        string.ascii_letters + \
        string.digits + \
        string.punctuation
    return ''.join(random.choice(password_characters) for i in range(length))


def windows_not_supported(f):
    def wrapper(*args, **kwargs):
        host = get_platform()
        if host == "windows":
            Console.error("Not supported on windows")
            return ""
        else:
            return f(*args, **kwargs)

    return wrapper


# noinspection PyPep8
class Burner(object):

    def __init__(self, dryrun=False):
        """
        Initializes the burner

        TODO: dryrun may not be specified for all functions. Not yet enabled.
              Hence do not use dryrun

        :param dryrun: if True only the commands will be listed that would
                       be executed
        """
        self.dryrun = dryrun
        self.hostname = None
        self.keypath = None

    @staticmethod
    def detect():
        if os_is_mac():
            details = USB.get_from_diskutil()
        else:
            details = USB.get_from_dmesg()
        return details

    @windows_not_supported
    def check(self, device="/dev/sdX"):
        """
        This method checks what configurations are placed on the PI se card

        :param device:
        :type device:
        :return:
        :rtype:
        """

        data = {
            "ssh": None,
            "hostname": None,
            "ip": None,
            "wifi": None,
            "psk": None,
            "ssid": None,
            "auth_key": None
        }

        host = get_platform()

        if host == "windows":
            Console.error("Not yet implemented for this OS")
            return ""

        card = SDCard(host=host)
        # ssh

        try:
            data["ssh"] = \
                os.path.exists(f'{card.boot_volume}/ssh') or \
                os.path.exists(f'{card.root_volume}/etc/systemd/system/sshd.service')
        except Exception as e:
            data["ssh"] = str(e)

        # auth_key

        try:
            data["auth_key"] = \
                os.path.exists(f'{card.root_volume}/home/pi/.ssh/authorized_keys')
            if data["auth_key"]:
                content = readfile(f"{card.root_volume}/home/pi/.ssh/authorized_keys")
                data["auth_key"] = content.split()[-1]
        except Exception as e:
            data["auth_key"] = str(e)

        # hostname

        try:
            content = readfile(f"{card.root_volume}/etc/hostname").strip()
            data['hostname'] = content
        except Exception as e:
            data["hostname"] = str(e)

        # ip

        try:
            content = readfile(f"{card.root_volume}/etc/dhcpcd.conf")
            for line in content.splitlines():
                if line.startswith('static ip_address='):
                    data['ip'] = line[18:]
            if data['ip'] is None:
                data['ip'] = 'False'
        except Exception as e:
            data["ip"] = str(e)

        # wifi

        try:
            location = f"{card.boot_volume}/wpa_supplicant.conf"
            data["wifi"] = os.path.exists(location)

            if data["wifi"]:
                lines = readfile(location).splitlines()
                for line in lines:
                    for tag in ["ssid", "psk"]:
                        if f'{tag}=' in line:
                            data[tag] = line.split(f'{tag}=')[1].replace('"', "")

            else:
                data["wifi"] = False
                data["ssid"] = None
                data["psk"] = None

        except Exception as e:  # noqa: F841

            data["wifi"] = False
            data["ssid"] = None
            data["psk"] = None

        banner("Card Check")
        print(Printer.attribute(
            data,
            sort_keys=False,
            order=[
                "hostname",
                "ip",
                "ssh",
                "auth_key",
                "wifi",
                "psk",
                "ssid"
            ]
        ))

    @windows_not_supported
    def firmware(self, action="check"):
        """
        Checks or update the firmware
        :param action: the cations to be performed. It is "check" or "update"
        :type action: str
        """

        def _execute(command):
            print(command)
            print()
            os.system(command)
            print()

        if not os_is_pi():
            Console.error("This command can only be run on a PI")
        else:
            if action == "check":
                _execute('sudo apt update')
                _execute('sudo apt install rpi-eeprom')
                _execute("sudo rpi-eeprom-update")
                _execute("vcgencmd bootloader_version")
                print("* https://www.raspberrypi.org/documentation/hardware/raspberrypi/booteeprom.md")
                print()
            elif action == "update":
                _execute('sudo apt update')
                _execute('sudo apt install rpi-eeprom')
                _execute("sudo rpi-eeprom-update -a")
                os.system("sudo reboot")

    @windows_not_supported
    def shrink(self, image=None):
        if image is None:
            Console.error("Image must have a value")
        image = path_expand(image)
        command = f"sudo /usr/local/bin/pishrink.sh {image}"
        print(command)
        os.system(command)

    @windows_not_supported
    def install(self):
        """
        Installs /usr/local/bin/pishrink.sh
        Installs parted
        :return:
        :rtype:
        """

        if os_is_linux() or os_is_pi():
            banner("Installing pishrink.sh into /usr/local/bin")
            script = \
                """
                wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
                chmod +x pishrink.sh
                sudo mv pishrink.sh /usr/local/bin
                sudo apt install parted -y > $HOME/tmp.log
                """

            result = JobScript.execute(script)
            print(Printer.write(result,
                                order=["name", "command", "status", "stdout", "returncode"]))
        else:
            raise NotImplementedError

    @windows_not_supported
    def backup(self, device=None, to_file=None, blocksize="4M"):
        if device is None:
            Console.error("Device must have a value")
        if to_file is None:
            Console.error("To file must have a value")
        else:
            to_file = path_expand(to_file)
            command = f"sudo dd if={device} bs={blocksize} |" \
                      f" pv -w 80 |" \
                      f"dd of={to_file} bs={blocksize} conv=fsync status=progress"
            print(command)
            os.system(command)

    @windows_not_supported
    def copy(self, device=None, from_file="latest"):
        if device is None:
            Console.error("Device must have a value")
        self.burn_sdcard(image=from_file, device=device)

    @windows_not_supported
    def info(self,
             print_os=True,
             print_fdisk=True,
             print_device_probe=True,
             print_stdout=True,
             output="table"):
        """
        Finds out information about USB devices

        TODO: should we rename print_stdout to debug? seems more in
              line with cloudmesh

        :param print_stdout: if set to True prints debug information
        :type print_stdout: bool
        :return: dict with details about the devices
        :rtype: dict
        """

        print("dryrun:    ", self.dryrun)

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
            details = USB.get_from_diskutil()
        else:
            details = USB.get_from_dmesg()

        if print_stdout:
            banner("SD Cards Found")
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
                card = SDCard(card_os="raspberry")
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

        #
        # use also lsub -v
        #

        # see also
        # https://raspberry-pi-guide.readthedocs.io/en/latest/system.html
        # this is for fedora, but should also work for raspbian

    def system_exec(self, command):
        """
        System command that uses subprocess to execute terminal commands
        Returns the stdout of the command

        TODO: check type of return<

        :param command: the command
        :type command: str
        :return: the stdout of the command
        :rtype: str
        """
        # if self.dryrun:
        #     print(command)
        # else:

        print("Executing", command)

        os.system(command)

        # res = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        # if res[0] != 0 and res[0] != 32:
        #    Console.warning(
        #        f'Warning: "{command}" did not execute properly -> {res[1]} :: exit code {res[0]}')

        # return res[1]
        return ""

    @windows_not_supported
    def burn_sdcard(self, image=None, tag=None, device=None, blocksize="4M"):
        """
        Burns the SD Card with an image

        :param image: Image object to use for burning (used by copy)
        :type image: str
        :param tag: tag object used for burning (used by sdcard)
        :type tag: str
        :param device: Device to burn to, e.g. /dev/sda
        :type device: str
        :param blocksize: the blocksize used when writing, default 4M
        :type blocksize: str
        """
        if image and tag:
            Console.error("Implementation error, burn_sdcard can't have image "
                          "and tag.")
            return ""

        Console.info("Burning...")
        if image is not None:
            image_path = image
        else:
            image = Image().find(tag=tag)

            if image is None:
                Console.error("No matching image found.")
                return ""
            elif len(image) > 1:
                Console.error("Too many images found")
                print(Printer.write(image,
                                    order=["tag", "version"],
                                    header=["Tag", "Version"]))
                return ""

            image = image[0]

            image_path = Image().directory + "/" + Image.get_name(image["url"]) + ".img"

        banner("Burning the SDCard")
        print("Image:    ", image_path)
        print("Device:   ", device)
        print("Blocksize:", blocksize)
        print()

        if os_is_linux() or os_is_pi():

            if device is None:
                Console.error("Please specify a device")
                return

            command = f"sudo dd if={image_path} |" \
                      f" pv -w 80 |" \
                      f" sudo dd of={device} bs={blocksize} conv=fsync status=progress"
            print(command)
            os.system(command)

            command = "sync"
            print(command)
            os.system(command)
        elif os_is_mac():

            details = USB.get_from_diskutil()

            output = "table"
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

            #
            # get size
            #

            size = humanize.naturalsize(os.path.getsize(image_path))

            # size = details[0]['size']
            n, unit = size.split(" ")
            unit = unit.replace("GB", "G")
            unit = unit.replace("MB", "M")
            n = int(round(float(n)))
            print(n, unit)
            size = f"{n}{unit}"

            blocksize = blocksize.replace("M", "m")

            if yn_choice(f"Do you like to write to {device} the image {image_path}"):

                # sudo dd if=/dev/rdiskX bs=1m | pv -s 64G | sudo dd of=/dev/rdiskY bs=1m

                command = f"sudo dd if={image_path} bs={blocksize} |" \
                          f' pv -s {size} |' \
                          f" sudo dd of={device} bs={blocksize}"
                print(command)

                if not yn_choice("CONTINUE? Please execute on your on risk"):
                    return ""

                os.system(command)

        else:
            raise NotImplementedError("Only implemented to be run on a PI")

    def mac(self, hostnames=None):
        """
        Sets the hostname for which we probe the MAC addresses

        :param hostname: the hostname
        :type hostname: str
        """
        self.hostnames = hostnames

        print(hostnames)
        Console.error("Not yet implemented")
        return ""

    @windows_not_supported
    def set_hostname(self, hostname):
        """
        Sets the hostname on the sd card

        :param hostname: the hostname
        :type hostname: str
        :param mountpoint: the mountpunt of the device on which the hostname
                           is found
        :type mountpoint: str
        """
        self.hostname = hostname
        if os_is_pi() or os_is_linux():
            card = SDCard()
        else:
            raise NotImplementedError

        mountpoint = card.root_volume
        # write the new hostname to /etc/hostname
        if not self.dryrun:
            self.system_exec(
                f'echo {hostname} | sudo cp /dev/stdin {mountpoint}/etc/hostname')
        else:
            print()
            print("Write to /etc/hostname")
            print(hostname)

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        if not self.dryrun:
            # with open(f'{mountpoint}/etc/hosts', 'r') as f:  # read /etc/hosts
            f = sudo_readfile(f'{mountpoint}/etc/hosts')
            # lines = [l for l in f.readlines()][:-1]  # ignore the last line
            lines = f[:-1]
            newlastline = '\n127.0.1.1 ' + hostname + '\n'

        if not self.dryrun:
            new_hostsfile_contents = '\n'.join(lines) + newlastline
            sudo_writefile(f'{mountpoint}/etc/hosts', new_hostsfile_contents)
        else:
            print()
            print("Write to /etc/hosts")
            print('127.0.1.1 ' + hostname + '\n')

        # Adds the ip and hostname to /etc/hosts if it isn't already there.

    def add_to_hosts(self, ip):
        # with open('/etc/hosts', 'r') as host_file:
        #     hosts = host_file.readlines()
        hosts = sudo_readfile('/etc/hosts')

        replaced = False
        for i in range(len(hosts)):
            ip_host = hosts[i].split()

            if len(ip_host) > 1:
                if ip_host[0] == ip:
                    ip_host[1] = self.hostname
                    hosts[i] = f"{ip_host[0]}\t{ip_host[1]}"
                    replaced = True

                elif ip_host[1] == self.hostname:
                    ip_host[0] = ip
                    hosts[i] = f"{ip_host[0]}\t{ip_host[1]}"
                    replaced = True
        if not replaced:
            hosts.append(f"{ip}\t{self.hostname}")

        config = ""
        for line in hosts:
            config = config + line + '\n'

        sudo_writefile('/etc/hosts', config)

    @windows_not_supported
    def set_static_ip(self, ip, iface="eth0", mask="24"):
        """
        Sets the static ip on the sd card for the specified interface
        Also writes to manager hosts file for easy access

        :param ip: ips address
        :type ip: str
        :param mountpoint: the mountpunt of the device on which the ip
                           is found
        :type mountpoint: str
        :param iface: the network Interface
        :type iface: str
        :param mask: the subnet Mask
        :type mask: str
        :return:
        :rtype:
        """
        # TODO:
        # router_ip statically set to default ip configured with cms bridge
        # create. Rewrite to consider the IP of the manager on iface

        if os_is_pi() or os_is_linux():
            card = SDCard()
        else:
            raise NotImplementedError

        mountpoint = card.root_volume
        if self.hostname is not None:
            self.add_to_hosts(ip)
        router_ip = '10.1.1.1'

        iface = f'interface {iface}'
        static_ip = f'static ip_address={ip}/{mask}'
        static_routers = f'static routers={router_ip}'

        curr_config = sudo_readfile(f'{mountpoint}/etc/dhcpcd.conf')
        if iface in curr_config:
            Console.warning("Found previous settings. Overwriting")
            # If setting already present, replace it and the static ip line
            index = curr_config.index(iface)
            try:
                if 'static ip_address' not in curr_config[index + 1]:
                    Console.warning(
                        "Missing static ip_address assignment. Overwriting line")
                curr_config[index + 1] = static_ip

            except IndexError:
                Console.error(f'{mountpoint}/etc/dhcpcd.conf ends abruptly. Aborting')
                sys.exit(1)

        else:
            curr_config.append(iface)
            curr_config.append(static_ip)
            curr_config.append(static_routers)
            curr_config.append('\n')
            # curr_config.append('nolink\n')

        sudo_writefile(f'{mountpoint}/etc/dhcpcd.conf', '\n'.join(curr_config))

    # TODO:
    # Deprecated function as dhcpcd.conf is the recommended file for
    # configuring static network configs. Should we keep this?
    #
    # def set_static_ip2(self, ip, mountpoint, iface="eth0", mask="16"):
    #     """
    #     Sets the static ip on the sd card for the specified interface
    #     Also writes to manager hosts file for easy access

    #     :param ip: ips address
    #     :type ip: str
    #     :param mountpoint: the mountpunt of the device on which the ip
    #                        is found
    #     :type mountpoint: str
    #     :param iface: the network Interface
    #     :type iface: str
    #     :param mask: the subnet Mask
    #     :type mask: str
    #     :return:
    #     :rtype:
    #     """

    #     # Adds the ip and hostname to /etc/hosts if it isn't already there.
    #     def add_to_hosts(ip):
    #         # with open('/etc/hosts', 'r') as host_file:
    #         #     hosts = host_file.readlines()
    #         hosts = sudo_readfile('/etc/hosts')

    #         replaced = False
    #         for i in range(len(hosts)):
    #             ip_host = hosts[i].split()

    #             if len(ip_host) > 1:
    #                 if ip_host[0] == ip:
    #                     ip_host[1] = self.hostname
    #                     hosts[i] = f"{ip_host[0]}\t{ip_host[1]}\n"
    #                     replaced = True

    #                 elif ip_host[1] == self.hostname:
    #                     ip_host[0] = ip
    #                     hosts[i] = f"{ip_host[0]}\t{ip_host[1]}\n"
    #                     replaced = True
    #         if not replaced:
    #             hosts.append(f"{ip}\t{self.hostname}\n")

    #         # with open('/etc/hosts', 'w') as host_file:
    #         #     host_file.writelines(hosts)
    #         config = ""
    #         for line in hosts:
    #             config = config + line + '\n'

    #         sudo_writefile('/etc/hosts', config)

    #     # Add static IP and hostname to manager's hosts file and configure worker with static IP
    #     if not self.dryrun:
    #         add_to_hosts(ip)

    #         # Configure static LAN IP
    #         if iface == "eth0":
    #             interfaces_conf = textwrap.dedent(f"""
    #             auto {iface}
    #             iface {iface} inet static
    #                 address {ip}/{mask}
    #             """)
    #             # with open(f'{mountpoint}/etc/network/interfaces',
    #             #           'a') as config:
    #             #     config.write(interfaces_conf)
    #             sudo_writefile(f'{mountpoint}/etc/network/interfaces',
    #                            interfaces_conf, append=True)

    #         # Configure static wifi IP
    #         elif iface == "wlan0":
    #             dnss = \
    #                 self.system_exec_exec("cat /etc/resolv.conf | grep nameserver").split()[
    #                     1]  # index 0 is "nameserver" so ignore
    #             routerss = self.system_exec_exec(
    #                 "ip route | grep default | awk '{print $3}'")  # omit the \n at the end
    #             dhcp_conf = textwrap.dedent(f"""
    #                     interface wlan0
    #                     static ip_address={ip}
    #                     static routers={routerss}
    #                     static domain_name_servers={dnss}
    #                     """)
    #             # with open(f'{mountpoint}/etc/dhcpcd.conf', 'a') as config:
    #             #     config.write(dhcp_conf)
    #             sudo_writefile(f'{mountpoint}/etc/dhcpcd.conf', dhcp_conf,
    #                            append=True)
    #     else:
    #         print('interface eth0\n')
    #         print(f'static ip_address={ip}/{mask}')

    @windows_not_supported
    def set_key(self, name):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card

        :param name: name of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        :type name: str
        :param mountpoint: the mountpunt of the device on which the key
                           is found
        :type mountpoint: str
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys
        if os_is_pi() or os_is_linux():
            card = SDCard()
        else:
            raise NotImplementedError

        mountpoint = card.root_volume
        self.system_exec(f'mkdir -p {mountpoint}/home/pi/.ssh/')
        self.system_exec(f'cp {name} {mountpoint}/home/pi/.ssh/authorized_keys')

    @windows_not_supported
    def mount(self, device=None, card_os="raspberry"):
        """
        Mounts the current SD card
        """

        host = get_platform()
        card = SDCard(card_os=card_os, host=host)

        if os_is_pi() or os_is_linux():
            dmesg = USB.get_from_dmesg()

            # TODO Need a better way to identify which sd card to use for mounting
            # instead of iterating over all of them

            if not self.dryrun:
                self.system_exec('sudo sync')  # flush any pending/in-process writes

                for usbcard in dmesg:

                    dev = device or usbcard['dev']
                    print(dev)
                    sd1 = f"{dev}1"
                    sd2 = f"{dev}2"
                    try:
                        if os.path.exists(sd1):
                            Console.ok(f"mounting {sd1} {card.boot_volume}")
                            self.system_exec(f"sudo mkdir -p {card.boot_volume}")
                            self.system_exec(f"sudo mount -t vfat {sd1} {card.boot_volume}")
                    except Exception as e:
                        print(e)
                    try:
                        if os.path.exists(sd2):
                            Console.ok(f"mounting {sd2} {card.root_volume}")
                            self.system_exec(f"sudo mkdir -p {card.root_volume}")
                            self.system_exec(f"sudo mount -t ext4 {sd2} {card.root_volume}")
                    except Exception as e:
                        print(e)
            return ""

        elif os_is_mac():

            dev = USB.get_dev_from_diskutil()[0]
            volumes = [
                {"dev": f"{dev}s1", "mount": card.boot_volume},
                {"dev": f"{dev}s2", "mount": card.root_volume},
            ]
            for volume in volumes:

                dev = str(volume['dev'])
                mount = volume['mount']
                try:
                    if not os.path.exists(mount):
                        self.system_exec(f"sudo mkdir -p {mount}")
                        self.system_exec(f"sudo mount -t vfat {dev} {mount}")
                except Exception as e:
                    print(e)
            for volume in volumes:
                dev = str(volume['dev'])
                mount = volume['mount']

                if os.path.exists(mount):
                    Console.ok(f"Mounted {mount}")
                else:
                    Console.error(f"Could not mounted {mount}")

            return ""

        else:
            Console.error("Not yet implemented for your OS")
            return ""

        # Keeping in case this was needed. Worked without it in testing.
        # elif os_is_pi():
        #    if not self.dryrun:
        # wait for the OS to detect the filesystems
        # in burner.info(), formatted will be true if the card has
        #        FAT32
        #   filesystems on it
        #        counter = 0
        #        max_tries = 5
        #        b = Burner()
        #        while counter < max_tries:
        #            time.sleep(1)
        #            formatted = b.info(print_stdout=False)[device]['formatted']
        #            if formatted:
        #                break
        #            counter += 1
        #            if counter == max_tries:
        #                print("Timed out waiting for OS to detect filesystem"
        #                      " on the burned card")
        #                sys.exit(1)

    @windows_not_supported
    def unmount(self, device=None, card_os="raspberry"):
        """
        Unmounts the current SD card

        :param device: device to unmount, e.g. /dev/sda
        :type device: str
        """

        def _execute(msg, command):
            Console.ok(msg)
            try:
                os.system(command)
            except:
                # ignore error
                pass

        host = get_platform()
        card = SDCard(card_os=card_os, host=host)

        if not self.dryrun:
            self.system_exec('sudo sync')  # flush any pending/in-process writes

            if os_is_mac() or os_is_linux() or os_is_pi():
                if device:
                    _execute(f"eject {device}", f"sudo eject {device}")
                    os.system("sync")
                _execute(f"unmounting {card.boot_volume}", f"sudo umount {card.boot_volume}")
                _execute(f"unmounting  {card.root_volume}", f"sudo umount {card.root_volume}")
                os.system("sync")

                rm = [f"sudo rmdir {card.boot_volume}",
                      f"sudo rmdir {card.root_volume}"]

                for command in rm:
                    _execute(command, command)
            elif host == "macos":

                _execute(f"unmounting {card.boot_volume}", f"diskutil umount {card.boot_volume}")

            else:
                Console.error("Not yet implemented for your OS")
                return ""

    @windows_not_supported
    def enable_ssh(self):
        """
        Enables ssh on next boot of sd card
        """
        host = get_platform()

        if host == "windows":
            Console.error("Not yet implemented for this OS")
            return ""

        if host in ['raspberry', "linux"]:
            sudo = True
        else:
            sudo = False

        card = SDCard(card_os="raspberry", host=host)
        if sudo:
            command = f'sudo touch {card.boot_volume}/ssh'
        else:
            command = f'touch {card.boot_volume}/ssh'

        self.system_exec(command)

        return ""

    # IMPROVE

    # TODO: docstring
    @windows_not_supported
    def disable_password_ssh(self):
        # sshd_config = self.filename("/etc/ssh/sshd_config")
        card = SDCard(card_os="raspberry")
        sshd_config = f'{card.root_volume}/etc/ssh/sshd_config'
        new_sshd_config = ""
        updated_params = False

        def sets_param(param, line):
            """See if a config line sets this parameter to something."""
            # front is only whitespace maybe a comment
            front = r'^\s*#?\s*'
            # only whitespace between param and value
            middle = r'\s+'
            # end can include a comment
            end = r'\s*(?:#.*)?$'
            re_sets_param = front + param + middle + r'.*' + end
            return re.search(re_sets_param, line) is not None

        force_params = [
            ("ChallengeResponseAuthentication", "no"),
            ("PasswordAuthentication", "no"),
            ("UsePAM", "no"),
            ("PermitRootLogin", "no"),
        ]

        found_params = set()
        # with open(sshd_config, 'r') as f:
        f = sudo_readfile(sshd_config)

        for line in f:
            found_a_param = False
            for param, value in force_params:
                if sets_param(param, line):
                    # Only set the parameter once
                    if param not in found_params:
                        new_sshd_config += param + " " + value + "\n"
                        updated_params = True
                    found_a_param = True
                    found_params.add(param)
            if not found_a_param:
                new_sshd_config += line
        # Check if any params not found
        for param, value in force_params:
            if param not in found_params:
                new_sshd_config += param + " " + value + "\n"
                updated_params = True
        if updated_params:
            # NOTE: This is actually necessary, see comment in method
            #
            # as we no longer do it on osx, we need to identify if this is still needed
            #
            # self.truncate_file(sshd_config)
            # with open(sshd_config, "w") as f:
            #     f.write(new_sshd_config)
            sudo_writefile(sshd_config, new_sshd_config)

    @windows_not_supported
    def configure_wifi(self,
                       ssid,
                       psk=None,
                       card_os='raspberry',
                       host=None,
                       country=None):
        """
        Sets the wifi. Only works for psk based wifi

        :param ssid: the ssid
        :type ssid: str
        :param psk: the psk
        :type psk: str
        :param card_os: the os on the sdcard
        :type card_os: str
        :param host: the machine os running the command
        :type host: str
        :param country: two digit country code for rf settings
        :type country: str
        """

        country = country or 'US'

        if psk:
            wifi = textwrap.dedent("""\
                    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
                    update_config=1
                    country={country}

                    network={{
                            ssid=\"{network}\"
                            psk=\"{psk}\"
                    }}""".format(network=ssid, psk=psk, country=country))
        else:
            wifi = textwrap.dedent("""\
                    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
                    update_config=1
                    country={country}

                    network={{
                            ssid=\"{network}\"
                            key_mgmt=NONE
                    }}""".format(network=ssid, country=country))

        card = SDCard(card_os=card_os, host=host)
        path = f"{card.boot_volume}/wpa_supplicant.conf"
        if self.dryrun:
            print("DRY RUN - skipping:")
            print("Writing wifi ssid:{} psk:{} to {}".format(ssid,
                                                             psk, path))
            return ""

        if os_is_mac():
            writefile(path, wifi)
        else:
            sudo_writefile(path, wifi)

        return ""

    @windows_not_supported
    def format_device(self, device='dev/sdX', hostname=None, title="UNTITLED", unmount=False):
        """
        Formats device with one FAT32 partition

        WARNING: make sure you have the right device, this command could
                 potentially erase your OS

        :param device: The device on which we format
        :type device: str
        :param hostname: the hostname
        :type hostname: str
        """

        def _execute(msg, command):
            banner(msg, c=".")
            try:
                os.system(command)
            except:
                # ignore error
                pass

        def prepare_sdcard():
            # ensures a card is detected and unmounted
            Console.ok(f'sudo eject -t {device}')
            self.system_exec(f'sudo eject -t {device}')
            time.sleep(3)
            device_basename = os.path.basename(device)
            result = Shell.run('lsblk')
            if device_basename in result.split():
                for line in result.splitlines():
                    line = line.split()
                    if device_basename in line[0] and len(line) > 6:
                        Console.ok(f'sudo umount {line[6]}')
                        self.system_exec(f'sudo umount {line[6]}')
                return True
            else:
                Console.error("SD Card not detected. Please reinsert "
                              "card reader. ")
                if not yn_choice("Card reader re-inserted? No to cancel "
                                 "operation"):
                    return False
                else:
                    time.sleep(3)
                    return prepare_sdcard()

        if os_is_linux() or os_is_pi():

            banner(f"format {device}")

            if not prepare_sdcard():
                return False

            script = f"""
                ls /media/pi
                sudo parted {device} --script -- mklabel msdos
                sudo parted {device} --script -- mkpart primary fat32 1MiB 100%
                sudo mkfs.vfat -n {title} -F32 {device}1
                sudo parted {device} --script print""".strip().splitlines()
            for line in script:
                _execute(line, line)

            _execute("sync", "sync")
            if unmount:
                time.sleep(1)
                self.unmount()  # without dev we unmount but do not eject. If
                # we completely eject, burn will fail to detect the device.
                time.sleep(1)

            Console.ok("Formatted SD Card")

        elif os_is_mac():

            details = USB.get_dev_from_diskutil()

            # checking if string contains list element
            valid = any(entry in device for entry in details)

            if not valid:
                Console.error("this device can not be used for formatting")
                return ""

            elif len(details) > 1:
                Console.error("For security reasons, please only put one USB writer in")
                return ""

            else:

                details = USB.get_from_diskutil()

                output = "table"
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

                print()
                if yn_choice(f"Do you like to format {device} as {title}"):
                    _execute(f"Formatting {device} as {title}",
                             f"sudo diskutil eraseDisk FAT32 {title} MBRFormat {device}")

        else:
            raise NotImplementedError("Not implemented for this OS")

        return True

    @windows_not_supported
    def load_device(self, device='dev/sdX'):
        """
        Loads the USB device via trayload

        :param device: The device on which we format
        :type device: str
        :param hostname: the hostname
        :type hostname: str
        """
        if os_is_linux() or os_is_pi():

            banner(f"load {device}")
            os.system(f"sudo eject -t {device}")

        else:
            raise Console.error("Not implemented for this OS")

    # This is to prevent desktop access of th pie (directly plugging monitor, keyboard, mouse into pi, etc.)
    #
    # Currently, ssh login is only possible with an authorized key. (No passwords)
    # Plugging pi directly into desktop, however, will still prompt for a user and password.
    # I can't figure out how to disable it

    @windows_not_supported
    def disable_terminal_login(self, mountpoint, password):
        """
        disables and replaces the password with a random string so that by
        accident the pi can not be logged into. The only way to login is via the
        ssh key

        :param mountpoint: the mountpount for the system
        :type mountpoint: str
        :param password: the password for login
        :type password: str
        :return: file in /etc/shadow
        :rtype: a written file
        """

        # Generates random salt for password generation
        def random_salt(length=10):
            letters_and_digits = string.ascii_letters + string.digits
            return ''.join(
                random.choice(letters_and_digits) for i in range(length))

        salt = random_salt()
        if password is not None:
            pswd = crypt.crypt(password, f'$6${salt}')
        else:
            raise NotImplementedError()

        # Make sure there's an 'x' in /etc/passwd
        #        with open(f'{mountpoint}/etc/passwd', 'r') as f:
        #            info = [l for l in f.readlines()]

        info = sudo_readfile(f'{mountpoint}/etc/passwd')

        for i in range(len(info)):
            inf = info[i].split(":")
            if inf[0] == 'pi':
                inf[1] = 'x'
                info[i] = ':'.join(inf)

        content = '\n'.join(info)

        # with open(f'{mountpoint}/etc/passwd', 'w') as f:
        #     f.writelines(info)

        sudo_writefile(f'{mountpoint}/etc/passwd', content)

        # Add it to shadow file
        # with open(f'{mountpoint}/etc/shadow', 'r') as f:
        #     data = [l for l in f.readlines()]

        data = sudo_readfile(f'{mountpoint}/etc/shadow')

        content = ""
        for i in range(len(data)):
            dat = data[i].split(":")
            if dat[0] == 'pi':
                dat[1] = pswd
                data[i] = ':'.join(dat)

        content = '\n'.join(data)

        # with open(f'{mountpoint}/etc/shadow', 'w') as f:
        #     f.writelines(data)
        sudo_writefile(f'{mountpoint}/etc/shadow', content)


class MultiBurner(object):
    """
    This class uses a single or multicard burner to burn SD Cards. It detects
    how many SD Cards are there and uses them. We assume no other USB devices
    are plugged in other than a keyboard or a mouse.

    """

    # System command that uses subprocess to execute terminal commands
    # Returns the stdout of the command
    def system_exec(self, command):
        """

        :param command:
        :return:
        """
        res = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        if res[0] != 0:
            Console.warning(
                f'Warning: "{command}" did not execute properly -> {res[1]} :: exit code {res[0]}')

        return res[1]

    # noinspection PyUnboundLocalVariable
    def burn_all(self,
                 image="latest",
                 device=None,
                 blocksize="4M",
                 progress=True,
                 hostnames=None,
                 ips=None,
                 key=None,
                 password=None,
                 ssid=None,
                 psk=None,
                 formatting=True,
                 tag='latest-lite'):
        """
        TODO: provide documentation

        :param image:
        :type image:
        :param device:
        :type device:
        :param blocksize:
        :type blocksize:
        :param progress:
        :type progress:
        :param hostnames:
        :type hostnames:
        :param ips:
        :type ips:
        :param key:
        :type key:
        :param password:
        :type password:
        :param ssid:
        :type ssid:
        :param psk:
        :type psk:
        :param formatting:
        :type formatting:
        :return:
        :rtype:
        """

        # :param devices: string with device letters

        # print (device)

        #
        # define the dev
        #
        devices = {}  # dict of {device_name: empty_status}
        #
        # probe the dev
        #
        # pprint(Burner().info())
        info_statuses = Burner().info()

        # If the user specifies a particular device, we only care about that
        # device

        if device is not None:
            for dev in device:
                devices[dev] = info_statuses[dev]['empty']
            # Change to empty to skip next loop
            info_statuses = {}

        for device in info_statuses.keys():
            # print("call the info command on the device and "
            #      "figure out if an empty card is in it")
            # change the status based on what you found
            devices[device] = info_statuses[device]['empty']

        # if we detect a non empty card we interrupt and tell
        # which is not empty.
        # (print out status of the devices in a table)
        device_statuses = devices.values()
        if False in device_statuses:
            print("\nEmpty status of devices:")
            for dev, empty_status in devices.items():
                x = "" if empty_status else "not "
                Console.info(f"Device {dev} is {x}empty")
        print()

        # detect if there is an issue with the cards, readers
        # TODO what exactly should be done here?

        # ask if this is ok to burn otherwise
        burn_all = yn_choice("Format the card before burning?")

        # if no burn all of them for which we have status "empty card"
        if not burn_all:
            # delete from devices dict any non-empty devices
            devices_to_delete = []
            for device in devices.keys():
                if devices[device]:
                    # can't delete while iterating
                    devices_to_delete.append(device)
            for device in devices_to_delete:
                del devices[device]

        print("Burning these devices:")
        print(' '.join(devices.keys()))

        keys = list(devices.keys())
        count = 0
        for i in range(len(hostnames)):
            # for device, status in devices.items():
            # We might be using one device slot to burn multiple cards
            device = keys[i % len(keys)]
            # status = devices[device]
            hostname = hostnames[i]
            ip = None if not ips else ips[i]

            self.burn(image, device, blocksize, progress, hostname,
                      ip, key, password, ssid, psk, formatting, tag)

            count += 1
            Console.info(f'Burned card {count}')
            print()
            Console.info('Please remove the card')
            print()
            self.system_exec('tput bel')  # ring the terminal bell to notify user
            if i < len(hostnames) - 1:
                if (i + 1) != ((i + 1) % len(keys)):
                    choice = input(
                        f"Slot {keys[(i + 1) % len(keys)]} "
                        "needs to be reused. Do you wish to continue? [y/n] ")
                    while (choice != 'y') and (choice != 'n'):
                        choice = input("Please use [y/n] ")
                    if choice == 'n':
                        break
                    elif choice == 'y':
                        input('Insert next card and press enter...')
                print('Burning next card...')
                print()

        Console.info(f"You burned {count} SD Cards")
        Console.ok("Done :)")

    def burn(self,
             image="latest",
             device=None,
             blocksize="4M",
             progress=True,
             hostname=None,
             ip=None,
             key=None,
             password=None,
             ssid=None,
             psk=None,
             formatting=True,
             tag='latest-lite'):
        """
        Burns the image on the specific device

        TODO: provide documentation

        :param image:
        :type image:
        :param device:
        :type device:
        :param blocksize:
        :type blocksize:
        :param progress:
        :type progress:
        :param hostname:
        :type hostname:
        :param ip:
        :type ip:
        :param key:
        :type key:
        :param password:
        :type password:
        :param ssid:
        :type ssid:
        :param psk:
        :type psk:
        :param formatting:
        :type formatting:
        :return:
        :rtype:
        """
        # TODO
        card = SDCard()
        # boot_volume = card.boot_volume
        root_volume = card.root_volume
        if key is None:
            key = '~/.ssh/id_rsa.pub'

        elif key == 'root':
            key = f'/{key}/.ssh/id_rsa.pub'

        else:
            key = f'/home/{key}/.ssh/id_rsa.pub'

        # don't do the input() after burning the last card
        # use a counter to check this

        counter = 0
        burner = Burner()

        print("counter", counter)
        StopWatch.start(f"create {device} {hostname}")

        if formatting:
            success = burner.format_device(device=device, hostname=hostname)
            if not success:
                Console.warning("Skipping card due to failed format. "
                                "Continuing with next hostname.")
                return

        burner.burn_sdcard(tag=tag, device=device, blocksize=blocksize)
        burner.mount(device=device)
        burner.set_hostname(hostname)
        burner.disable_terminal_login(root_volume, password)
        if ssid:
            Console.warning("In the future, try to interface with the workers via "
                            "ethernet/switch rather than WiFi")
            burner.configure_wifi(ssid, psk)
        burner.enable_ssh()
        burner.disable_password_ssh()
        burner.set_key(key)
        if ip:
            interface = "wlan0" if ssid is not None else "eth0"
            burner.set_static_ip(ip, iface=interface)

        burner.unmount(device=device)
        # for some reason, need to do unmount twice for it to work properly
        # burner.unmount(device)
        time.sleep(2)
        StopWatch.stop(f"create {device} {hostname}")
        StopWatch.status(f"create {device} {hostname}", True)
