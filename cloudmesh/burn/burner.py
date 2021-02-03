import crypt
import os
import pathlib
import random
import re
import string
import subprocess
import sys
import textwrap
import time

import sys
import subprocess
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
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import sudo_readfile
from cloudmesh.common.util import sudo_writefile
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.util import readfile


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
    def wrapper(*args,**kwargs):
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

        :param dryrun: if True onle the commands will be listed that would
                       be executed
        """
        self.dryrun = dryrun
        self.hostname = None
        self.keypath = None

    @windows_not_supported
    def check(self, device="/dev/sdX"):
        """
        This method checks what configurations are placed on the PI se card

        @param device:
        @type device:
        @return:
        @rtype:
        """

        data = {
            "ssh": None,
            "hostname": None,
            "ip": None,
            "password": None,
            "shadow": None,
            "wifi": None,
            "psk": None,
            "ssid": None,
            "wifipassword": None
        }

        card = SDCard()

        # ssh

        try:
            self.mount(device)
            data["ssh"] = os.path.exists(card.boot_volume)
        except Exception as e:
            data["ssh"] = str(e)
        # hostname

        content = readfile(f"{card.root_volume}/etc/hostname").strip()
        data['hostname'] = content

        # ip

        data["ip"] = "not yet implemented"

        # passwod

        data["password"] = "not yet implemented"

        data["shadow"] = os.path.exists(f"{card.boot_volume}/etc/shadow")

        # wifi

        try:
            location = f"{card.boot_volume}/wpa_supplicant.conf"
            data["wifi"] = os.path.exists(location)

            if data["wifi"]:
                lines = readfile(location).splitlines()

                for line in lines:
                    for tag in ["ssid", "wifipassword", "psk"]:
                        if f"{tag} =" in line:
                            data[tag] = line.split("{tag} =")[1]

            else:
                data["wifi"] = False
                data["ssid"] = None
                data["wifipassword"] = None

        except Exception as e:

            data["wifi"] = False
            data["ssid"] = None
            data["wifipasswd"] = None

        banner("Card Check")
        print(Printer.attribute(
            data,
            order=[
                "ssh",
                "hostname",
                "ip",
                "password",
                "shadow",
                "wifi",
                "psk",
                "ssid",
                "wifipassword"
            ]
        ))

    @windows_not_supported
    def firmware(self, action="check"):
        """
        Checks or update the firmware
        :param action: the cations to be performed. It is "check" or "update"
        :type action: str
        """
        if not os_is_pi():
            Console.error("This command can only be run on a PI")
        else:
            if action == "check":
                Console.error("To be implemented")

                command = f"sudo rpi-eeprom-update"
                print(command)
                os.system(command)

                os.system ("vcgencmd bootloader_version")

                print("For more information see:")
                print()
                print("* https://www.raspberrypi.org/documentation/hardware/raspberrypi/booteeprom.md")
                print()
            elif action == "update":
                os.system("sudo rpi-eeprom-update -a")
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
        Installes parted
        @return:
        @rtype:
        """

        if os_is_linux():
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
        self.burn_sdcard(from_file, device)


    @windows_not_supported
    def info(self, print_stdout=True):
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

        if os_is_pi():
            banner("This is  Raspberry PI")
        elif os_is_mac():
            banner("This is Mac")
        elif os_is_windows():
            banner("This is a Windows COmputer")
        elif os_is_linux():
            banner("This is a Linux Computer")
        else:
            Console.error("unkown OS")
            sys.exit(1)

        if os_is_pi():
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
                        "Comment"]
            )
            )

        # devices = USB.get_devices()

        # banner("Devices found")

        # print ('\n'.join(sorted(devices)))

        details = USB.get_from_dmesg()

        if print_stdout:
            banner("SD Cards Found")
            print(Printer.write(details,
                                order=[  # "name",
                                    "dev",
                                    # "device",
                                    # "bus",
                                    # "sg",
                                    "active",
                                    "info",
                                    "readable",
                                    "formatted",
                                    "empty",
                                    "size",
                                    "direct-access",
                                    "removable",
                                    "writeable"],
                                header=[  # "Name",
                                    "Path",
                                    # "Device",
                                    # "Bus",
                                    # "Sg",
                                    "Plugged-in",
                                    "Info",
                                    "Readable",
                                    "Formatted",
                                    "Empty",
                                    "Size",
                                    "Access",
                                    "Removable",
                                    "Writeable"]))

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
                                        header=["Name", "Path", "Type", "Device", "Parameters"]))
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

    def system(self, command):
        """
        System command that uses subprocess to execute terminal commands
        Returns the stdout of the command

        TODO: check typr of return

        :param command: the command
        :type command: str
        :return: the stdout of the command
        :rtype: str
        """
        # if self.dryrun:
        #     print(command)
        # else:
        #     os.system(command)

        res = subprocess.getstatusoutput(command)
        # If exit code is not 0, warn user
        if res[0] != 0 and res[0] != 32:
            Console.warning(
                f'Warning: "{command}" did not execute properly -> {res[1]} :: exit code {res[0]}')

        return res[1]

    @windows_not_supported
    def burn_sdcard(self, tag="latest-lite", device=None, blocksize="4M"):
        """
        Burns the SD Card with an image

        :param image: Image object to use for burning
        :type image: str
        :param device: Device to burn to, e.g. /dev/sda
        :type device: str
        :param blocksize: the blocksize used when writing, default 4M
        :type blocksize: str
        """

        Console.info("Burning...")
        image = Image().find(tag=tag)

        if image is None:
            Console.error("No matching image found.")
            return ""
        elif len(image) > 1:
            Console.error("Too manay images found")
            print(Printer.write(image,
                                order=["tag", "version"],
                                header=["Tag", "Version"]))
            return ""

        image = image[0]

        image_path = Image().directory + "/" + Image.get_name(image["url"]) + ".img"

        if os_is_pi():

            command = f"sudo dd bs={blocksize} if={image_path} of={device}"

            result = subprocess.getoutput(command)

            if "failed to open" in result:
                Console.error("The image could not be found")
                sys.exit(1)
        elif os_is_linux():

            print(image_path)
            print(device)
            print(blocksize)
            if device is None:
                # or device == "none":
                Console.error("Please specify a device")

            # find device

            command = f"dd if={image_path} |" \
                      f" pv -w 80 |" \
                      f" sudo dd of={device} bs={blocksize} conv=fsync status=progress"
            print(command)
            os.system(command)

        else:
            raise NotImplementedError("Only implemented to be run on a PI")

    @windows_not_supported
    def set_hostname(self, hostname):
        """
        Sets the hostname on the sd card

        :param hostname: the hostname
        :type hostname: str
        :param mountpoint: the mountpunt of the device on which the hostanme
                           is found
        :type mountpoint: str
        """
        self.hostname = hostname
        if os_is_pi():
            card = SDCard()
        elif os_is_linux():
            card = SDCard(card_os="linux")
        else:
            raise NotImplementedError

        mountpoint = card.root_volume
        # write the new hostname to /etc/hostname
        if not self.dryrun:
            self.system(
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
            new_hostsfile_contents = ''.join(lines) + newlastline
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
        Also writes to master hosts file for easy access

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
        # router_ip statically set to default ip configured with cms bridge create. Rewrite to consider the IP of the master on iface

        if os_is_pi():
            card = SDCard()
        elif os_is_linux():
            card = SDCard(card_os="linux")
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
    # Deprecated function as dhcpcd.conf is the recommended file for configuring static network configs. Should we keep this?
    #
    # def set_static_ip2(self, ip, mountpoint, iface="eth0", mask="16"):
    #     """
    #     Sets the static ip on the sd card for the specified interface
    #     Also writes to master hosts file for easy access

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

    #     # Add static IP and hostname to master's hosts file and configure worker with static IP
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
    #                 self.system("cat /etc/resolv.conf | grep nameserver").split()[
    #                     1]  # index 0 is "nameserver" so ignore
    #             routerss = self.system(
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
        if os_is_pi():
            card = SDCard()
        elif os_is_linux():
            card = SDCard(card_os="linux")
        else:
            raise NotImplementedError

        mountpoint = card.root_volume
        self.system(f'mkdir -p {mountpoint}/home/pi/.ssh/')
        self.system(f'cp {name} {mountpoint}/home/pi/.ssh/authorized_keys')

    @windows_not_supported
    def mount(self, device=None, card_os="raspberry", host=None):
        """
        Mounts the current SD card
        """
        host = host or get_platform()
        card = SDCard(card_os=card_os,host=host)
        dmesg = USB.get_from_dmesg()

        #TODO Need a better way to itentify which sd card to use for mounting
        # instead of iterating over all of them

        if not self.dryrun:
            self.system('sudo sync')  # flush any pending/in-process writes

            for usbcard in dmesg:

                dev = device or usbcard['dev']
                print(dev)
                sd1 = f"{dev}1"
                sd2 = f"{dev}2"
                try:
                    if os.path.exists(sd1):
                        Console.ok(f"mounting {sd1} {card.boot_volume}")
                        self.system(f"sudo mkdir -p {card.boot_volume}")
                        self.system(f"sudo mount -t vfat {sd1} {card.boot_volume}")
                except Exception as e:
                    print(e)
                try:
                    if os.path.exists(sd2):
                        Console.ok(f"mounting {sd2} {card.root_volume}")
                        self.system(f"sudo mkdir -p {card.root_volume}")
                        self.system(f"sudo mount -t ext4 {sd2} {card.root_volume}")
                except Exception as e:
                    print(e)

        #Keeping in case this was needed. Worked without it in testing.
        #elif os_is_pi():
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
    def unmount(self, device=None, card_os="raspberry", host=None):
        """
        Unmounts the current SD card

        :param device: device to unmount, e.g. /dev/sda
        :type device: str
        """

        host = host or get_platform()
        card = SDCard(card_os=card_os, host=host)

        if not self.dryrun:
            self.system('sudo sync')  # flush any pending/in-process writes

            os.system(f"sudo umount {card.boot_volume}")
            time.sleep(3)
            os.system(f"sudo umount {card.root_volume}")

            time.sleep(3)

            rm = [f"sudo rmdir {card.boot_volume}",
                  f"sudo rmdir {card.root_volume}"]

            for command in rm:
                print(rm)
                os.system(command)

    @windows_not_supported
    def enable_ssh(self):
        """
        Enables ssh on next boot of sd card
        """
        if os_is_pi():
            card = SDCard(card_os="raspberry")
            command = f'sudo touch {card.boot_volume}/ssh'
            self.system(command)
        elif os_is_linux():
            card = SDCard(card_os="raspberry")
            command = f"sudo touch {card.boot_volume}/ssh"
            self.system(command)

        else:
            raise NotImplementedError

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

    # IMPROVE
    # ok osx
    @windows_not_supported
    def activate_ssh(self, public_key, debug=False, interactive=False):
        """
        Sets the public key path and copies it to the SD card

        TODO: this has bugs as we have not yet thought about debug,
              interactive, yesno yesno we can take form cloudmesh.common

        BUG: this just raise a non implementation error

        :param public_key: the public key location
        :type public_key: str
        :param debug: if set to tru debug messages will be printed
        :type debug: bool
        :param interactive: set to tru if you like interactive mode
        :type interactive: bool
        :return: True if successful
        :rtype: bool
        """

        raise NotImplementedError

        # set the keypath
        self.keypath = public_key
        if debug:
            print(self.keypath)
        if not os.path.isfile(self.keypath):
            Console.error("key does not exist", self.keypath)
            sys.exit()

        if self.dryrun:
            print("DRY RUN - skipping:")
            print("Activate ssh authorized_keys pkey:{}".format(public_key))
            return
        elif interactive:
            if not yn_choice("About to write ssh config. Please confirm:"):
                return

        # activate ssh by creating an empty ssh file in the boot drive
        pathlib.Path(self.filename("/ssh")).touch()
        # Write the content of the ssh rsa to the authorized_keys file
        key = pathlib.Path(public_key).read_text()
        ssh_dir = self.filename("/home/pi/.ssh")
        print(ssh_dir)
        if not os.path.isdir(ssh_dir):
            os.makedirs(ssh_dir)
        auth_keys = ssh_dir / "authorized_keys"
        auth_keys.write_text(key)

        # We need to fix the permissions on the .ssh folder but it is hard to
        # get this working from a host OS because the host OS must have a user
        # and group with the same pid and gid as the raspberry pi OS. On the PI
        # the pi uid and gid are both 1000.

        # All of the following do not work on OS X:
        # execute("chown 1000:1000 {ssh_dir}".format(ssh_dir=ssh_dir))
        # shutil.chown(ssh_dir, user=1000, group=1000)
        # shutil.chown(ssh_dir, user=1000, group=1000)
        # execute("sudo chown 1000:1000 {ssh_dir}".format(ssh_dir=ssh_dir))

        # Changing the modification attributes does work, but we can just handle
        # this the same way as the previous chown issue for consistency.
        # os.chmod(ssh_dir, 0o700)
        # os.chmod(auth_keys, 0o600)

        # /etc/rc.local runs at boot with root permissions - since the file
        # already exists modifying it shouldn't change ownership or permissions
        # so it should run correctly. One lingering question is: should we clean
        # this up later?

        new_lines = textwrap.dedent('''
                    # FIX298-START: Fix permissions for .ssh directory 
                    if [ -d "/home/pi/.ssh" ]; then
                        chown pi:pi /home/pi/.ssh
                        chmod 700 /home/pi/.ssh
                        if [ -f "/home/pi/.ssh/authorized_keys" ]; then
                            chown pi:pi /home/pi/.ssh/authorized_keys
                            chmod 600 /home/pi/.ssh/authorized_keys
                        fi
                    fi
                    # FIX298-END
                    ''')
        rc_local = self.filename("/etc/rc.local")
        new_rc_local = ""
        already_updated = False
        with rc_local.open() as f:
            for line in f:
                if "FIX298" in line:
                    already_updated = True
                    break
                if line == "exit 0\n":
                    new_rc_local += new_lines
                    new_rc_local += line
                else:
                    new_rc_local += line
        if not already_updated:
            with rc_local.open("w") as f:
                f.write(new_rc_local)
        self.disable_password_ssh()

    @windows_not_supported
    def configure_wifi(self,
                       ssid,
                       psk=None,
                       interactive=False):
        """
        Sets the wifi. Only works for psk based wifi

        :param ssid: the ssid
        :type ssid: str
        :param psk: the psk
        :type psk: str
        :param interactive: true if you like to run it interactively
        :type interactive: bool
        """
        if psk is not None:
            wifi = textwrap.dedent("""\
                    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
                    update_config=1 
                    country=US

                    network={{
                            ssid=\"{network}\"
                            psk=\"{pwd}\"
                            key_mgmt=WPA-PSK
                    }}""".format(network=ssid, pwd=psk))
        else:
            wifi = textwrap.dedent("""\
                    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev 
                    update_config=1 
                    country=US

                    network={{
                            ssid=\"{network}\"
                            key_mgmt=NONE
                    }}""".format(network=ssid))

        # Per fix provided by Gregor, we use this path to get around rfkill block on boot
        card = SDCard(card_os=card_os, host=host)
        path = f"{card.boot_volume}/wpa_supplicant.conf"
        if self.dryrun:
            print("DRY RUN - skipping:")
            print("Writing wifi ssid:{} psk:{} to {}".format(ssid,
                                                             psk, path))
            return

        # with open(path, 'w') as f:
        #     f.write(wifi)
        sudo_writefile(path, wifi)

    # TODO
    @windows_not_supported
    def format_device(self, device='dev/sdX', hostname=None, title="UNTITLED"):
        """
        Formats device with one FAT32 partition

        WARNING: make sure you have the right device, this comamnd could
                 potentially erase your OS

        :param device: The defice on which we format
        :type device: str
        :param hostname: the hostname
        :type hostname: str
        """

        if os_is_linux() or os_is_pi():

            banner("format {device}")

            script = f"""
                sudo eject -t {device}
                sudo parted {device} --script -- mklabel msdos
                sudo parted {device} --script -- mkpart primary fat32 1MiB 100%
                sudo mkfs.vfat -n {title} -F32 {device}1
                sudo parted {device} --script print""".strip().splitlines()
            for line in script:
                print(line)
                os.system(line)

            Console.ok("Formatted SD Card")

        else:
            raise NotImplementedError("Not implemented for this OS")

    @windows_not_supported
    def load_device(self, device='dev/sdX'):
        """
        Loads the USB device via trayload

        :param device: The defice on which we format
        :type device: str
        :param hostname: the hostname
        :type hostname: str
        """
        if os_is_pi():
            Console.error("Not yet implemented")

        elif os_is_linux():

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
    def system(self, command):
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
                 fromatting=True,
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
        :param fromatting:
        :type fromatting:
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
        burn_all = yn_choice("Burn non-empty devices too?")

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
                      ip, key, password, ssid, psk, fromatting, tag)

            count += 1
            Console.info(f'Burned card {count}')
            self.system('tput bel')  # ring the terminal bell to notify user
            if i < len(hostnames) - 1:
                if (i + 1) != ((i + 1) % len(keys)):
                    choice = input(
                        f"Slot {keys[(i + 1) % len(keys)]} "
                        "needs to be reused. Do you wish to continue? [y/n] ")
                    while (choice != 'y') and (choice != 'n'):
                        choice = input("Please use [y/n] ")
                    if choice == 'n':
                        break
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
             fromatting=True,
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
        :param fromatting:
        :type fromatting:
        :return:
        :rtype:
        """
        #TODO
        card = SDCard()
        boot_volume = card.boot_volume
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

        if fromatting:
            burner.format_device(device=device, hostname=hostname)

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

        burner.unmount(device)
        # for some reason, need to do unmount twice for it to work properly
        # burner.unmount(device)
        time.sleep(2)
        StopWatch.stop(f"create {device} {hostname}")
        StopWatch.status(f"create {device} {hostname}", True)
