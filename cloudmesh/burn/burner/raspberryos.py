import os
import random
import re
import string
import subprocess
import sys
import textwrap
import time
from getpass import getpass

from cloudmesh.bridge.Bridge import Bridge
from cloudmesh.burn.image import Image
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_pi
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.burn.wifi.provider import Wifi
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Host import Host
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Shell import windows_not_supported
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.security import generate_strong_pass
from cloudmesh.common.sudo import Sudo
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import yn_choice
from cloudmesh.inventory.inventory import Inventory

if not os_is_windows():
    import crypt
else:
    import bcrypt as crypt


# noinspection PyPep8
class Burner(object):

    def __init__(self):
        """
        Initializes the burner
        """
        self.hostname = None
        self.keypath = None
        self.hostnames = None

    # noinspection PyBroadException
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

        card = SDCard(host_os=host)
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

    def mac(self, hostnames=None):
        """
        Sets the hostname for which we probe the MAC addresses

        :param hostnames: the hostnames
        :type hostnames: str
        """
        self.hostnames = hostnames

        print(hostnames)
        Console.error("Not yet implemented")
        return ""

    @windows_not_supported
    def set_locale(self, locale="en_US.UTF-8"):

        lang = textwrap.dedent(f'''
        LANG={locale}
        LC_ALL={locale}
        LANGUAGE={locale}
        #
        ''').strip()

        card = SDCard()

        # Write it 3 times as sometimes it does not work
        for i in range(0, 3):
            SDCard.writefile(f"{card.root_volume}/etc/default/locale", lang)

        locale_gen = SDCard.readfile(f"{card.root_volume}/etc/locale.gen",
                                     split=True, decode=True)
        for i in range(0, len(locale_gen)):
            if not locale_gen[i].startswith("#"):
                locale_gen[i] = "# " + locale_gen[i]
            if locale in locale_gen[i]:
                locale_gen[i] = locale_gen[i].replace("# ", "")
        locale_gen = "\n".join(locale_gen) + "\n"

        for i in range(0, 3):
            SDCard.writefile(f"{card.root_volume}/etc/locale.gen", locale_gen)

    def set_cmdline(self, cmdline):
        card = SDCard()
        filename = f'{card.boot_volume}/cmdline.txt'
        content = Sudo.readfile(filename=filename, split=False, decode=True)
        content = content.rstrip() + " " + cmdline
        SDCard.writefile(filename=f'{card.boot_volume}/cmdline.txt',
                         content=content)

    @windows_not_supported
    def set_hostname(self, hostname):
        """
        Sets the hostname on the sd card

        :param hostname: the hostname
        :type hostname: str
        """

        # On macOS we have
        # 644 -rw-r--r--  1 user  group  /Volumes/rootfs/etc/hostname

        # od -c  /Volumes/rootfs/etc/hostname
        # 0000000    r   a   s   p   b   e   r   r   y   p   i  \n
        # 0000014

        self.hostname = hostname
        card = SDCard()

        name = hostname.strip()

        # Write it 3 times as sometimes it does not work
        for i in range(0, 3):
            time.sleep(0.5)
            SDCard.writefile(f"{card.root_volume}/etc/hostname", name)

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new

        hosts = textwrap.dedent(f"""
        127.0.0.1  localhost
        ::1        localhost ip6-localhost ip6-loopback
        ff02::1    ip6-allnodes
        ff02::2    ip6-allrouters
        #
        127.0.1.1  {hostname}
        #
        """).strip()

        print(f'Writing: {card.root_volume}/etc/hosts')
        print(hosts)
        print()

        SDCard.writefile(f'{card.root_volume}/etc/hosts', hosts)

    def add_to_hosts(self, ip=None):
        hosts = SDCard.readfile('/etc/hosts', split=True, decode=True)

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

        SDCard.writefile('/etc/hosts', config + "\n")

    def write_cluster_hosts(self, cluster_hosts=None):
        card = SDCard()
        hosts = SDCard.readfile(f'{card.root_volume}/etc/hosts', split=False, decode=True)
        hosts = hosts + '\n'
        for ip, hostname in cluster_hosts:
            hosts = hosts + f"{ip}\t{hostname}\n"
        hosts = hosts + "#\n"
        SDCard.writefile(f'{card.root_volume}/etc/hosts', hosts)

    @windows_not_supported
    def set_static_ip(self,
                      ip=None,
                      iface="eth0",
                      mask="24",
                      router_ip="10.1.1.1",
                      write_local_hosts=True):
        """
        Sets the static ip on the sd card for the specified interface
        Also writes to manager hosts file for easy access

        :param ip: ips address
        :type ip: str
        :param iface: the network Interface
        :type iface: str
        :param mask: the subnet Mask
        :type mask: str
        :param router_ip:
        :type router_ip: str
        :param write_local_hosts:
        :type write_local_hosts: bool
        :return:
        :rtype:
        """
        # TODO:
        # router_ip statically set to default ip configured with cms bridge
        # create. Rewrite to consider the IP of the manager on iface

        card = SDCard()

        mountpoint = card.root_volume
        if self.hostname is not None and write_local_hosts:
            self.add_to_hosts(ip)

        iface = f'interface {iface}'
        static_ip = f'static ip_address={ip}/{mask}'
        static_routers = f'static routers={router_ip}'

        curr_config = SDCard.readfile(f'{mountpoint}/etc/dhcpcd.conf', decode=True, split=True)
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
            if router_ip:
                curr_config.append(static_routers)
            curr_config.append('\n')
            # curr_config.append('nolink\n')

        SDCard.writefile(f'{mountpoint}/etc/dhcpcd.conf', '\n'.join(curr_config))

    @windows_not_supported
    def keyboard(self, country="US"):
        """
        Sets the country on the SDCard

        :param country: two letter country code
        :type country: str
        :return: true if set
        :rtype: bool
        """

        # cat /etc/default/keyboard
        # # KEYBOARD CONFIGURATION FILE
        #
        # # Consult the keyboard(5) manual page.
        #
        # XKBMODEL="pc105"
        # XKBLAYOUT=us
        # XKBVARIANT=""
        # XKBOPTIONS=""
        #
        # BACKSPACE="guess"

        card = SDCard()

        layout = f"{card.root_volume}/etc/default/keyboard"

        content = SDCard.readfile(layout, decode=True, split=True)

        country = country.lower()
        found = False
        for i in range(0, len(content)):
            if content[i].strip().startswith("XKBLAYOUT"):
                content[i] = f"XKBLAYOUT={country}"
                found = True
                break

        content = "\n".join(content)
        print(content)
        SDCard.writefile(layout, content)
        Sudo.execute("sync")
        return found

    @windows_not_supported
    def set_key(self, key_file=None):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card

        :param key_file: key_file of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        :type key_file: str
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys

        card = SDCard()

        location = path_expand(key_file)

        SDCard.execute(f'mkdir -p {card.root_volume}/home/pi/.ssh/')
        SDCard.execute(f'cp {location} {card.root_volume}/home/pi/.ssh/authorized_keys')
        # cleanup
        if os.path.exists(f"{card.root_volume}/home/pi/.ssh/._authorized_keys"):
            SDCard.execute(f"rm -f {card.root_volume}/home/pi/.ssh/._authorized_keys")

    def write_fix(self, locale="en_US.UTF-8"):
        """
        Not yet integrated:
            /etc/systemd/system/sshd.service
            /etc/passwd
            /etc/ssh/sshd_config
        """
        timezone = Shell.timezone()
        script = textwrap.dedent(f"""
            #! /usr/bin/env python
            # file, owner, group, permissions
            import os
            if not os.path.exists("/boot/fixed"):
                files = [
                    ["/etc/default/keyboard", 0, 0, 0o644],
                    ["/boot/fix_permissions.py", 0, 0, 0o777],
                    ["/boot/ssh", 0, 0, 0o777],
                    ["/boot/wpa_supplicant.conf", 0, 0, 0o600],
                    ["/etc/hosts", 0, 0, 0o644],
                    ["/etc/default/locale", 0, 0, 0o644],
                    ["/etc/environment", 0, 0, 0o644],
                    ["/etc/locale.conf", 0, 0, 0o644],
                    ["/etc/passwd", 0, 0, 0o644],
                    ["/etc/dhcpcd.conf", 0, 109, 0o664],
                    ["/etc/hostname", 0, 0, 0o644],
                    ["/etc/ssh/sshd_config", 0, 0, 0o644],
                    ["/etc/shadow", 0, 42, 0o640],
                    ["/etc/rc.local", 0, 0, 0o751],
                    ["/home/pi/.ssh", 1000, 1000, 0o700],
                    ["/home/pi/.ssh/authorized_keys", 1000, 1000, 0o644],
                    ["/home/pi/.ssh/id_rsa", 1000, 1000, 0o600],
                    ["/home/pi/.ssh/id_rsa.pub", 1000, 1000, 0o644]
                ]
                for name, uid, guid, permission in files:
                    if os.path.exists(name):
                        os.chown(name, uid, guid)
                        os.chmod(name, permission)
                os.system("locale-gen {locale}")
                name = "/boot/fixed"
                os.system("touch /boot/fixed")
                os.chown("/boot/fixed", 0, 0)
                os.chmod("/boot/fixed", 0o644)
                os.system("sudo timedatectl set-timezone {timezone}")
                os.system("sudo sync")
                # os.system("sleep 90")
                # os.system("sudo reboot")
                #
        """)

        card = SDCard()
        fix = "/boot/fix_permissions.py"
        fix_on_sdcard = f"{card.boot_volume}/fix_permissions.py"
        SDCard.writefile(fix_on_sdcard, script)

        rc_local = f"{card.root_volume}/etc/rc.local"
        content = readfile(rc_local)
        if fix in content:
            return
        else:
            content = content.replace("exit 0", f"sudo python {fix}")
            content = content + "\n" + "exit 0\n"
            SDCard.writefile(rc_local, content)

    @windows_not_supported
    def enable_ssh(self):
        """
        Enables ssh on next boot of sd card
        """
        host = get_platform()

        if host in ['raspberry', "linux"]:
            sudo = True
        else:
            sudo = False

        card = SDCard(card_os="raspberry", host_os=host)
        if sudo:
            Sudo.password()
            command = f'sudo touch {card.boot_volume}/ssh'
        else:
            command = f'touch {card.boot_volume}/ssh'

        os.system(command)

        return ""

    # IMPROVE

    # TODO: docstring
    @windows_not_supported
    def disable_password_ssh(self):

        # sshd_config = self.filename("/etc/ssh/sshd_config")
        card = SDCard()
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
        f = SDCard.readfile(sshd_config, decode=True, split=True)

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
            # as we do it on osx, we need to identify if this is still needed
            #
            # self.truncate_file(sshd_config)
            # with open(sshd_config, "w") as f:
            #     f.write(new_sshd_config)

            SDCard.writefile(sshd_config, new_sshd_config)

    @windows_not_supported
    def configure_wifi(self,
                       ssid=None,
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

        card = SDCard(card_os=card_os, host_os=host)
        path = f"{card.boot_volume}/wpa_supplicant.conf"

        card_os = "raspberry"  # needs to become a parameter based on tag

        # noinspection PyPep8Naming
        WifiClass = Wifi(card_os=card_os)

        if card_os == "raspberry":
            if psk:
                if os_is_mac():
                    WifiClass.set(ssid=ssid, password=psk, country=country, location=path)
                else:
                    WifiClass.set(ssid=ssid, password=psk, country=country, location=path, sudo=True)
            else:
                if os_is_mac():
                    WifiClass.set(ssid=ssid, psk=False, country=country, location=path)
                else:
                    WifiClass.set(ssid=ssid, psk=False, country=country, location=path, sudo=True)
        else:
            if os_is_mac():
                WifiClass.set(ssid=ssid, password=psk, country=country, location=path)
            else:
                WifiClass.set(ssid=ssid, password=psk, country=country, location=path, sudo=True)

        return ""

    # This is to prevent desktop access of th pie (directly plugging monitor, keyboard, mouse into pi, etc.)
    #
    # Currently, ssh login is only possible with an authorized key. (No passwords)
    # Plugging pi directly into desktop, however, will still prompt for a user and password.
    # I can't figure out how to disable it

    @windows_not_supported
    def disable_terminal_login(self, mountpoint=None, password=None):
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

        info = SDCard.readfile(f'{mountpoint}/etc/passwd', split=True, decode=True)

        for i in range(len(info)):
            inf = info[i].split(":")
            if inf[0] == 'pi':
                inf[1] = 'x'
                info[i] = ':'.join(inf)

        content = '\n'.join(info)

        # with open(f'{mountpoint}/etc/passwd', 'w') as f:
        #     f.writelines(info)

        SDCard.writefile(f'{mountpoint}/etc/passwd', content)

        # Add it to shadow file
        # with open(f'{mountpoint}/etc/shadow', 'r') as f:
        #     data = [l for l in f.readlines()]

        data = SDCard.readfile(f'{mountpoint}/etc/shadow', decode=True, split=True)

        content = ""
        for i in range(len(data)):
            dat = data[i].split(":")
            if dat[0] == 'pi':
                dat[1] = pswd
                data[i] = ':'.join(dat)

        content = '\n'.join(data)

        SDCard.writefile(f'{mountpoint}/etc/shadow', content)

    def generate_key(self, hostname=None):
        card = SDCard()
        # TODO investigate what happens if not run as UID 1000 (e.g. first user)

        cmd = f'mkdir -p {card.root_volume}/home/pi/.ssh/'
        os.system(cmd)

        cmd = f'ssh-keygen -q -N "" -C "pi@{hostname}" -f {card.root_volume}/home/pi/.ssh/id_rsa'
        os.system(cmd)

    @staticmethod
    def store_public_key():
        card = SDCard()
        cmd = f'cp {card.root_volume}/home/pi/.ssh/id_rsa.pub ~/.cloudmesh/cmburn/'
        os.system(cmd)

    @staticmethod
    def remove_public_key():
        cmd = 'rm -f ~/.cloudmesh/cmburn/id_rsa.pub'
        os.system(cmd)

    @staticmethod
    def get_tag(worker=True, card_os="raspberry"):
        tag = None
        if "raspberry" in card_os and worker:
            tag = "latest-lite"
        elif "raspberry" in card_os and not worker:
            tag = "latest-full"
        elif "ubuntu" in card_os and worker:
            tag = "ubuntu-20.04.2-64-bit"
        elif "ubuntu" in card_os and not worker:
            tag = "ubuntu-desktop"
        else:
            Console.error("For now only raspberry and ubuntu are supported")
        return tag

    def cluster(self, arguments=None):

        # is true when
        #
        # cms burn cluster --hostname=red,red00[1-2]
        #                  --device=/dev/sdb
        #                  --ip=10.1.1.[1-3]
        #                  --ssid=myssid
        #                  --wifipassword=mypass
        #

        Sudo.password()
        yes = arguments.yes
        arguments.os = arguments.os or "raspberry"

        if os_is_windows():
            Console.error("Only supported on Pi and Linux. On Mac you will "
                          "need to have ext4 write access.")
            return ""

        hostnames = Parameter.expand(arguments.hostname)
        manager, workers = Host.get_hostnames(hostnames)
        if arguments.burning is None:
            burning = hostnames
        else:
            burning = Parameter.expand(arguments.burning)

        if not (arguments.cluster and  # noqa: W504
                arguments.device and  # noqa: W504
                arguments.hostname):  # noqa: W504
            Console.error("Parameters not complete")
            return ""

        passwd = None
        if arguments.set_passwd:
            passwd = getpass("Host Password: ")
        elif "PASSWD" in os.environ:
            passwd = os.environ["PASSWD"]
        else:
            passwd = generate_strong_pass()

        if manager is not None and arguments.ssid is None:
            Console.error("Please set ssid")
            return ""

        if manager is not None and \
            (arguments.wifipassword is None
             or arguments.wifipassword.lower() in ['input', "none", ""]):  # noqa: W503
            print()
            arguments.wifipassword = getpass("Wifi Password: ")

        if workers is None:
            n = 1
        else:
            n = len(workers) + 1
        if arguments.ip is None:
            ips = Parameter.expand(f"10.1.1.[1-{n}]")
        else:
            ips = Parameter.expand(arguments.ip)

        cluster_hosts = tuple(zip(ips, hostnames))

        key = path_expand("~/.ssh/id_rsa.pub")

        banner("Parameters", figlet=True)

        print("Burning:      ", burning)
        print("Manager:      ", manager)
        print("Workers:      ", workers)
        print("IPS:          ", ips)
        print("Device:       ", arguments.device)
        print("SSID:         ", arguments.ssid)
        print("Wifi Password:", "********")
        print("Key:          ", key)
        print("Blocksize:    ", arguments.bs)
        print("OS:           ", arguments.os)
        print("Imaged:       ", arguments.imaged)
        print("Host Password:", "********")

        if not (yes or yn_choice('\nWould you like to continue?')):
            Console.error("Aborting ...")
            return ""

        banner("Download Images", figlet=True)

        StopWatch.start("download image")

        result = Image.create_version_cache()
        if result is None:
            result = Image.create_version_cache(refresh=True)

        image = Image()
        image.read_version_cache()

        if "raspberry" in arguments.os:
            if workers is not None:
                image.fetch(tag=["latest-lite"])
            if manager is not None:
                image.fetch(tag=["latest-full"])
        elif "ubuntu" in arguments.os:
            if workers is not None:
                image.fetch(tag=["ubuntu-20.04.2-64-bit"])
            if manager is not None:
                image.fetch(tag=["ubuntu-desktop"])
        else:
            Console.error("For now only raspberry and ubuntu are supported")
        StopWatch.stop("download image")
        StopWatch.status("download image", True)

        multi = MultiBurner()

        if manager is not None and manager in burning:
            banner("Burn the Manager", figlet=True)

            Console.info(f"Please insert the SD Card: {manager}")

            Console.info(f"Preparing to burn the manager: {manager}")
            if not yn_choice('\nWould you like to continue?'):
                Console.error("Aborting ...")
                return ""

            multi.burn(device=arguments.device,
                       blocksize=arguments.bs,
                       progress=True,
                       hostname=manager,
                       ip=ips[0],
                       key=key,
                       password=passwd,
                       ssid=arguments.ssid,
                       psk=arguments.wifipassword,
                       formatting=not arguments.imaged,
                       imaging=not arguments.imaged,
                       tag=Burner.get_tag(card_os=arguments.os, worker=False),
                       router=None,
                       generate_key=True,
                       store_key=True,
                       write_local_hosts=False,
                       cluster_hosts=cluster_hosts,
                       yes=yes)

            Console.info(f"Completed manager: {manager}")

        if workers is not None:
            banner("Burn the Workers", figlet=True)

            Console.info(f"Preparing to burn the workers: {workers}")
            for worker, ip in tuple(zip(workers, ips[1:])):
                if worker not in burning:
                    continue

                banner(f"Worker {worker}", figlet=True)

                print()
                Console.info(f"Please insert SD Card for worker {worker}")
                print()

                if not yn_choice("Say Y once you inserted it. Press no to terminate ..."):
                    return ""

                multi.burn(device=arguments.device,
                           blocksize=arguments.bs,
                           progress=True,
                           hostname=worker,
                           ip=ip,
                           key='~/.cloudmesh/cmburn/id_rsa.pub',
                           password=passwd,
                           ssid=None,
                           psk=None,
                           formatting=not arguments.imaged,
                           imaging=not arguments.imaged,
                           tag=Burner.get_tag(card_os=arguments.os, worker=True),
                           router=ips[0],
                           generate_key=False,
                           store_key=False,
                           write_local_hosts=False,
                           cluster_hosts=cluster_hosts,
                           yes=yes)

            Console.info(f"Completed workers: {workers}")
            Console.info("Cluster burn is complete.")
            # Burner.remove_public_key()
            # TODO remove public key on GUI close or single cluster cmd complete

        banner("Benchmark", figlet=True)

        StopWatch.status("load", True)
        StopWatch.status("command", True)

        Benchmark.print(sysinfo=True, csv=True, tag="local")
        banner("Done", figlet=True)
        return ""


class MultiBurner(object):
    """
    This class uses a single or multicard burner to burn SD Cards. It detects
    how many SD Cards are there and uses them. We assume no other USB devices
    are plugged in other than a keyboard or a mouse.

    """

    # System command that uses subprocess to execute terminal commands
    # Returns the stdout of the command
    def system_exec(self, command=None):
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
                 burning=None,
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
                 imaging=True,
                 tag='latest-lite',
                 locale="en_US.UTF-8",
                 yes=False):
        """
        TODO: provide documentation
        :param burning:
        :type burning:
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
        :param tag:
        :type tag:
        :param locale:
        :type locale:
        :param formatting:
        :type formatting:
        :param imaging:
        :type imaging:
        :param yes:
        :type yes:
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
        card = SDCard()
        info_statuses = card.info()

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

        # TODO This does nothing relevant
        # ask if this is ok to burn otherwise
        # burn_all = yn_choice("Format the card before burning?")

        # # if no burn all of them for which we have status "empty card"
        # if not burn_all:
        #     # delete from devices dict any non-empty devices
        #     devices_to_delete = []
        #     for device in devices.keys():
        #         if devices[device]:
        #             # can't delete while iterating
        #             devices_to_delete.append(device)
        #     for device in devices_to_delete:
        #         del devices[device]

        print("Burning these devices:")
        print(' '.join(devices.keys()))

        if burning is None:
            burning = hostnames

        keys = list(devices.keys())
        count = 0
        for i in range(len(hostnames)):
            # for device, status in devices.items():
            # We might be using one device slot to burn multiple cards
            device = keys[i % len(keys)]
            # status = devices[device]
            hostname = hostnames[i]
            ip = None if not ips else ips[i]

            self.burn(image=image,
                      device=device,
                      blocksize=blocksize,
                      progress=progress,
                      hostname=hostname,
                      ip=ip,
                      key=key,
                      password=password,
                      ssid=ssid,
                      psk=psk,
                      formatting=formatting,
                      imaging=imaging,
                      tag=tag,
                      locale=locale,
                      yes=yes)

            count += 1
            Console.info(f'Burned card {count}')
            print()
            Console.info('Please remove the card')
            print()
            os.system('tput bel')  # ring the terminal bell to notify user
            if i < len(hostnames) - 1:
                if (i + 1) != ((i + 1) % len(keys)):
                    slot = keys[(i + 1) % len(keys)]
                    print()
                    print(f"Please remove any card from slot {slot} and insert a new one.")
                    if yn_choice("Is the card inserted and do you wish to continue?"):
                        pass
                    else:
                        return ""

                print('Burning next card...')
                print()

        Console.info(f"You burned {count} SD Cards")
        Console.ok("Done :)")

    # noinspection PyBroadException
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
             imaging=True,
             tag='latest-lite',
             router="10.1.1.1",
             generate_key=False,
             store_key=False,
             write_local_hosts=True,
             cluster_hosts=None,
             keyboard="us",
             locale="en_US.UTF-8",
             yes=False):
        """
        Burns the image on the specific device

        TODO: provide documentation

        :param image:
        :type image:
        :param device:
        :type device:
        :param blocksize:
        :type blocksize:
        :type blocksize:
        :param progress:
        :type progress:
        :param hostname: The hostnames to burn
        :type hostname: str
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
        :param yes:
        :type yes:
        :param imaging:
        :type imaging:
        :param tag:
        :type tag:
        :param locale:
        :type locale:
        :param keyboard:
        :type keyboard:
        :param router:
        :type router:
        :param cluster_hosts:
        :type cluster_hosts:
        :param generate_key:
        :type generate_key:
        :param store_key:
        :type store_key:
        :param write_local_hosts:
        :type write_local_hosts:
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

        # don't do the input() after burning the last card
        # use a counter to check this

        counter = 0
        burner = Burner()

        print("counter", counter)
        StopWatch.start(f"create {device} {hostname}")

        card = SDCard()
        if formatting:
            StopWatch.start(f"format {device} {hostname}")
            success = card.format_device(device=device,
                                         unmount=True,
                                         yes=yes)
            StopWatch.stop(f"format {device} {hostname}")

            if not success:
                Console.warning("Skipping card due to failed format. "
                                "Continuing with next hostname.")
                return
            StopWatch.status(f"format {device} {hostname}", True)

        if os_is_linux() or os_is_pi():
            card.unmount(device=device)  # can not fully eject before burn on pi or linux
        elif os_is_mac():
            card.unmount(device=device)

        if imaging:
            StopWatch.start(f"write image {device} {hostname}")
            card.burn_sdcard(tag=tag,
                             device=device,
                             blocksize=blocksize,
                             name=hostname,
                             yes=yes)
            StopWatch.stop(f"write image {device} {hostname}")
            StopWatch.status(f"write image {device} {hostname}", True)

        if os_is_linux():
            # full unmount is needed before mount on linux
            # added here for --imaged option to work
            card.unmount(device=device, full=True)

        Sudo.password()
        StopWatch.start(f"write host data {device} {hostname}")
        card.mount(device=device)
        Sudo.execute("sync")

        burner.keyboard(country=keyboard)
        burner.set_hostname(hostname)
        burner.set_locale(locale=locale)
        if generate_key:
            burner.generate_key(hostname)
        if store_key:
            Burner.store_public_key()
        burner.disable_terminal_login(root_volume, password)
        if ssid:
            Console.warning("In the future, try to interface with the workers via "
                            "ethernet/switch rather than WiFi")
            burner.configure_wifi(ssid, psk)
        burner.enable_ssh()
        burner.disable_password_ssh()
        burner.set_key(key)
        if ip:
            # TODO
            # interface = "wlan0" if ssid is not None else "eth0"
            #
            # we can't rely on ssid to determine which interface to static set.
            # for burning a cluster we want to static set the eth on manager
            # and enable wifi. We will need to add options --wifi_ip
            # --wifi_router
            #
            interface = 'eth0'
            burner.set_static_ip(ip, iface=interface, router_ip=router,
                                 write_local_hosts=write_local_hosts)
            if not write_local_hosts:
                burner.write_cluster_hosts(cluster_hosts)
        burner.write_fix()
        try:
            os.system(f"sudo rm -f {card.root_volume}/etc/xdg/autostart/piwiz.desktop")
        except:  # noqa: E722
            Console.error("Gui wizzard not found at "
                          f"{card.root_volume}/etc/xdg/autostart/piwiz.desktop")

        card.unmount(device=device, full=True)
        StopWatch.stop(f"write host data {device} {hostname}")
        StopWatch.status(f"write host data {device} {hostname}", True)

        time.sleep(2)
        StopWatch.stop(f"create {device} {hostname}")
        StopWatch.status(f"create {device} {hostname}", True)

    def burn_inventory(self,
                       inventory=None,
                       name=None,
                       device=None,
                       locale='en_US.UTF-8',
                       yes=False,
                       passwd=None):
        banner("Burning Inventory", figlet=True)
        i = Inventory(inventory)
        i.print()

        name = Parameter.expand(name)
        manager, workers = Host.get_hostnames(name)

        # name formatted as manager,worker
        # if ',' in name:
        #    manager, worker = name.split(',')
        #    workers = Parameter.expand(worker)
        # else:

        devices = Parameter.expand(device)

        # Warn user if they are burning non-empty devices
        card = SDCard()
        info_statuses = card.info(print_stdout=False)

        if os_is_mac():
            Console.warning(" ignoring device check")
            pass
        else:
            try:
                empty_statuses = {}
                for device in devices:
                    empty_statuses[device] = info_statuses[device]['empty']
            except KeyError:
                Console.error("Device specified not found by cms burn info. "
                              "Did you specify the correct path? Is the card properly inserted?")
                return

            for dev, empty_status in empty_statuses.items():
                if not empty_status:
                    if not (yes or yn_choice(f"Device {dev} is not empty. Do you wish to continue?")):
                        Console.error("Terminating")
                        return

        if manager is not None:
            manager_search_results = i.find(host=manager)
            if len(manager_search_results) == 0:
                Console.error(f"Could not find {manager} in inventory {inventory}. "
                              "Please correct before continuing.")
                return
            elif len(manager_search_results) > 1:
                Console.error(
                    f"Found duplicate {manager} configurations in inventory {inventory}. "
                    "Please correct before contuing")
                return

        if manager is not None:
            manager_config = {
                "hostname": manager,
                "tag": i.get(manager, "tag"),
                "ip": i.get(manager, "ip"),
                "services": i.get(manager, "services"),
                "keyfile": i.get(manager, "keyfile"),
                "dns": ','.join(i.get(manager, "dns"))
            }
        else:
            manager_config = None

        worker_configs = []
        if workers:
            for worker in workers:
                worker_config = {
                    "hostname": worker,
                    "tag": i.get(worker, "tag"),
                    "ip": i.get(worker, "ip"),
                    "services": i.get(worker, "services"),
                    "keyfile": i.get(worker, "keyfile"),
                    "router": i.get(worker, "router")
                }
                worker_configs.append(worker_config)

        _, system_hostname = subprocess.getstatusoutput("cat /etc/hostname")

        banner("Retrieving Images", figlet=True)
        # Get Images if not already downloaded
        result = Image.create_version_cache()
        if result is None:
            result = Image.create_version_cache(refresh=True)

        image = Image()
        image.read_version_cache()

        if manager is not None and system_hostname != manager_config["hostname"]:
            image.fetch(tag=manager_config["tag"])
        if workers is not None:
            image.fetch(tag=worker_configs[0]["tag"])

        # Set up this pi as a bridge if the hostname is the same
        # as the manager and if the user wishes
        if manager is not None:
            if system_hostname == manager_config["hostname"]:
                if yes or yn_choice("Manager hostname is the same as this system's "
                                    "hostname. Is this intended?"):
                    if yes or yn_choice("Do you wish to configure this system as a WiFi "
                                        "bridge? A restart is required after this "
                                        "command terminates"):
                        Bridge.create(managerIP=manager_config['ip'],
                                      priv_interface='eth0',
                                      ext_interface='wlan0',
                                      dns=manager_config["dns"])
                else:
                    Console.error("Terminating")
                    return
            else:
                self.burn(
                    device=device,
                    hostname=manager_config["hostname"],
                    ip=manager_config["ip"],
                    key=manager_config["keyfile"],
                    tag=manager_config["tag"],
                    password=passwd or generate_strong_pass(),
                    locale=locale)
                print("Safe to remove manager card.")
                if not workers or not yn_choice(f"Insert new card into slot {device}."
                                                " Is it inserted and do you wish to continue?"):
                    Console.ok("Done.")

        # The code below was taken from self.multi_burn
        # It would be nice to move this functionality of cycling over
        # sd card slots into a nice one liner function
        count = 0
        for i in range(len(worker_configs)):

            device = devices[i % len(devices)]
            worker_config = worker_configs[i]
            self.burn(
                device=device,
                hostname=worker_config["hostname"],
                ip=worker_config["ip"],
                key=worker_config["keyfile"],
                tag=worker_config["tag"],
                password=passwd or generate_strong_pass(),
                router=worker_config["router"] or (manager_config["ip"] if manager_config else None),
                locale=locale)

            count += 1
            Console.info(f'Burned card {count}')
            print()
            Console.info('Card is safe to remove')
            print()

            if i < len(worker_configs) - 1:
                if (i + 1) != ((i + 1) % len(devices)):
                    slot = devices[(i + 1) % len(devices)]
                    print()
                    print(f"Please remove any card from slot {slot} and insert a new one.")
                    if yn_choice("Is the card inserted and do you wish to continue?"):
                        pass
                    else:
                        return ""

        Console.info(f"You burned {count} SD Cards")
        Console.ok("Done :)")
