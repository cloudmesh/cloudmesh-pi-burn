from cmburn.pi.util import readfile, writefile
from cmburn.pi import columns, lines

from cmburn.pi.util import WARNING

import os
from cmburn.pi.image import Image

class Burner(object):

    @staticmethod
    def burn(image, device):
        """
        Burns the SD Card with an image
        :param image: Image object to use for burning
        :param device: Device to burn to, e.g. /dev/mmcblk0
        """
        # cat image.img >/dev/mmcblk0
        os.system('sudo cat ' + Image(image).fullpath + ' >' + device)

    @staticmethod
    def set_hostname(hostname, mountpoint):
        """
        Sets the hostname on the sd card
        :param hostname: hostname
        """
        # write the new hostname to /etc/hostname
        with open(mountpoint + '/etc/hostname', 'w') as f:
            f.write(hostname + '\n')

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        with open(mountpoint + '/etc/hosts', 'r') as f:  # read /etc/hosts
            lines = [l for l in f.readlines()][:-1]  # ignore the last line
            newlastline = '127.0.1.1 ' + hostname + '\n'

        with open(mountpoint + '/etc/hosts',
                  'w') as f:  # and write the modified version
            for line in lines:
                f.write(line)
            f.write(newlastline)

    @staticmethod
    def set_static_ip(ip, mountpoint):
        """
        Sets the static ip on the sd card
        :param ip: IP address
        """
        # append to mountpoint/etc/dhcpcd.conf:
        #  interface eth0
        #  static ip_addres=[IP]/24
        with open(mountpoint + '/etc/dhcpcd.conf') as f:
            lines = [l for l in f.readlines()]
        with open(mountpoint + '/etc/dhcpcd.conf', 'w') as f:
            for line in lines:
                f.write(line)
            f.write('interface eth0\n')
            f.write('static ip_address=' + ip + '/24')

    @staticmethod
    def set_key(name, mountpoint):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card
        :param name: name of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys
        os.system('mkdir -p ' + mountpoint + '/home/pi/.ssh/')
        os.system(
            'cp ~/.ssh/' + name + '.pub ' + mountpoint + '/home/pi/.ssh/authorized_keys')

    @staticmethod
    def mount(device, mountpoint="/mount/pi"):
        """
        Mounts the current SD card
        :param device: Device to mount, e.g. /dev/mmcblk0
        :param mountpoint: Mountpoint, e.g. /mount/pi - note no trailing slash
        """
        # mount p2 (/) and then p1 (/boot)

        os.system('sudo rmdir ' + mountpoint)
        os.system('sudo mkdir -p ' + mountpoint)
        # depending on how SD card is interfaced to system:
        # if /dev/mmcblkX, partitions will be /dev/mmcblkXp1 and /dev/mmcblkXp2
        if 'mmc' in device:
            os.system('sudo mount ' + device + 'p2 ' + mountpoint)
            os.system('sudo mount ' + device + 'p1 ' + mountpoint + '/boot')
        # if /dev/sdX, partitions will be /dev/sdX1 and /dev/sdX2
        else:
            os.system('sudo mount ' + device + '2 ' + mountpoint)
            os.system('sudo mount ' + device + '1 ' + mountpoint + '/boot')

    @staticmethod
    def unmount(device):
        """
        Unmounts the current SD card
        :param device: Device to unmount, e.g. /dev/mmcblk0
        """
        # unmount p1 (/boot) and then p1 (/)
        os.system('sudo umount ' + device + 'p1')
        try:
            os.system('sudo umount ' + device + 'p1')
        except:
            pass
        os.system('sudo umount ' + device + 'p2')

    @staticmethod
    def enable_ssh(mountpoint):
        """
        Enables ssh on next boot of sd card
        """
        # touch mountpoint/boot/ssh
        os.system('sudo touch ' + mountpoint + '/boot/ssh')

