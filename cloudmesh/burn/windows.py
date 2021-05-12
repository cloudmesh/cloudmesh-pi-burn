import string
from ctypes import windll
import ascii
from cloudmesh.common.Shell import Shell

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
