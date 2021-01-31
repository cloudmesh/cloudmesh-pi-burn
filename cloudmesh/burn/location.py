from pathlib import Path
import os
import ctypes
import ctypes.util
import os
from cloudmesh.common.Shell import Shell
import platform


def os_is_windows():
    """
    Checks if the os is windows

    :return: True is windows
    :rtype: bool
    """
    return platform.system() == "Windows"


def os_is_linux():
    """
    Checks if the os is linux

    :return: True is linux
    :rtype: bool
    """
    return platform.system() == "Linux" and "raspberry" not in platform.uname()


def os_is_mac():
    """
    Checks if the os is macOS

    :return: True is macOS
    :rtype: bool
    """
    return platform.system() == "Darwin"


def os_is_pi():
    """
    Checks if the os is Raspberry OS

    :return: True is Raspberry OS
    :rtype: bool
    """
    return "raspberry" in platform.uname()


class Location:

    def __init__(self, os=None, host=None):
        """
        Creates mount point strings based on OS and the host where it is executed

        :param os: the os that is part of the mount. Default: raspberry
        :type os: str
        :param host: the host on which we execute the command
        :type host: possible values: raspeberry, darwin, ubuntu
        """
        self.os = os or "raspberry"
        self.host = host or "raspberry"
        print (self.os, self.host)

    @property
    def root_volume(self):
        """
        the location of system volume on the SD card for the specified host
        and os in Location initialization

        TODO: not implemented

        :return: the location
        :rtype: str
        """
        if self.os == "raspberry" and self.host =="darwin":
            raise "not supported without paragon"
            # return "/volume/???"
        elif self.host == 'ubuntu':
            user = os.environ.get('USER')
            if "raspberry" in self.os:
                return Path(f"/media/{user}/rootfs")
            if "ubuntu" in self.os:
                return Path(f"/media/{user}/writable")
        return "undefined"

    @property
    def boot_volume(self):
        """
        the location of the boot volume for the specified host and os in
        Location initialization

        :return: the location
        :rtype: str
        """
        if self.host == "darwin":
            if "raspberry" in self.os:
                return  Path("/Volume/boot")
            elif "ubuntu" in self.os:
                return  Path("/Volume/system-boot")
        elif self.host == "ubuntu":
            user = os.environ.get('USER')
            if "raspberry" in self.os:
                return Path(f"/media/{user}/boot")
            elif "ubuntu" in self.os:
                return Path(f"/media/{user}/system-boot")
        return "undefined"

    @staticmethod
    def mount(source, target, fs, options=''):
        """
        mount('/dev/sdb1', '/mnt', 'ext4', options='rw')

        @param target: the tagret to be mounted. Ex. /dev/sdb1
        @type target: str
        @param fs: the mount point. Example /mnt/a
        @type fs: str
        @param options: read and write options. default rw
        @type options: str
        @return: rteurn value
        @rtype: int
        """

        libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
        libc.mount.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p)

        ret = libc.mount(source.encode(), target.encode(), fs.encode(), 0, options.encode())
        if ret < 0:
            errno = ctypes.get_errno()
            raise OSError(errno,
                          f"Error mounting {source} ({fs}) on {target} with options '{options}': {os.strerror(errno)}")

    def mount_ls(self):
        r = Shell.run("mount -l").splitlines()
        root_fs = self.root_volume
        boot_fs = self.boot_volume
        print (root_fs)
        print(boot_fs)

        details = {}
        for line in r:
            if str(root_fs) in line or str(boot_fs)  in line:
                entry = \
                    line.replace(" on ", "|")\
                    .replace(" type ", "|")\
                    .replace(" (","|")\
                    .replace(") [","|")\
                    .replace("]", "")\
                    .split("|")
                detail = {
                    "dev": entry[0],
                    "fs": entry[1],
                    "type": entry[2],
                    "parameters": entry[3],
                    "name": entry[4],
                }
                details[detail["name"]] = detail
        return details

    def mount_card(self):
        root_fs = self.root_volume
        boot_fs = self.boot_volume

        #if os_is_linux():
        #    Location.mount(root_fs,)

    def unmount(self):
        root_fs = self.root_volume
        boot_fs = self.boot_volume



