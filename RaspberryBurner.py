"""
3. cp -r /home/pi/.ssh /media/pi/rootfs/home/pi/ .
4. chmod -R pi /media/pi/rootfs/home/pi/.ssh
   chgrp -R pi /media/pi/rootfs/home/pi/.ssh
5. Figure out how to add static IP to Raspberry Pi
6. Figure out how to umount from /media/pi
7. Check cm-burn
"""


class Image(object):

    def __init__(self, name):
        if name == "latest":
            self.url = "abc"

    def fetch(self):
        # if image is already there skip
        # else downlod from url using python requests
        # see cmburn.py you can copy form there
        raise NotImplementedError

    def verify(self):
        # verifiy if the image is ok, ise sha
        raise NotImplementedError

    def rm(self):
        # remove the downloaded image
        raise NotImplementedError


class Burner(object):

    def __init__(self, device=None, name="red01"):
        pass

    def burn(self, image):
        """
        burns the SD Card

        :param image: name of the image
        :return:
        """
        raise NotImplementedError

    def set_hostname(self, hostname):
        """
        sets the hostname on the sdc card

        :param hostname:
        :return:
        """
        # 1. echo "red01" > /media/pi/rootfs/etc/hostname
        raise NotImplementedError

    def set_static_ip(self, ip):
        """
        Sets the static ip on the sd card

        :param ip:
        :return:
        """
        raise NotImplementedError

    def set_keys(self):
        """
        copies the public key into the .ssh/authorized_keys file on the sd card
        :return:
        """
        raise NotImplementedError

    def mount(self):
        """
        mounts the current SD card
        :return:
        """
        raise NotImplementedError

    def unmount(self):
        """
        unmounts the current SD card
        :return:
        """
        raise NotImplementedError

    def enable_ssh(self):
        """
        Enables ssh on next boot of sd card
        :return:
        """
        # touch /media/pi/boot/ssh
        raise NotImplementedError


if __name__ == "__main__":
    device = "FINDME"

    image = Image(name="latest")
    image.fetch()
    image.verify()

    sdcard = Burner(device="TBD", name="red01")
    sdcard.burn(image)
    sdcard.mount()
    sdcard.enable_ssh()
    sdcard.set_hostname()
    sdcard.set_keys()
    sdcard.set_static_ip()
    sdcard.unmount()
