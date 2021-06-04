from cloudmesh.burn.util import os_is_windows

import string
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile as common_writefile
from cloudmesh.common.util import readfile as common_readfile
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import path_expand
from pathlib import Path
import os
import sys
import string
import subprocess
import re
from pathlib import Path

# we need to deal with that imports of windos libraries are conditional

if os_is_windows():
    from ctypes import windll
    import win32api
    import win32wnet
    import win32netcon


class USB:
    @staticmethod
    def info():
        print("Prints the table of information about devices on the  usb info")


class WindowsSDCard:
    tmp = "tmp.txt"

    # device will be likely of form Z:/path we need to use Path from new python 3

    def __init__(self, drive=None):
        self.drive = drive

        # if drive is not None:
        #     self.volume = self.drive_to_volume(drive=self.drive)
        #     self.device = self.filter_info(info=self.device_info(), args={"win-mounts": self.drive})[0]
        #     self.device = "/dev/" + self.device["name"][0:3]

    def fix_path(self,path=None):
        path = path.replace(r"\\","/")
        return path

    def readfile(self, filename=None):
        content = common_readfile(filename, mode='rb')
        # this may need to be changed to just "r"
        return content

    def writefile(self, filename=None, content=None):
        with open(path_expand(filename), 'w') as outfile:
            outfile.write(content)
            outfile.truncate()  # may not be needed, but is better
            os.fsync(outfile)

    def get_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1

        return drives

    def drive_to_volume(self,drive=None):
        print("entered")
        print(drive)

        return self.filter_info(self.info(),args={"drive":drive})[0]["volume"]

    def diskmanager(self):
        os.system('diskmgmt.msc &')
        # DETACHED_PROCESS = 0x00000008
        #
        # pid = subprocess.Popen([sys.executable, "diskmgmt.msc"],
        #                        creationflags=DETACHED_PROCESS).pid


        # import os
        # os.spawnl(os.P_NOWAIT, 'diskmgmt.msc')


    def automount(self):
        self.diskpart("automount")

    def unmount(self, drive=None):
        """
        unmounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """

        # which is correct
        content = self.info()
        v = content[0]["volume"]
        d = content[0]["drive"]
        Console.info("Unmounting Card")
        os.system(f"mountvol {drive}: /p")

        # b = self.diskpart(f"remove letter={drive}")
        # os.system(f"mountvol {device} /p")

    # def eject(self,volume=None):
    #     if volume is not None:


    @staticmethod
    def guess_drive():
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
            return sorted(drives)[0] + ':'

    def online(self,volume=None):
        if volume is not None:
            all_volumes = self.info()
            matching_volumes = self.filter_info(all_volumes, {"volume": volume,
                                                              "type": "Removable",
                                                              "status": "Healthy",
                                                              "info": "Offline"})

            print(matching_volumes)
            if len(matching_volumes) != 0:
                self.diskpart(command=f"select volume {volume}\nonline volume")
                self.mount(label="UNTITLED")

                Console.ok(f"Volume {volume} online")
            else:
                Console.error(f"Volume {volume} cannot be brought online")
        else:
            Console.error("Provide volume")

    def inject(self):
        info = self.info()
        if(info[0]["status"] == "No Media"):
            Console.ok("Please plug out and in your card")
            return yn_choice("Have you inserted the card?")
        return True


    def assign_drive(self,volume=None,drive=None):
        if drive is None:
            drive = self.guess_drive()
        result = self.diskpart(f"select volume {volume}\nassign letter={drive}")
        return result

    def remove_drive(self,volume=None,drive=None):
        if drive is None:
            drive = self.guess_drive()

        result = self.diskpart(f"select volume {volume}\nremove letter={drive}")

    def basic_mount(self, volume_number=None, drive=None):
        """
        mounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """
        # Figure out drive letter
        # if drive is not None:
        #     volume_letter = self.get_free_drive()
        a = self.diskpart(f"select volume {volume_number}\nassign letter={drive}")
        return drive


    def mount(self, drive=None,label=None):
        """
        mounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """
        content = self.info()
        found = False

        if drive is not None:
            d = drive
            v = -1
            for _drive in content:
                d = _drive["drive"]
                v = _drive["volume"]
                if d == drive:
                    found = True

            if found:
                self.basic_mount(volume_number=v,drive=d)
            else:
                print(self.info())
                Console.error(f"Mount: Drive letters do not match, Found: {drive}, {d}")
        elif label is not None and drive is None:
            drive = self.guess_drive()
            v= -1
            for _drive in content:
                l = _drive["label"]
                v = _drive["volume"]
                if l == label:
                    found = True

            if found:
                self.assign_drive(volume=v,drive=drive)
                self.basic_mount(volume_number=v, drive=drive)

            else:
                Console.error(f"Mount: Drive label not found")
        else:
            Console.error("Drive or label not specified")
            return None


    def burn_drive(self,drive=None,image_path=None,blocksize=None,size=None):
        print(drive)
        self.volume = self.drive_to_volume(drive=drive)

        try:
            self.devName = self.filter_info(self.device_info(), {"win-mounts": drive})[0]
            self.devName = "/dev/" + self.devName["name"][0:3]
        except IndexError as e:
            Console.error("No device with that drive is mounted")

        self.remove_drive(volume=self.volume, drive=drive)
        # command = "DVC_IGNORE_ISATTY=true: "\
        #         "dd bs=4M if=/c/Users/venkata/.cloudmesh/cmburn/images/2021-03-04-raspios-buster-armhf-lite.img oflag=direct |"\
        #         " tqdm --bytes --total 68719441552 --ncols 80 |"\
        #         " dd bs=4M of=/dev/sdb conv=fdatasync oflag=direct iflag=fullblock"


        command =  "dd bs=4M if=/c/Users/venkata/.cloudmesh/cmburn/images/2021-03-04-raspios-buster-armhf-lite.img oflag=direct of=/dev/sdb conv=fdatasync iflag=fullblock status=progress"
        print(command)
        os.system(command)
        # os.environ["DVC_IGNORE_ISATTY"] = "true"
        # image_path = (Path(image_path))
        #
        # #
        # # command = f"dd bs={blocksize} if={image_path} oflag= direct |" \
        # #           f" tqdm --bytes --total {size} --ncols 80 |" \
        # #           f" dd bs={blocksize} of={self.devName} conv=fdatasync oflag=direct  iflag=fullblock"
        #
        # command = "dd"
        # args = f"bs={blocksize} if={image_path}  of={self.devName} conv=fdatasync status=progress"

        # try:
        #     result = subprocess.check_output(
        #     command,
        #     # shell=True,
        #     stderr=subprocess.STDOUT,
        #     cwd=os.getcwd())
        # except subprocess.CalledProcessError as e:
        #     raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        # Shell.execute(cmd=command,arguments=args)
        self.assign_drive(volume=self.volume, drive=drive)
        sys.exit()

    def format_drive(self, drive=None):
        """
        formats the drive
        :param drive: is a drive latte in Windows
        :type drive: str
        :return:
        :rtype:
        """
        content = self.info()
        print(content)
        # d = content[0]["drive"]
        # v = content[0]["volume"]
        # if d == "":
        #     self.inject(volume=v)
        # content = self.info()

        # see https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/format
        command = f"C:\Windows\system32\\format.com {drive}: /FS:EXFAT /V:UNTITLED /Q"
        Console.info("Formatting Card with command: " + command)

        import ctypes
        class disable_file_system_redirection:
            _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
            _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

            def __enter__(self):
                self.old_value = ctypes.c_long()
                self.success = self._disable(ctypes.byref(self.old_value))

            def __exit__(self, type, value, traceback):
                if self.success:
                    self._revert(self.old_value)

        with disable_file_system_redirection():
            command = command.split(" ")
            r = subprocess.run(command)
            print(r.__dict__["returncode"])
            return r.__dict__["returncode"] == 0


    def diskpart(self, command):
        _diskpart = Path("C:/Windows/system32/diskpart.exe")
        common_writefile(WindowsSDCard.tmp, f"{command}\nexit")
        b = Shell.run(f"{_diskpart} /s {WindowsSDCard.tmp}")
        WindowsSDCard.clean()
        return b

    @staticmethod
    def filter_info(info=None, args=None):
        for key,value in args.items():
            info = [device for device in info if key in device.keys() and device[key] == value]
        return info

    def device_info(self):
        r = Shell.execute("cat", arguments="/proc/partitions")
        r = r.splitlines()
        content = []
        for line in r:
            if "sd" in line:
                content.append(line)

        devices = []
        for line in content:
            line = line.strip()
            values = re.split("\s+",line)
            values = [value.strip() for value in values]

            data = {
                "major": values[0],
                "minor": values[1],
                "#blocks": values[2],
                "name": values[3],
            }
            if len(values) > 4:
                data["win-mounts"] = values[4][0]

            devices.append(data)

        return devices


    def disk_info(self):
        r = self.diskpart("list disk")
        disks = self.process_disks_text(text=r)
        return disks

    def process_disks_text(self,text=None):
        if text is None:
            Console.error("No disks provided")
            return None
        else:
            r = text.splitlines()
            content = []
            for line in r:
                if "Disk " in line:
                    content.append(line)
            content = content[1:]

            disks = []
            for line in content:
                data = {
                    "disk": line[0:11].replace("Disk", "").replace("*","").strip(),
                    "status": line[11:26].strip(),
                    "size": line[26:35].strip(),
                    "free": line[35:44].strip(),
                    "dyn": line[44:49].strip(),
                    "gpt": line[49:].strip()
                }
                disks.append(data)
            return disks

    def get_disk(self,volume=None,drive=None):
        if volume is not None:
            volume = self.filter_info(info=self.info(),args={'volume': volume})
            if(len(volume) == 0):
                Console.error("Volume does not exist")
            else:
                r = self.diskpart(f"select volume {volume}\ndetail volume")
                disks = self.process_disks_text(text=r)
                return disks[0]["disk"]

        elif drive is not None:
            volume = self.filter_info(info=self.info(), args={'drive': drive})
            print(volume)
            if (len(volume) == 0):
                Console.error("Drive with given letter does not exist.")
            else:
                r = self.diskpart(f"select volume {drive}\ndetail volume")
                print(r)
                disks = self.process_disks_text(text=r)
                return disks[0]["disk"]
        else:
            Console.error("Provide volume or drive to get disk")

    def info(self):

        """
        Prints information about the USB and sdcard if it is available

        :return:
        :rtype:
        """
        empty = {"volume": None, "drive": None, "fs": None, "label": None, "size": None, "#blocks":None, "major": None,
                 "minor": None, "minor": None, "name": None, "win-mounts": None}
        b = self.diskpart("list volume")
        volumes = self.process_volumes_text(text=b)
        print("aaa",volumes)
        if volumes[0]["drive"] == 0:
            check = self.inject()
            if not check:
                return [empty]


        for volume in volumes:
            for key in empty:
                if key not in volume:
                    volume[key] = None

        content = volumes
        print("bbb",content)
        d = content[0]["drive"]
        v = content[0]["volume"]
        if d == "":
            d = self.guess_drive()
            self.assign_drive(volume=v, drive=d)
        if len(content) > 1:
            Console.error("Too many removable USB devices found")
            return content
        # TODO
        results = []
        proc_info = self.device_info()
        for entry in proc_info:
            if "win-mounts" in entry and entry["win-mounts"] == d:
                results.append(entry)
        for attribute in ["#blocks", "major", "minor", "minor", "name", "name", "win-mounts"]:
            content[0][attribute] = results[0][attribute]
        # content = card.diskinfo(number=)
        # print(content)

        return content



    # def info_fancy(self):
    #     content = self.
    #     d = content[0]["drive"]
    #     v = content[0]["volume"]
    #     if d == "":
    #         d = card.guess_drive()
    #         card.assign_drive(volume=v, drive=d)
    #     print(Printer.write(content, order=["volume", "drive", "fs", "label", "size"]))
    #     if len(content) > 1:
    #         print(Printer.write(content, order=["volume", "drive", "fs", "label", "size"]))
    #         Console.error("Too many removable USB devices found")
    #         return ""
    #     # TODO
    #     results = []
    #     proc_info = card.device_info()
    #     for entry in proc_info:
    #         if "win-mounts" in entry and entry["win-mounts"] == d:
    #             results.append(entry)
    #     for attribute in ["#blocks", "major", "minor", "minor", "name", "win-mounts"]:
    #         content[0][attribute] = results[0][attribute]
    #     # content = card.diskinfo(number=)
    #     # print(content)
    #     print(Printer.write(content,
    #                         order=["volume", "drive", "fs", "label", "size", "#blocks", "major", "minor", "minor",
    #                                "name", "win-mounts"]))


    def process_volumes_text(self,text=None):
        if text is None:
            Console.error("No volume info provided")
        else:
            lines = text.splitlines()
            result = []
            for line in lines:
                if "Removable" in line and "Healthy" in line:
                    result.append(line)

            content = []
            for line in result:
                data = {

                    "volume": line[0:13].replace("Volume", "").strip(),
                    "drive": line[13:18].strip(),
                    "label": line[18:31].strip(),
                    "fs": line[31:38].strip(),
                    "type": line[38:50].strip(),
                    "size": line[50:59].strip(),
                    "status": line[59:70].strip(),
                    "info": line[70:].strip()

                }
                content.append(data)

            return content

    def dd(self,image_path=None,device=None):
        command = f"dd bs=4M if={image_path} oflag=direct of={device} conv=fdatasync iflag=fullblock status=progress"
        print(command)
        os.system(command)

    def writefile(self,filename=None,content=None):
        with open(filename, 'w') as outfile:
            outfile.write(content)
            outfile.truncate()


        # command = f"mountvol {self.drive} /L"
        # r = Shell.run(command)
        # print (r)
        # see also gregos implementation for mac, osx, and raspberry,
        # that just may work

        # diskpart list disk
        # diskpart detail disk
        # diskpart detail volume

        # diskpart /s <script_file>

        # os.system("diskpart list disk")

        # Path pathlib
        # filename = Path("/tmp/list-disk.txt")

        # common_writefile(filename, "list disk\n\exit")
        # os.system(f"diskpart /s {filename}")

    def ls(self):
        content = self.info()
        return content

    @staticmethod
    def clean():
        os.remove(WindowsSDCard.tmp)

    # @staticmethod
    # def list_file_systems():


"""
class WindowsSDCard:
    
    tmp = "tmp.txt"

    @staticmethod
    def clean():
        raise NotImplementedError
        # rm SDCard.tmp

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

        common_writefile(SdCard.tmp, f"select disk {disk_number} \n exit")
        
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

        print(a)

        common_writefile(SdCard.tmp, f"select volume {volume_number}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")
        print(SdCard.tmp)
        print(a)

        common_writefile(SdCard.tmp, "format fs=fat32 quick")
        print(SdCard.tmp)
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

    @staticmethod
    def mount(volume_number, volume_letter=None):
        if volume_letter == None:
            volume_letter = SdCard.get_free_drive()
        common_writefile(SdCard.tmp, f"select volume {volume_number}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")

        common_writefile(SdCard.tmp, f"assign letter={volume_letter}")
        a = Shell.run(f"diskpart /s {SdCard.tmp}")
        return volume_letter

    @staticmethod
    def unmount(volume_letter):
        common_writefile(SdCard.tmp, f"remove letter={volume_letter}")
        b = Shell.run(f"diskpart /s {SdCard.tmp}").splitlines()[8:]

        # os.system(f"mountvol {device} /p")

        print(b)

    @staticmethod
    def write(volume_number, volume_letter):
        pass

    @staticmethod
    def info():
        print("Disk info")
        common_writefile(SdCard.tmp, "list volume")
        b = Shell.run(f"diskpart /s {SdCard.tmp}").splitlines()[8:]
        return b

    @staticmethod
    def get_free_drive():
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


SdCard.format_card(5, 3)
"""

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
