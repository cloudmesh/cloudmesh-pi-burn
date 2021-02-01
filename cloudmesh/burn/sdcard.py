import os
from pathlib import Path

from cloudmesh.common.Shell import Shell
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_windows
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi

class SDCard:

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

    @property
    def root_volume(self):
        """
        the location of system volume on the SD card for the specified host
        and os in Location initialization

        TODO: not implemented

        :return: the location
        :rtype: str
        """
        if self.os == "raspberry" and self.host == "darwin":
            raise "not supported without paragon"
            # return "/volume/???"
        elif self.host == 'ubuntu':
            user = os.environ.get('USER')
            if "raspberry" in self.os:
                return Path(f"/media/{user}/rootfs")
            if "ubuntu" in self.os:
                return Path(f"/media/{user}/writable")
        elif host == "raspberty":
            raise NotImplementedError
        elif host == "windows":
            raise NotImplementedError
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
                return Path("/Volume/boot")
            elif "ubuntu" in self.os:
                return Path("/Volume/system-boot")
        elif self.host == "ubuntu":
            user = os.environ.get('USER')
            if "raspberry" in self.os:
                return Path(f"/media/{user}/boot")
            elif "ubuntu" in self.os:
                return Path(f"/media/{user}/system-boot")
        elif host == "raspberty":
            raise NotImplementedError
        elif host == "windows":
            raise NotImplementedError
        return "undefined"

    def ls(self):
        """
        List all file systems on the SDCard. This is for the PI rootfs and boot

        @return: A dict representing the file systems on the SDCCards
        @rtype: dict
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
                detail = {
                    "device": entry[0],
                    "path": entry[1],
                    "type": entry[2],
                    "parameters": entry[3],
                    "name": entry[4],
                }
                details[detail["name"]] = detail
        return details
