import os
import string
import subprocess
import sys
from pathlib import Path
from pprint import pprint
from pathlib import PurePosixPath

from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile as common_readfile
from cloudmesh.common.util import writefile as common_writefile
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import banner

from cloudmesh.burn.util import os_is_windows

# we need to deal with that imports of windos libraries are conditional

if os_is_windows():
    from ctypes import windll
    import win32api
    import win32wnet
    import win32netcon

import re


def find_entries(data=None, keys=None, value=None):
    results = []
    for entry in data:
        for key in keys:
            if entry[key] == str(value):
                results.append(entry)
    return results

def convert_path(path):
    p = str(PurePosixPath(Path(path)))
    for letter in ["A", "B", "C", "D", "E"]:
        p = p.replace(f"{letter}:\\", "/c")
    return p

class USB:
    @staticmethod
    def info():
        print("Prints the table of information about devices on the  usb info")


class Diskpart:
    tmp = "tmp.txt"

    @staticmethod
    def detail(disk=None):
        detail = {}
        disk = str(disk)
        result = Diskpart.run(f"select disk {disk}\n"
                     "detail disk")
        result = "\n".join(result.strip().splitlines()[7:])
        detail = Diskpart.table_parser(result, kind="Volume")[0]

        info = result.split("Volume ###")[0].strip().split("\n")

        detail["Description"] = info[0]
        for line in info[1:]:
            if ":" in line:
                attribute, value = line.split(":")
                attribute = attribute.strip()
                value = value.strip()
                detail[attribute] = value
        detail["Disk"] = disk
        try:
            detail["Volume"] = detail["###"]
            del detail["###"]
        except:
            pass

        return detail

    @staticmethod
    def remove_drive(letter=None):
        volumes = Diskpart.list_volume()
        found = False
        for volume in volumes:
            if letter in volume["Ltr"]:
                found = True
                number = volume["###"]
                break
        if found:
            result = Diskpart.run(f"select volume {number}\nremove letter={letter}")
            print (result)
        else:
            Console.error(f"Could not remove drive {letter}")

    @staticmethod
    def assingn_drive(letter=None, volume=None):
        result = Diskpart.run(f"select volume {volume}\nassign letter={letter}")
        print (result)



    @staticmethod
    def get_removable_volumes():
        volumes = Diskpart.list_volume()
        result = []
        for volume in volumes:
            if volume["Type"] == "Removable":
                result.append(volume)

        return result

    @staticmethod
    def automount(enable=True):
        if enable:
            result = Diskpart.run(f"automount enable")
        else:
            result = Diskpart.run(f"automount disable")
        # print(result)
        return "enable" in result

    @staticmethod
    def list_device():
        lines = Shell.execute("cat", arguments="/proc/partitions").splitlines()
        headline = lines[0].strip()
        words = re.sub('\s+', ' ', headline.strip()).split(" ")
        lines = lines[1:]
        devices = []
        for line in lines:
            if "sd" not in line:
                continue
            line = line.strip()
            values = re.split("\s+", line)
            values = [value.strip() for value in values]

            data = {
                "major": values[0],
                "minor": values[1],
                "#blocks": values[2],
                "name": values[3],
            }
            if len(values) > 4:
                data["win-mounts"] = values[4][0]
            else:
                data["win-mounts"] = ""

            devices.append(data)

        return devices

    @staticmethod
    def run(command):
        _diskpart = Path("C:/Windows/system32/diskpart.exe")
        common_writefile(Diskpart.tmp, f"{command}\nexit")
        result = Shell.run(f"{_diskpart} /s {Diskpart.tmp}")
        WindowsSDCard.clean()
        # print(result)
        return result

    @staticmethod
    def clean():
        os.remove(Diskpart.tmp)

    @staticmethod
    def table_parser(content=None, kind=None, truncate=2):
        lines = content.splitlines()

        i = 0
        for line in lines:
            if line.strip().startswith(kind):
                break
            i = i + 1
        if truncate > 0:
            lines = lines[i:-truncate]

        headline = lines[0].strip()
        words = re.sub('\\s+', ' ', headline.strip()).split(" ")
        start = []
        end = []
        for word in words:
            start.append(headline.index(word))
        for i in range(0, len(words)):
            try:
                end.append(start[i + 1] - 1)
            except:
                end.append(len(headline))
        data = []
        lines = lines[2:]
        for line in lines:
            line = line.strip()
            entry = {}
            for i in range(0, len(words)):
                try:
                    value = line[start[i]:end[i]].strip()
                except:
                    value = ""
                entry[words[i]] = value.strip()
            data.append(entry)
        return data

    @staticmethod
    def select(disk=None, partition=None, volume=None):
        result = None
        if disk is not None and partition is None and volume is None:
            result = Diskpart.run(f"select disk {disk}")
        elif disk is None and partition is not None and volume is None:
            Diskpart.run(f"select partition {partition}")
        elif disk is None and partition is None and volume is not None:
            Diskpart.run(f"select volume {volume}")
        return result

    @staticmethod
    def list_disk():
        result = Diskpart.run("list disk")
        """
          Disk ###  Status         Size     Free     Dyn  Gpt
          --------  -------------  -------  -------  ---  ---
          Disk 0    Online         1863 GB  1024 KB        *
          Disk 1    No Media           0 B      0 B
          Disk 2    Online           59 GB  1024 KB
        """
        return Diskpart.table_parser(content=result, kind="Disk")

    @staticmethod
    def list_volume():
        result = Diskpart.run("list volume")
        return Diskpart.table_parser(content=result, kind="Volume")

    @staticmethod
    def list_partition(disk=""):
        try:
            result = Diskpart.run(f"select disk {disk}\nlist partition")
            return Diskpart.table_parser(content=result, kind="Partition")
        except:
            return None

    @staticmethod
    def help(command=None):
        if command is None:
            command = ""
        print(Diskpart.run(f"help {command}"))

    @staticmethod
    def get_volume(letter=None, volumes=None):
        if volumes is None:
            volumes = Diskpart.list_volume()
        result = None
        for volume in volumes:
            if volume["Ltr"] == letter:
                return volume
        return result

class WindowsSDCard:
    tmp = "tmp.txt"

    # device will be likely of form Z:/path we need to use Path from new python 3

    def __init__(self, drive=None):
        self.drive = drive

        # if drive is not None:
        #     self.volume = self.drive_to_volume(drive=self.drive)
        #     self.device = self.filter_info(info=self.device_info(), args={"win-mounts": self.drive})[0]
        #     self.device = "/dev/" + self.device["name"][0:3]

    def fix_path(self, path=None):
        path = path.replace(r"\\", "/")
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

    def drive_to_volume(self, drive=None):
        print("entered")
        print(drive)

        return self.filter_info(Diskpart.list_volume(), args={"Ltr": drive})[0]["Volume"]

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

        content = Diskpart.list_volume()
        v = content[0]["Volume"]
        d = content[0]["Ltr"]
        Console.info("Unmounting Card")
        os.system(f"mountvol {drive}: /p")


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

    def online(self, volume=None):
        if volume is not None:
            all_volumes = Diskpart.list_volume()
            matching_volumes = self.filter_info(all_volumes, {"Volume": volume,
                                                              "type": "Removable",
                                                              "status": "Healthy",
                                                              "info": "Offline"})

            if len(matching_volumes) != 0:
                self.diskpart(command=f"select volume {volume}\nonline volume")
                Console.ok(f"Volume {volume} online")
            else:
                Console.error(f"Volume {volume} cannot be brought online")
        else:
            Console.error("Provide valid volume")

    def inject(self):
        Console.ok("Please plug out and in your card")
        user_action = yn_choice("Have you inserted the card?")
        if user_action:
            info = Diskpart.list_volume()
            injected = info[0]["status"] != "No Media"
            if injected:
                Console.ok("Success!")
            else:
                Console.error("Injection failed")
            return injected
        else:
            Console.error("Please plug out and reinsert your card")
            return user_action

    def assign_drive(self, volume=None, drive=None):
        if drive is None:
            drive = self.guess_drive()
        result = self.diskpart(f"select volume {volume}\nassign letter={drive}")
        return result

    def remove_drive(self, volume=None, drive=None):
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

    def mount(self, drive=None, label=None):
        """
        mounts the drive

        :param drive:
        :type drive:
        :return:
        :rtype:
        """
        content = Diskpart.list_volume()
        found = False

        if drive is not None:
            d = drive
            v = -1
            for _drive in content:
                d = _drive["Ltr"]
                v = _drive["Volume"]
                if d == drive:
                    found = True

            if found:
                self.basic_mount(volume_number=v, drive=d)
            else:
                print(Diskpart.list_volume())
                Console.error(f"Mount: Drive letters do not match, Found: {drive}, {d}")
        elif label is not None and drive is None:
            drive = self.guess_drive()
            v = -1
            for _drive in content:
                l = _drive["label"]
                v = _drive["Volume"]
                if l == label:
                    found = True

            if found:
                self.assign_drive(volume=v, drive=drive)
                self.basic_mount(volume_number=v, drive=drive)

            else:
                Console.error(f"Mount: Drive label not found")
        else:
            Console.error("Drive or label not specified")
            return None

    def burn_disk(self, disk=None, image_path=None, blocksize=None, size=None):
        detail = Diskpart.detail(disk=disk)
        drive = detail["Ltr"]
        self.burn_drive(drive=drive, image_path=image_path, blocksize=blocksize, size=size)


    def burn_drive(self, drive=None, image_path=None, blocksize=None, size=None):
        #p = convert_path(image_path)
        p = image_path

        size = Shell.run('stat --print="%s" ' + image_path)

        volumes = self.info_message()

        volume = Diskpart.get_volume(letter=drive, volumes=volumes)


        if volume is None:
            print(Printer.write(
                volume,
                order=['Volume', '###', 'Ltr', 'Label', 'Fs', 'Type', 'Size', 'Status', 'Info', 'name']
                ))

            print()
            Console.error(f"Can not find the drive {drive}")
            print()

        device = volume["name"]
        if device == "":
            Console.error("Drive has no device attached with it")
            return ""

        device = f"/dev/{device}"

        volume = volume["###"]

        banner("Card Info")
        print("Drive:", drive)
        print("Image:", p)
        print("Size: ", size, "Bytes")
        print("Volume:", volume)
        print("Device:", device)
        print()

        # Diskpart.remove_drive(letter=drive)

        if not yn_choice("Is the data correct?"):
            return ""

        command = f'dd bs=4M if="{p}" oflag=direct | ' + \
                  f'tqdm --desc="format" --bytes --total={size} --ncols=80 | ' + \
                  f"dd bs=4M of={device} conv=fdatasync oflag=direct iflag=fullblock"
        print(command)

        file = WindowsSDCard.tmp
        file = "bbb.sh"
        common_writefile(file, command)
        os.system(f"sh {file}")
        banner("assign drive")
        print(drive, volume)
        Diskpart.remove_drive(letter=drive)
        Diskpart.assingn_drive(letter=drive, volume=volume)

    def format_drive(self, disk=None):
        """
        formats the disk with the given number
        :param disk: the disk numner
        :type drive: str
        :return:
        :rtype:
        """

        disks = Diskpart.list_disk()
        entry = find_entries(disks, ["###"], 2)[0]
        number = entry["###"]
        size = entry["Size"]

        details = Diskpart.detail(disk=number)
        print(Printer.attribute(details))

        if not yn_choice(f"Format disk {number} with {size}"):
            return

        command = f"select disk {disk}\n" + \
                     "clean\n" + \
                     "convert mbr\n" + \
                     "create partition primary\n" + \
                     "select partition 1\n" + \
                     "format fs=exfat label=UNTITLED quick"

        Diskpart.run(command)
        return True


    def diskpart(self, command):
        _diskpart = Path("C:/Windows/system32/diskpart.exe")
        common_writefile(WindowsSDCard.tmp, f"{command}\nexit")
        b = Shell.run(f"{_diskpart} /s {WindowsSDCard.tmp}")
        WindowsSDCard.clean()
        return b

    @staticmethod
    def filter_info(info=None, args=None):
        for key, value in args.items():
            info = [device for device in info if key in device.keys() and device[key] == value]
        return info

    def device_info(self):
        # function deprecated use directly Diskpart
        return Diskpart.list_device()

    def disk_info(self):
        # function deprecated use Diskpart directly
        return Diskpart.list_disk()

    def get_disk(self, volume=None, drive=None):
        if volume is not None:
            volume = self.filter_info(info=Diskpart.list_volume(), args={'volume': volume})
            if (len(volume) == 0):
                Console.error("Volume does not exist")
            else:
                r = self.diskpart(f"select volume {volume}\ndetail volume")
                disks = self.process_disks_text(text=r)
                return disks[0]["disk"]

        elif drive is not None:
            volume = self.filter_info(info=Diskpart.list_volume(), args={'drive': drive})
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

    def all_info(self):
        #
        # this may no longer be needed, also we use now the original artttributes from diskpart
        #
        content = self.volume_info()

        # all the fields we wish to display to the user about a device
        empty_info = {"Volume": None, "Ltr": None, "name": None, "fs": None, "label": None, "size": None,
                      "#blocks": None, "major": None, "minor": None, "minor": None, "win-mounts": None}

        # add additional keys to the volume
        for volume in content:
            for key in empty_info:
                if key not in volume:
                    volume[key] = None

        # select info from the first removable volume
        d = content[0]["Ltr"]
        v = content[0]["Volume"]

        results = []
        proc_info = self.device_info()
        for entry in proc_info:
            if "win-mounts" in entry and entry["win-mounts"] == d:
                results.append(entry)

        # add the info from proc info to the content
        for attribute in ["#blocks", "major", "minor", "minor", "name", "name", "win-mounts"]:
            content[0][attribute] = results[0][attribute]

        # return the content to be printed
        return content

    def info_message(self):
        # collect info for all removable volumes
        volumes = Diskpart.list_volume()

        empty = {
            "major": "",
            "minor": "",
            "#blocks": "",
            "name": "",
            "win-mounts": ""
        }
        devices = Diskpart.list_device()
        found = {}
        for device in devices:
            letter = device['win-mounts']
            if letter != "":
                device["name"] = device["name"][:3]
                found[letter] = device
        for volume in volumes:
            volume.update(empty)
            letter = volume['Ltr']
            if letter != "":
                try:
                    values = found[letter]
                    volume.update(values)
                except:
                    Console.error(f"Drive {letter} is not readable")

        # if theres no removable volume, then we cannot proceed
        if len(volumes) == 0:
            Console.error("No removable volume detected!")
            injected = self.inject()
            if not injected:
                Console.error("try again")
                return volumes

        # if there is more than one removable device, ask the user to remove all but target before proceeding
        if len(volumes) > 1:
            Console.error("Too many removable devices found. "
                          "Please remove all except the one for the burn, and rerun")

            #print(Printer.write(
            #    volumes,
            #    order=['Volume', '###', 'Ltr', 'Label', 'Fs', 'Type', 'Size', 'Status', 'Info']
            #))

            return volumes

        # make sure the removable volume is readable
        if volumes[0]["status"] == "No Media":
            result = self.inject()

        # make sure the volume has a drive letter
        if volumes[0]["Ltr"] == "":
            self.assign_drive(volume=volumes[0]["Volume"], drive=self.guess_drive())

        if volumes[0]["status"] != "Healthy":
            print(volumes)
            print(volumes[0]["status"])
            Console.error("Removable device is not healthy")
            return volumes

        if volumes[0]["info"] != "Online":
            Console.ok("Device not online. Attempting to online")
            self.online(volume=volumes[0]["Volume"])

        # Have ensured there is only one removable device, and is readable, has letter, is healthy, and is online

        return self.all_info()

    # def info_fancy(self):
    #     content = self.
    #     d = content[0]["Ltr"]
    #     v = content[0]["Volume"]
    #     if d == "":
    #         d = card.guess_drive()
    #         card.assign_drive(volume=v, drive=d)
    #     print(Printer.write(content, order=["Volume", "Ltr", "fs", "label", "size"]))
    #     if len(content) > 1:
    #         print(Printer.write(content, order=["Volume", "Ltr", "fs", "label", "size"]))
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
    #                         order=["Volume", "Ltr", "fs", "label", "size", "#blocks", "major", "minor", "minor",
    #                                "name", "win-mounts"]))


    def dd(self, image_path=None, device=None):
        command = f"dd bs=4M if={image_path} oflag=direct of={device} conv=fdatasync iflag=fullblock status=progress"
        print(command)
        os.system(command)

    def writefile(self, filename=None, content=None):
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
        content = Diskpart.list_volume()
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
