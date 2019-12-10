from cmburn.pi.util import readfile, writefile
from cmburn.pi import columns, lines

from cmburn.pi.util import WARNING

import os
import sys
from pprint import pprint
from cmburn.pi.image import Image
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import banner
from cloudmesh.common.console import Console
from cloudmesh.common.util import yn_choice


class Burner(object):

    def __init__(self, dryrun=False):
        #
        # BUG this is actually a bug ;-) we should do this differently ;-)
        #
        self.cm_burn = Shell.which("/home/pi/ENV3/bin/cm-pi-burn")
        self.dryrun = dryrun

    def detect(self):
        """
        banner("Detecting USB Card Reader")

        print ("Make sure the USB Reader is removed ...")
        if not yn_choice("Is the reader removed?"):
            sys.exit()
        usb_out = set(Shell.execute("lsusb").splitlines())
        print ("Now plug in the Reader ...")
        if not yn_choice("Is the reader pluged in?"):
            sys.exit()
        usb_in = set(Shell.execute("lsusb").splitlines())
        
        """
        usb_out =  set(['Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub',
                    'Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub',
                    'Bus 001 Device 004: ID 413c:2113 Dell Computer Corp. ',
                    'Bus 001 Device 003: ID 046d:c077 Logitech, Inc. M105 Optical Mouse',
                    'Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub',
                    'Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub'])
        usb_in  =  set(['Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub',
                    'Bus 002 Device 005: ID 05e3:0749 Genesys Logic, Inc. ',
                    'Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub',
                    'Bus 001 Device 004: ID 413c:2113 Dell Computer Corp. ',
                    'Bus 001 Device 003: ID 046d:c077 Logitech, Inc. M105 Optical Mouse',
                    'Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub',
                    'Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub'])

        writer = usb_in - usb_out
        if len(writer) == 0:
            print("ERROR: we did not detect the devise, make sure it is plugged.")
            sys.exit()
        else:
            banner("Detected Card Writer")

            print (" ".join(writer))
            print()
            
        
    def info(self):
        print("cm-pi-burn:", self.cm_burn)
        print("dryrun:    ", self.dryrun)

        banner("Operating System")
        os.system("fdisk -l /dev/mmcblk0")

        banner("SD-Card")

        sda = Shell.execute("fdisk", ["-l", "/dev/sda"])
        print(sda)
        if "Linux" in sda:
            Console.error("the SD-Card is not empty")
        if "FAT32" not in sda:
            Console.error("the SD-Card is not properly formatted")


        #
        # use also lsub -v
        #

        # see also
        # https://raspberry-pi-guide.readthedocs.io/en/latest/system.html
        # this is for fedora, but should also work for rasbian

    def system(self, command):
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
            with open(f'{mountpoint}/etc/hostname', 'w') as f:
                f.write(hostname + '\n')
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
            with open(mountpoint + '/etc/hosts',
                      'w') as f:  # and write the modified version
                for line in lines:
                    f.write(line)
                f.write(newlastline)
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
        #  static ip_addres=[IP]/24
        if not self.dryrun:

            with open(f'{mountpoint}/etc/dhcpcd.conf') as f:
                lines = [l for l in f.readlines()]
            with open(f'{mountpoint}/etc/dhcpcd.conf', 'w') as f:
                for line in lines:
                    f.write(line)
                f.write('interface eth0\n')
                f.write(f'static ip_address={ip}/24')
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
        self.system(f'mkdir -p {mountpoint} /home/pi/.ssh/')
        self.system(f'cp ~/.ssh/{name}.pub {mountpoint} /home/pi/.ssh/authorized_keys')

    def mount(self, device, mountpoint="/mount/pi"):
        """
            Mounts the current SD card
            :param device: Device to mount, e.g. /dev/mmcblk0
            :param mountpoint: Mountpoint, e.g. /mount/pi - note no trailing
                               slash
            """
        # mount p2 (/) and then p1 (/boot)

        self.system(f'sudo rmdir {mountpoint}')
        self.system(f'sudo mkdir -p {mountpoint}')
        # depending on how SD card is interfaced to system:
        # if /dev/mmcblkX, partitions will be /dev/mmcblkXp1 and /dev/mmcblkXp2
        if 'mmc' in device:
            self.system(f'sudo mount {device}p2 {mountpoint}')
            self.system(f'sudo mount {device}p1 {mountpoint}/boot')
            # if /dev/sdX, partitions will be /dev/sdX1 and /dev/sdX2
        else:
            self.system(f'sudo mount {device}2 {mountpoint}')
            self.system(f'sudo mount {device}1 {mountpoint}/boot')

    def unmount(self, device):
        """
            Unmounts the current SD card
            :param device: Device to unmount, e.g. /dev/mmcblk0
            """
        # unmount p1 (/boot) and then p1 (/)
        self.system(f'sudo umount {device}p1')
        try:
            self.system(f'sudo umount {device}p1')
        except:
            pass
        self.system(f'sudo umount {device}p2')

    def enable_ssh(self, mountpoint):
        """
            Enables ssh on next boot of sd card
            """
        # touch mountpoint/boot/ssh
        command = f'sudo touch {mountpoint}/boot/ssh'
        self.system(command)

class MultiCardBurner(object):
    """pseudo code, please complete

    This class uses a single or multicard burner to burn SD Cards. It detects
    how many SD Cards are there and uses them. We assumom no other USB devices
    are blugged in other than a keyboard or a mouse.

    """



    def __init__(self, prefix="/dev/sd", devices="abcdefgh"):
        """


        :param devices: string with device letters
        """

        #
        # define the dev
        #
        self.devices = [] # dict of {name: status}
        device_letters = devices.split()
        for device in device_letters:
            dev = f'{prefix}{device}'
            self.devices.append(dict({dev, None}))
        #
        # probe the dev
        #
        for device, status in self.devices:
            print ("call the info command on the device and "
                   "figure out if an empty card is in it")
            # change the status based on what you found

        # print out the status of the devices in a table

        # detect if tehre is an issue with the cards, readers

        # if we detect a non empty card we interrupt and tell which is not empty.

        # ask if this is ok to burn otherwise

        # if yes burn all of them for which we have status "empty card"

        for device, status in self.devices:
            if status == "empty card":
                raise NotImplementedError
                # burn the card, use the Burner class

    def burn(self,
             image="latest",
             device="dev/sda",
             blocksize="4M",
             progress=True):
        """
        Burns the image on the specific device

        :param devive:
        :param image:
        :param blocksize:
        :param progress:
        :return:
        """
        raise NotImplementedError
