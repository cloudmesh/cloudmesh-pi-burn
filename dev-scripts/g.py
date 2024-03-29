import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile
from cloudmesh.common.util import yn_choice
import sys
import string
import win32api
import win32wnet
import win32netcon
import subprocess
import textwrap
from cloudmesh.common.Tabulate import Printer
from pathlib import Path

class USB:
    @staticmethod
    def info():
        print("Prints the table of information about devices on the  usb info")


'''
    diskpart commands - 
    https://www.windowscentral.com/how-mount-drive-windows-10#:~:text=Unmount%20drive%20with%20DiskPart&text=using%20these%20steps%3A-,Open%20Start.,Run%20as%20administrator**%20option.&text=Confirm%20the%20volume%20you%20want%20to%20unmount.&text=volume%20VOLUME%2DNUMBER-,In%20the%20command%2C%20replace%20VOLUME%2DNUMBER%20with%20the%20number%20of,volume)%20you%20want%20to%20mount.
    https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-xp/bb490893(v=technet.10)?redirectedfrom=MSDN
'''
class SdCard:
    tmp = "tmp.txt"

    @staticmethod
    def clean():
        # rm SDCard.tmp
        os.remove(SdCard.tmp)

    # Take a look at Gregor's SDCard init method
    @staticmethod
    def format_card(volume_number, disk_number):

        '''
        # see https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/format
        if unmount:
            set_unmount = "/x"
        else:
            set_unmount = ""
        command = f"format {device} /fs:FAT32 /v:UNTITLED /q {set_unmount}".strip()
        print(command)
        '''

        print(f"format :{volume_number}")
        script = textwrap.dedent(f"""
        select disk {disk_number}
        select volume {volume_number}
        format fs=fat32 quick
        """)

        try:
            a = SdCard.diskpart(script)
        except Exception as e:
            print(e)



    @staticmethod
    def mount(volume_number, volume_letter=None):
        #Figure out drive letter
        if volume_letter == None:
            volume_letter = SdCard.get_free_drive()
        a = SdCard.diskpart(f"select volume {volume_number}\nassign letter={volume_letter}")
        return volume_letter

    @staticmethod
    def unmount(volume_letter):
        b = SdCard.diskpart(f"remove letter={volume_letter}")
        # os.system(f"mountvol {device} /p")

        print(b)

    @staticmethod
    def write(volume_number, volume_letter):
        pass

    @staticmethod
    def sync(drive_letter):
        os.system(f"sync -r {drive_letter}")

    @staticmethod
    def eject(drive_letter):
        os.system(f"sync -e {drive_letter}")

    @staticmethod
    def diskpart(command):
        _diskpart = Path("C:/Windows/system32/diskpart.exe")
        writefile(SdCard.tmp, f"{command}\nexit")
        b = Shell.run(f"{_diskpart} /s {SdCard.tmp}")
        SdCard.clean()
        return b

    @staticmethod
    def info():
        print("Disk info")
        b = SdCard.diskpart("list volume")

        lines = b.splitlines()
        result = []
        for line in lines:
            if "Removable" in line and "Healthy" in line:
                result.append(line)

        info = []
        for line in result:
            data = {

                "volume" : line[0:13].replace("Volume", "").strip(),
                "drive"  : line[13:18].strip(),
                "label"  : line[18:31].strip(),
                "fs"     : line[31:38].strip(),
                "type"   : line[38:50].strip(),
                "size"   : line[50:59].strip(),
                "status" : line[59:70].strip(),

            }
            info.append(data)

        return info



    @staticmethod
    def get_free_drive():
        """

        """
        drives = set(string.ascii_uppercase[2:])
        for d in win32api.GetLogicalDriveStrings().split(':\\\x00'):
            drives.discard(d)
        # Discard persistent network drives, even if not connected.
        henum = win32wnet.WNetOpenEnum(win32netcon.RESOURCE_REMEMBERED,
                                       win32netcon.RESOURCETYPE_DISK, 0, None)
        while True:
            result = win32wnet.WNetEnumResource(henum)
            if not result:
                break
            for r in result:
                if len(r.lpLocalName) == 2 and r.lpLocalName[1] == ':':
                    drives.discard(r.lpLocalName[0])
        if drives:
            return sorted(drives)[-1] + ':'

    @staticmethod
    def guess_volume_number():
        r = SdCard.info()
        print(r)
        for line in r:
            line = line.strip()
            if "*" not in line:
                line = line.replace("No Media", "NoMedia")
                line = line.replace("Disk ", "")
                line = ' '.join(line.split())
                num, kind, size, unit, unused1, unused2 = line.split(" ")
                size = int(size)

                if unit == "GB" and (size > 7 and size < 128):
                    return num
        raise ValueError("No SD card found")

# SdCard.format_card(5, 3)
info = SdCard.info()

print(Printer.write(info, order=["volume", "drive", "fs", "label", "size"]))

'''
DO NOT DELETE THIS COMMENT - WORKING CODE HERE. 

r = SdCard.info()
print(r)
volume_number = SdCard.guess_volume_number()

if not yn_choice (f"Would you like to contine burning on disk {volume_number}"):
    sys.exit(0)

volume_letter = SdCard.mount(volume_number)

from glob import glob

files = glob(f"{volume_letter}:")

print(files)

SdCard.unmount(volume_letter)
'''






