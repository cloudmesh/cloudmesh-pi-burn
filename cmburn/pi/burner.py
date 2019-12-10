from cmburn.pi.util import readfile, writefile
from cmburn.pi import columns, lines

from cmburn.pi.util import WARNING

import os
from cmburn.pi.image import Image

class Burner(object):

    @staticmethod
    def system(command, dryrun=False):
        if dryrun:
            print (command)
        else:
            os.system(command)

    @staticmethod
    def burn(image, device, blocksize="4M", dryrun=False):
        """
        Burns the SD Card with an image
        :param image: Image object to use for burning
        :param device: Device to burn to, e.g. /dev/mmcblk0
        """
        # dd if=image.img of=/dev/mmcblk0

        image_path = Image(image).fullpath

        Burner.system('sudo dd bs={} if={} of={}'.format(blocksize, image_path, device),
                      dryrun=dryrun)

    @staticmethod
    def set_hostname(hostname, mountpoint, dryrun=False):
        """
        Sets the hostname on the sd card
        :param hostname: hostname
        """
        # write the new hostname to /etc/hostname
        if not dryrun:
            with open(mountpoint + '/etc/hostname', 'w') as f:
                f.write(hostname + '\n')
        else:
            print()
            print ("Write to /etc/hostname")
            print(hostname)

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        if not dryrun:
            with open(mountpoint + '/etc/hosts', 'r') as f:  # read /etc/hosts
                lines = [l for l in f.readlines()][:-1]  # ignore the last line
                newlastline = '127.0.1.1 ' + hostname + '\n'

        if not dryrun:
            with open(mountpoint + '/etc/hosts',
                      'w') as f:  # and write the modified version
                for line in lines:
                    f.write(line)
                f.write(newlastline)
        else:
            print()
            print ("Write to /etc/hosts")
            print ('127.0.1.1 ' + hostname + '\n')


    @staticmethod
    def set_static_ip(ip, mountpoint, dryrun=False):
        """
        Sets the static ip on the sd card
        :param ip: IP address
        """
        # append to mountpoint/etc/dhcpcd.conf:
        #  interface eth0
        #  static ip_addres=[IP]/24
        if not dryrun:

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

    @staticmethod
    def set_key(name, mountpoint, dryrun=False):
        """
        Copies the public key into the .ssh/authorized_keys file on the sd card
        :param name: name of public key, e.g. 'id_rsa' for ~/.ssh/id_rsa.pub
        """
        # copy file on burner computer ~/.ssh/id_rsa.pub into
        #   mountpoint/home/pi/.ssh/authorized_keys
        Burner.system('mkdir -p ' + mountpoint + '/home/pi/.ssh/', dryrun=dryrun)
        Burner.system(
            'cp ~/.ssh/' + name + '.pub ' + mountpoint + '/home/pi/.ssh/authorized_keys', dryrun=dryrun)

    @staticmethod
    def mount(device, mountpoint="/mount/pi", dryrun=False):
        """
        Mounts the current SD card
        :param device: Device to mount, e.g. /dev/mmcblk0
        :param mountpoint: Mountpoint, e.g. /mount/pi - note no trailing slash
        """
        # mount p2 (/) and then p1 (/boot)

        Burner.system('sudo rmdir ' + mountpoint, dryrun=dryrun)
        Burner.system('sudo mkdir -p ' + mountpoint, dryrun=dryrun)
        # depending on how SD card is interfaced to system:
        # if /dev/mmcblkX, partitions will be /dev/mmcblkXp1 and /dev/mmcblkXp2
        if 'mmc' in device:
            Burner.system('sudo mount ' + device + 'p2 ' + mountpoint, dryrun=dryrun)
            Burner.system('sudo mount ' + device + 'p1 ' + mountpoint + '/boot', dryrun=dryrun)
        # if /dev/sdX, partitions will be /dev/sdX1 and /dev/sdX2
        else:
            Burner.system('sudo mount ' + device + '2 ' + mountpoint, dryrun=dryrun)
            Burner.system('sudo mount ' + device + '1 ' + mountpoint + '/boot', dryrun=dryrun)

    @staticmethod
    def unmount(device, dryrun=False):
        """
        Unmounts the current SD card
        :param device: Device to unmount, e.g. /dev/mmcblk0
        """
        # unmount p1 (/boot) and then p1 (/)
        Burner.system('sudo umount ' + device + 'p1', dryrun=dryrun)
        try:
            Burner.system('sudo umount ' + device + 'p1', dryrun=dryrun)
        except:
            pass
        Burner.system('sudo umount ' + device + 'p2', dryrun=dryrun)

    @staticmethod
    def enable_ssh(mountpoint, dryrun=False):
        """
        Enables ssh on next boot of sd card
        """
        # touch mountpoint/boot/ssh
        command = 'sudo touch ' + mountpoint + '/boot/ssh'
        Burner.system(command, dryrun=dryrun)

