import os
import sys
import time
import glob
from cmburn.pi.image import Image
from cloudmesh.common.util import banner
from cloudmesh.common.util import yn_choice
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from pprint import pprint

# TODO: make sure everything is compatible with --dryrun

# noinspection PyPep8
class Burner(object):

    def __init__(self, dryrun=False):
        """

        :param dryrun:
        """
        #
        # BUG this is actually a bug ;-) we should do this differently ;-)
        #
        self.cm_burn = Shell.which("/home/pi/ENV3/bin/cm-pi-burn")
        self.dryrun = dryrun

    def detect(self):
        """

        :return:
        """
        banner("Detecting USB Card Reader")

        print("Make sure the USB Reader is removed ...")
        if not yn_choice("Is the reader removed?"):
            sys.exit()
        usb_out = set(Shell.execute("lsusb").splitlines())
        print("Now plug in the Reader ...")
        if not yn_choice("Is the reader plugged in?"):
            sys.exit()
        usb_in = set(Shell.execute("lsusb").splitlines())

        writer = usb_in - usb_out
        if len(writer) == 0:
            print(
                "ERROR: we did not detect the devise, make sure it is plugged.")
            sys.exit()
        else:
            banner("Detected Card Writer")

            print("\n".join(writer))
            print()

    def info(self, print_stdout=True):
        """

        :return:
        """

        print("cm-pi-burn:", self.cm_burn)
        print("dryrun:    ", self.dryrun)

        banner("Operating System")
        if print_stdout:
            os.system("sudo fdisk -l /dev/mmcblk0")
        else:
            os.system("sudo fdisk -l /dev/mmcblk0 &>/dev/null")

        dmesg = Shell.run(f"dmesg").splitlines()

        # banner("SD-Card Search")
        status = {}
        # devices = [f"/dev/sd{x}" for x in list("abcdefghijklm")]
        devices = glob.glob("/dev/sd?")

        for device in devices:
            status[device] = {}
            # banner(device)

            sd = Shell.run(f"sudo fdisk -l {device}")
            if "cannot open" in sd:
                # Console.error(f"no SD Card Writer in device {device}")
                status[device]["reader"] = False
            else:
                status[device]["reader"] = True

            if "Linux" in sd:
                # Console.error("the SD-Card is not empty")
                status[device]["empty"] = False
            else:
                status[device]["empty"] = True

            if "FAT32" not in sd:
                # Console.error("the SD-Card is not properly formatted")
                status[device]["formatted"] = False
            else:
                status[device]["formatted"] = True

            sdx = device.replace("/dev/", "")
            msg = [i.split("]", 1)[1].strip() for i in dmesg if
                   sdx in i and "sdhci" not in i and "sdio" not in i]
            if len(msg) > 0:
                # print (sdx)
                # pprint (msg)
                information = '\n'.join(msg)
                status[device].update(dict(
                    {'name': sdx,
                     'dev': device,
                     'removable_disk': 'Attached SCSI removable disk' in information,
                     'write_protection': "Write Protect is off" not in information,
                     'size': information.split("blocks:", 1)[1].split("\n", 1)[
                         0].replace("(", "").replace(")", "")
                     }))
                # pprint(information)

        if print_stdout:
            # pprint(status)
            banner("SD Cards Found")
            print(Printer.write(status,
                                order=["name", "dev", "reader", "formatted",
                                       "empty",
                                       "size", "removable_disk",
                                       "write_protection"],
                                header=["Name", "Device", "Reader", "Formatted",
                                        "Empty",
                                        "Size", "Removable", "Protected"]))
        return status

        #
        # use also lsub -v
        #

        # see also
        # https://raspberry-pi-guide.readthedocs.io/en/latest/system.html
        # this is for fedora, but should also work for rasbian

    def system(self, command):
        """

        :param command:
        :return:
        """
        if self.dryrun:
            print(command)
        else:
            os.system(command)

    def burn(self, image, device, blocksize="4M"):
        """
        Burns the SD Card with an image

        :param image: Image object to use for burning
        :param device: Device to burn to, e.g. /dev/sda
        :param blocksize:
        :return:
        """

        image_path = Image(image).fullpath

        self.system(f'sudo dd bs={blocksize} if={image_path} of={device}')

    def set_hostname(self, hostname, mountpoint):
        """
        Sets the hostname on the sd card

        :param hostname: hostname
        :param mountpoint: TBD
        """
        # write the new hostname to /etc/hostname
        if not self.dryrun:
            self.system(f'echo {hostname} | sudo cp /dev/stdin {mountpoint}/etc/hostname')
        else:
            print()
            print("Write to /etc/hostname")
            print(hostname)

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        if not self.dryrun:
            with open(f'{mountpoint}/etc/hosts', 'r') as f:  # read /etc/hosts
                lines = [l for l in f.readlines()][:-1]  # ignore the last line
                newlastline = '127.0.1.1 ' + hostname + '\n'

        if not self.dryrun:
            new_hostsfile_contents = ''.join(lines) + newlastline
            self.system(f'echo "{new_hostsfile_contents}" | sudo cp /dev/stdin {mountpoint}/etc/hosts')
        else:
            print()
            print("Write to /etc/hosts")
            print('127.0.1.1 ' + hostname + '\n')

    def set_static_ip(self, ip, mountpoint):
        """
        Sets the static ip on the sd card

        :param ip: IP address
        :param mountpoint: TBD
        """
        # append to mountpoint/etc/dhcpcd.conf:
        #  interface eth0
        #  static ip_address=[IP]/24
        if not self.dryrun:

            with open(f'{mountpoint}/etc/dhcpcd.conf') as f:
                lines = [l for l in f.readlines()]
            new_dhcpcd_contents = ''.join(lines)
            new_dhcpcd_contents += 'interface eth0\n'
            new_dhcpcd_contents += f'static ip_address={ip}/24\n'
            self.system(f'echo "{new_dhcpcd_contents}" | sudo cp /dev/stdin {mountpoint}/etc/dhcpcd.conf')
        else:
            print('interface eth0\n')
            print(f'static ip_address={ip}/24')

    def set_key(self, name, mountpoint):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card

        :param name: name of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        :param mountpoint: TBD
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys
        self.system(f'mkdir -p {mountpoint}/home/pi/.ssh/')
        self.system(
            f'cp ~/.ssh/{name}.pub {mountpoint}/home/pi/.ssh/authorized_keys')

    def mount(self, device, mountpoint="/mount/pi"):
        """
        Mounts the current SD card

        :param device: Device to mount, e.g. /dev/sda
        :param mountpoint: Mountpoint, e.g. /mount/pi - note no trailing
                           slash
        """
        # mount p2 (/) and then p1 (/boot)

        if not self.dryrun:
            # wait for the OS to detect the filesystems
            # in burner.info(), formatted will be true if the card has FAT32
            #   filesystems on it
            counter = 0
            max_tries = 5
            b = Burner()
            while counter < max_tries:
                time.sleep(1)
                formatted = b.info(print_stdout=False)[device]['formatted']
                if formatted:
                    break
                counter += 1
                if counter == max_tries:
                    print("Timed out waiting for OS to detect filesystem on burned card")
                    sys.exit(1)
        self.system(f'sudo mkdir -p {mountpoint}')
        self.system(f'sudo mount {device}2 {mountpoint}')
        self.system(f'sudo mount {device}1 {mountpoint}/boot')

    def unmount(self, device):
        """
        Unmounts the current SD card

        :param device: Device to unmount, e.g. /dev/sda
        """
        if not self.dryrun:
            self.system('sudo sync') # flush any pending/in-process writes

        # unmount p1 (/boot) and then p1 (/)
        self.system(f'sudo umount {device}1')
        try:
            self.system(f'sudo umount {device}1')
        except:
            pass
        self.system(f'sudo umount {device}2')

    def enable_ssh(self, mountpoint):
        """

        :param mountpoint:
        :return:
        """
        """
            Enables ssh on next boot of sd card
            """
        # touch mountpoint/boot/ssh
        command = f'sudo touch {mountpoint}/boot/ssh'
        self.system(command)


    def format(self, devices=None):
        """

        :param devices:
        :return:
        """
        if devices is None:
            return
        for device in devices:
            self.umount(device)
            command = f"sudo mkfs.vfat -F32 -v {device}"
            if self.dryrun:
                print(command)
            else:
                os.system(f"sudo mkfs.vfat -F32 -v {device}")


class MultiBurner(object):
    """pseudo code, please complete

    This class uses a single or multicard burner to burn SD Cards. It detects
    how many SD Cards are there and uses them. We assume no other USB devices
    are plugged in other than a keyboard or a mouse.

    """

    def burn_all(self,
             image="latest",
             device="dev/sda",
             blocksize="4M",
             progress=True,
             hostnames=None,
             ips=None,
             key=None):
        """
        :param image:
        :param device:
        :param blocksize:
        :param progress:
        :param hostnames:
        :param ips:
        :param key:
        :return:
        """

        #:param devices: string with device letters

        #
        # define the dev
        #
        devices = {}  # dict of {device_name: empty_status}
        #
        # probe the dev
        #
        #pprint(Burner().info())
        info_statuses = Burner().info()
        for device in info_statuses.keys():
            #print("call the info command on the device and "
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
                print(f"Device {dev} is {x}empty")
        print()

        # detect if there is an issue with the cards, readers
        # TODO what exactly should be done here?

        # ask if this is ok to burn otherwise
        burn_all = yn_choice("Burn non-empty devices too?")

        # if yes burn all of them for which we have status "empty card"
        if not burn_all:
            # delete from devices dict any non-empty devices
            devices_to_delete = []
            for device in devices.keys():
                if devices[device] == False:
                    devices_to_delete.append(device) # can't delete while iterating
            for device in devices_to_delete:
                del devices[device]

        print("Burning these devices:")
        print(' '.join(devices.keys()))

        keys = list(devices.keys())
        for i in range(len(keys)):
        #for device, status in devices.items():
            device = keys[i]
            status = devices[device]
            hostname = hostnames[i]
            ip = ips[i]
            self.burn(image, device, blocksize, progress, hostname, ip, key)

            os.system('tput bel')  # ring the terminal bell to notify user
            print()
            if i < len(keys) - 1:
                input('Insert next card and press enter...')
                print('Burning next card...')
                print()
        i += 1
        print(f"You burned {i} SD Cards")
        print("Done.")

    def burn(self,
             image="latest",
             device="/dev/sda",
             blocksize="4M",
             progress=True,
             hostname=None,
             ip=None,
             key=None):
        """

        :param image:
        :param device:
        :param blocksize:
        :param progress:
        :param hostname:
        :param ip:
        :param key:
        :return:
        """
        # Burns the image on the specific device

        mp = '/mount/pi'

        # don't do the input() after burning the last card
        # use a counter to check this
        
        counter = 0
        burner = Burner()
        for i in range(1):

            print("counter", counter)
            StopWatch.start("fcreate {hostname}")

            burner.burn(image, device, blocksize=blocksize)
            
            burner.mount(device, mp)
            
            burner.enable_ssh(mp)
            burner.set_hostname(hostname, mp)
            burner.set_key(key, mp)
            burner.set_static_ip(ip, mp)
            burner.unmount(device)
            # for some reason, need to do unmount twice for it to work properly
            burner.unmount(device)
            StopWatch.start("fcreate {hostname}")

