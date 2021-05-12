import string

from cloudmesh.burn.util import os_is_windows
from cloudmesh.common.util import readfile, writefile
import ascii
from cloudmesh.common.Shell import Shell

# we need to deal with that imports of windos libraries are conditional

if os_is_windows():
    from ctypes import windll


# see mountvol
# see diskpart

# https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-vista/cc766465(v=ws.10)?redirectedfrom=MSDN

class Windows:

    # device will be likely of form Z:/path we need to use Path from new python 3

    # see https://superuser.com/questions/704870/mount-and-dismount-hard-drive-through-a-script-software#:~:text=Tutorial,open%20Command%20Prompt%20as%20Administrator.&text=To%20mount%20a%20drive%2C%20type,you%20noted%20in%20Step%202.

    def __init__(self, device=None):
        self.device = device

    def get_drives():
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1

        return drives

    def find_free_drive_letter(self):
        """
        returns the first free driveletter
        :return: returns a free drive letter
        :rtype:
        """
        drives = self.get_drives()
        for drive in ascii.charlist()[10:]:
            if drive not in drives:
                return drive
        return ValueError("no free drive found")

    def unmount(self, device=None):
        """
        unmounts the device

        :param device:
        :type device:
        :return:
        :rtype:
        """
        os.system(f"mountvol {device} /p")

    def mount(self, device=None):
        """
        mounts the device

        :param device:
        :type device:
        :return:
        :rtype:
        """
        # this will use mountvol
        raise NotImplementedError

    def format_device(self, device=None, unmount=True):
        """
        formats the device
        :param device: is a drive latte in Windows
        :type device: str
        :return:
        :rtype:
        """
        # see https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/format
        if unmount:
            set_unmount = "/x"
        else:
            set_unmount = ""
        command = f"format {device} /fs:FAT32 /v:UNTITLED /q {set_unmount}".strip()
        print(command)
        # os.system(command)  ## this must be checked to prevent disaster
        raise NotImplementedError

    def info(self):
        """
        Prints information about the USB and sdcard if it is available

        :return:
        :rtype:
        """
        command = f"mountvol {self.device} /L"
        r = Shell.run(command)
        print (r)
        # see also gregos implementation for mac, osx, and raspberry,
        # that just may work

        # diskpart list disk
        # diskpart detail disk
        # diskpart detail volume

        # diskpart /s <script_file>

        #os.system("diskpart list disk")

        # Path pathlib
        # filename = Path("/tmp/list-disk.txt")

        # writefile(filename, "list disk\n\exit")
        # os.system(f"diskpart /s {filename}")


# TASK 1 explre sdcard that has raspberry os on it.
'''
1. plug in card with raspberry os burned on it
2. see hw the card registers
3. prg : cms burn info
4. prg : w = Windows()
         r = w.info()
         print(r)
5. find the drive letter
6. prg: drive = device = "Z:"
7: prg: ... mount the drive
8: prg: look if you can find the boot partition on the drive
10: prg: can you list and write things in the boot partition?
11: prg: unmount the drive

12: First task won

TASK 2: do the same as task 1 but with ubuntu on it


TASK 3: FORMAT SD CARD form commandline

9: prg: format the sdcard
'''
