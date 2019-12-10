from cmburn.pi.util import readfile, writefile
from cmburn.pi import columns, lines

from cmburn.pi.util import WARNING

import os
from cmburn.pi.image import Image
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import banner

class Burner(object):

    def __init__(self, dryrun=False):
        #
        # BUG this is actually a bug ;-) we should do this differently ;-)
        #
        self.cm_burn = Shell.which("/home/pi/ENV3/bin/cm-pi-burn")
        self.dryrun = dryrun

    def info(self):
        print("cm-pi-burn:", self._burn)
        print("dryrun:    ", self.dryrun)

        banner("Operating System")
        os.system("fdisk -l /dev/mmcblk0")

        banner("SD-Card")

        sda = Shell.execute("fdisk", ["-l", "/dev/sda"])
        print (sda)


def system(self, command):
        if self.dryrun:
            print (command)
        else:
            os.system(command)

    def burn(self, image, device, blocksize="4M"):
        """
        Burns the SD Card with an image
        :param image: Image object to use for burning
        :param device: Device to burn to, e.g. /dev/mmcblk0
        """
        # dd if=image.img of=/dev/mmcblk0

        image_path = Image(image).fullpath

        self.system('sudo dd bs={} if={} of={}'.format(blocksize, image_path, device))

    def set_hostname(self, hostname, mountpoint):
        """
        Sets the hostname on the sd card
        :param hostname: hostname
        """
        # write the new hostname to /etc/hostname
        if not self.dryrun:
            with open(mountpoint + '/etc/hostname', 'w') as f:
                f.write(hostname + '\n')
        else:
            print()
            print ("Write to /etc/hostname")
            print(hostname)

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        if not self.dryrun:
            with open(mountpoint + '/etc/hosts', 'r') as f:  # read /etc/hosts
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
            print ("Write to /etc/hosts")
            print ('127.0.1.1 ' + hostname + '\n')


    def set_static_ip(self, ip, mountpoint):
        """
        Sets the static ip on the sd card
        :param ip: IP address
        """
        # append to mountpoint/etc/dhcpcd.conf:
        #  interface eth0
        #  static ip_addres=[IP]/24
        if not self.dryrun:

            with open(mountpoint + '/etc/dhcpcd.conf') as f:
                lines = [l for l in f.readlines()]
            with open(mountpoint + '/etc/dhcpcd.conf', 'w') as f:
                for line in lines:
                    f.write(line)
                f.write('interface eth0\n')
                f.write('static ip_address=' + ip + '/24')
        else:
            print('interface eth0\n')
            print('static ip_address=' + ip + '/24')

    def set_key(self, name, mountpoint):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card
        :param name: name of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys
        self.system('mkdir -p ' + mountpoint + '/home/pi/.ssh/')
        self.system(
            'cp ~/.ssh/' + name + '.pub ' + mountpoint + '/home/pi/.ssh/authorized_keys')

    def mount(self, device, mountpoint="/mount/pi"):
        """
        Mounts the current SD card
        :param device: Device to mount, e.g. /dev/mmcblk0
        :param mountpoint: Mountpoint, e.g. /mount/pi - note no trailing slash
        """
        # mount p2 (/) and then p1 (/boot)

        self.system('sudo rmdir ' + mountpoint)
        self.system('sudo mkdir -p ' + mountpoint)
        # depending on how SD card is interfaced to system:
        # if /dev/mmcblkX, partitions will be /dev/mmcblkXp1 and /dev/mmcblkXp2
        if 'mmc' in device:
            self.system('sudo mount ' + device + 'p2 ' + mountpoint)
            self.system('sudo mount ' + device + 'p1 ' + mountpoint + '/boot')
            # if /dev/sdX, partitions will be /dev/sdX1 and /dev/sdX2
        else:
            self.system('sudo mount ' + device + '2 ' + mountpoint)
            self.system('sudo mount ' + device + '1 ' + mountpoint + '/boot')

    def unmount(self, device):
        """
        Unmounts the current SD card
        :param device: Device to unmount, e.g. /dev/mmcblk0
        """
        # unmount p1 (/boot) and then p1 (/)
        self.system('sudo umount ' + device + 'p1')
        try:
            self.system('sudo umount ' + device + 'p1')
        except:
            pass
        self.system('sudo umount ' + device + 'p2')

    def enable_ssh(self, mountpoint):
        """
        Enables ssh on next boot of sd card
        """
        # touch mountpoint/boot/ssh
        command = 'sudo touch ' + mountpoint + '/boot/ssh'
        self.system(command)

