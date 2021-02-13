import os
from pathlib import Path

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import get_platform


class SDCard:

    def __init__(self, card_os=None, host=None):
        """
        Creates mount point strings based on OS and the host where it is executed

        :param os: the os that is part of the mount. Default: raspberry
        :type os: str
        :param host: the host on which we execute the command
        :type host: possible values: raspberry, macos, linux
        """
        self.card_os = card_os or "raspberry"
        self.host = host or get_platform()

    @property
    def root_volume(self):
        """
        the location of system volume on the SD card for the specified host
        and os in Location initialization

        TODO: not implemented

        :return: the location
        :rtype: str
        """
        user = os.environ.get('USER')
        if self.card_os == "raspberry" and self.host == "macos":
            return Path("/Volumes/rootfs")
        elif self.host == 'linux':
            if "raspberry" in self.card_os:
                return Path(f"/media/{user}/rootfs")
            if "linux" in self.card_os:
                return Path(f"/media/{user}/writable")
        elif self.host == "raspberry":
            if "raspberry" in self.card_os:
                return Path(f"/media/{user}/rootfs")
            if "linux" in self.card_os:
                return Path(f"/media/{user}/writable")
        elif self.host == "windows":
            Console.error("Windows is not yet supported")
        return "undefined"

    @property
    def boot_volume(self):
        """
        the location of the boot volume for the specified host and os in
        Location initialization

        :return: the location
        :rtype: str
        """
        user = os.environ.get('USER')
        if self.host == "macos":
            if "raspberry" in self.card_os:
                return Path("/Volumes/boot")
            elif "linux" in self.card_os:
                return Path("/Volume/system-boot")
        elif self.host == "linux":
            if "raspberry" in self.card_os:
                return Path(f"/media/{user}/boot")
            elif "linux" in self.card_os:
                return Path(f"/media/{user}/system-boot")
        elif self.host == "raspberry":
            if "raspberry" in self.card_os:
                return Path(f"/media/{user}/boot")
            elif "linux" in self.card_os:
                return Path(f"/media/{user}/system-boot")
        elif self.host == "windows":
            Console.error("Windows is not yet supported")
        return "undefined"

    def ls(self):
        """
        List all file systems on the SDCard. This is for the PI rootfs and boot

        :return: A dict representing the file systems on the SDCCards
        :rtype: dict
        """

        r = Shell.run("mount -l").splitlines()
        root_fs = self.root_volume
        boot_fs = self.boot_volume

        details = {}
        for line in r:
            if str(root_fs) in line or str(boot_fs) in line:
                entry = \
                    line.replace(" on ", "|") \
                        .replace(" type ", "|") \
                        .replace(" (", "|") \
                        .replace(") [", "|") \
                        .replace("]", "") \
                        .split("|")
                print(entry)
                detail = {
                    "device": entry[0],
                    "path": entry[1],
                    "type": entry[2],
                    "parameters": entry[3],
                    "name": entry[4],
                }
                details[detail["name"]] = detail
        return details
