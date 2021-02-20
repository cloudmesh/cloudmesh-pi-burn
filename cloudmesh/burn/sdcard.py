import os
from pathlib import Path

from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.sudo import Sudo
from cloudmesh.burn.util import os_is_mac
from cloudmesh.common.util import readfile


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

    @staticmethod
    def execute(command, decode="True", debug=False):
        """
        Executes the command

        :param command: The command to run
        :type command: list or str
        :return:
        :rtype:
        """

        result = Sudo.execute(command, decode=decode, debug=debug)
        return result

    @staticmethod
    def readfile(filename, split=False, trim=False, decode=True):
        """
        Reads the content of the file as sudo and returns the result

        :param filename: the filename
        :type filename: str
        :param split: uf true returns a list of lines
        :type split: bool
        :param trim: trim trailing whitespace. This is useful to
                     prevent empty string entries when splitting by '\n'
        :type trim: bool
        :return: the content
        :rtype: str or list
        """
        os.system("sync")

        if os_is_mac():
            if decode:
                mode = "r"
            else:
                mode = "rb"
            content = readfile(filename, mode=mode)
        else:
            Sudo.password()
            result = Sudo.execute(f"cat {filename}", decode=decode)
            content = result.stdout

        if trim:
            content = content.rstrip()

        if split:
            content = content.splitlines()

        return content

    @staticmethod
    def writefile(filename, content, append=False):
        """
        Writes the content in the the given file.

        :param filename: the filename
        :type filename: str
        :param content: the content
        :type content: str
        :param append: if true it append it at the end, otherwise the file will
                       be overwritten
        :type append: bool
        :return: the output created by the write process
        :rtype: int
        """

        if append:
            content = Sudo.readfile(filename, split=False, decode=True) + content

        os.system(f"echo '{content}' | sudo cp /dev/stdin {filename}")
        os.system("sync")

        return content
