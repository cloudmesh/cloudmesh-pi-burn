import glob
import os
import subprocess

import humanize
import requests

import usb as usb_device
from cloudmesh.burn.util import os_is_mac
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.sudo import Sudo
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


# from cloudmesh.burn.util import os_is_linux
# from cloudmesh.burn.util import os_is_pi


def _get_attribute(attribute, lines):
    for line in lines:
        if attribute in line:
            return line.split(attribute, 1)[1].strip()
    return None


class USB(object):
    """
    Class to make interacting with USB devices such as SDCard writers easier.
    """

    def __init__(self):
        self.vendors = None

    # noinspection PyBroadException
    def get_product(self, vendor=None, product=None):
        """
        internal method used to retrieve the vendor, product string
        :param vendor: the vendor name
        :type vendor: str
        :param product: the product name
        :type product: str
        :return: the vendor product string
        :rtype: str
        """
        try:
            return self.vendors[vendor][product]
        except Exception as e:  # noqa: F841
            return "unkown"

    # noinspection PyBroadException
    def load_vendor_description(self):
        """
        Creates a dict from the usb devices that are detected.
        Attributes for each entry include

            'vendor_id'
            'product_id'
            'vendor'
            'product'

        :return: a dict of vendor specifications for the USB devices
        :rtype: dict
        """
        self.get_vendor()
        data = {}
        product_id = None
        vendor_id = None
        vendor = None
        content = self.get_vendor().splitlines()
        for line in content:
            try:
                other_devices = ['C', 'AT', 'HID', 'R', 'BIAS', 'PHY', 'HUT',
                                 'L', 'HCC', 'VT']
                other_dev = False
                for dev in other_devices:
                    if line.startswith(dev):
                        other_dev = True

                first_word = line.strip().split()[0]

                if line.startswith("#") or line.startswith("]") or line is None or other_dev:
                    continue
                elif not line.startswith("\t") and len(first_word) == 4:
                    vendor_id, vendor = line.strip().split(" ", 1)
                    data[vendor_id] = {}
                elif line.startswith("\t") and len(first_word) == 4:
                    product_id, product = line.strip().split(" ", 1)
                    data[vendor_id][product_id] = {
                        'vendor_id': vendor_id,
                        'product_id': product_id,
                        'vendor': vendor,
                        'product': product
                    }

            except:  # noqa: E722
                pass
        self.vendors = data
        return data

    def get_vendor(self):
        """
        Retrieves the names of vendors from linux-usb.org

        :return: the content of the file
        :rtype: str
        """
        filename = 'usb.ids'
        full_path = path_expand(f"~/.cloudmesh/cmburn/{filename}")
        if not os.path.isfile(full_path):
            r = requests.get(f'http://www.linux-usb.org/{filename}')
            content = r.text
            writefile(full_path, content)
        else:
            content = readfile(full_path)
        return content

    @staticmethod
    def get_devices():
        """
        finds all devices starting with /dev/sd?

        :return: list
        :rtype: list of devices
        """
        if os_is_mac():
            return glob.glob("/dev/disk?")
        else:
            return glob.glob("/dev/sd?")

    @staticmethod
    def fdisk(dev):
        """
        calls fdisk on the specified device

        :param dev: device, example /dev/sdz
        :type dev: str
        :return: the output from the fdisk command
        :rtype: str
        """
        if os_is_mac():
            raise NotImplementedError("fdisk -l not supported on MacOS")
        else:
            Sudo.password()
            return subprocess.getoutput(f"sudo fdisk -l {dev}")

    # noinspection PyBroadException,PyBroadException
    @staticmethod
    def get_from_usb():
        """
        TODO: explain difference to get_from_lsusb

        Finds the information about attached USB devices from lsusb
        Attributes of the devices found include

            'comment'
            "hVendor"
            "hProduct"
            "search"

        :return: list of dicts
        :rtype: list
        """
        try:
            v = USB()
            v.load_vendor_description()
        except:  # noqa: E722
            pass

        def h(d, a):
            v = hex(d[a])
            return v.replace("0x", "0")

        lsusb = USB.get_from_lsusb()
        if len(lsusb) == 0:
            Console.warning("We could not find your USB reader in the list of known readers")
            return None
        busses = usb_device.busses()

        details = []
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                data = dev.__dict__
                data.update(dev.dev.__dict__)
                data['comment'] = lsusb[f"{dev.bus}-{dev.address}"]["comment"]
                del data['configurations']
                try:
                    vendor = f'{data["idVendor"]:04x}'
                    product = f'{data["idProduct"]:04x}'
                    vendor_str = v.vendors[vendor][product]['vendor']
                    device_str = v.vendors[vendor][product]['product']
                    data["hVendor"] = vendor_str
                    data["hProduct"] = device_str
                except:  # noqa: E722
                    data["hVendor"] = h(data, "idVendor")
                    data["hProduct"] = h(data, "idProduct")
                data["search"] = "tbd"
                details.append(data)
        return details

    # noinspection PyBroadException
    @staticmethod
    def get_from_lsusb():
        """
        Gets information about USB devices from lsusb. Attributes include

            'bus'
            'addr'
            'ivendor'
            'iproduct'
            'vendor'
            'product'
            'comment'

        :return: list of dicts
        :rtype: list of dicts
        """
        lsusb = subprocess.getoutput("lsusb").splitlines()

        found = {}
        for line in lsusb:
            line = line.replace("Bus ", "")
            line = line.replace("Device ", "")
            line = line.replace("ID ", "")
            line = line.replace(":", "", 1)
            line = line.replace(":", " ", 1)
            content = line.split(" ")

            try:
                bus = int(content[0])
                addr = int(content[1])

                data = {
                    'bus': bus,
                    'addr': addr,
                    'ivendor': int(content[2], 16),
                    'iproduct': int(content[3], 16),
                    'vendor': content[2],
                    'product': content[3],
                    'comment': ' '.join(content[4:])
                }
                found[f"{bus}-{addr}"] = data
            except Exception as e:  # noqa: F841
                pass

        return found

    # noinspection PyBroadException
    @staticmethod
    def get_from_dmesg(pluggedin=True):
        """
        Get information for USB and other direct attached devices from
        dmsg. It includes information such if the device is readable or writable,
        and if a card is formatted with FAT32.

        :param pluggedin: Only listed the plugged in USB devices
        :type pluggedin: bool
        :return: list of dicts
        :rtype: list of dicts
        """
        try:
            lines = subprocess.getoutput("dmesg -t").splitlines()
        except:
            return None

        details = {}
        for line in lines:
            if line.startswith("scsi") and "Direct-Access" in line:
                sdci, key, what = line.split(" ", 2)
                comment = line.split("Direct-Access")[1].strip()
                what = " ".join(comment.split("  ")[:2])
                if key not in details:
                    details[key] = {}
                details[key]["key"] = key
                details[key]["direct-access"] = True
                details[key]["info"] = what
                device, a, b, bus, rest = key.split(":")
                details[key]["device"] = device
                details[key]["bus"] = bus

            elif line.startswith("sd") and " sg" in line:
                sg = line.split(" sg")[1].split(" ", 1)[0]
                details[key]["sg"] = sg

            elif line.startswith("sd") and "] " in line:
                prefix, key, device, comment = line.split(" ", 3)
                if key not in details:
                    details[key] = {}
                details[key]["key"] = key
                if "Attached SCSI removable disk" in comment:
                    try:
                        details[key]["removable"] = True
                    except:  # noqa: E722
                        details[key]["removable"] = False
                if "logical blocks:" in comment:
                    size = comment.split("blocks:")[1]
                    details[key]["size"] = size.strip().replace("(",
                                                                "").replace(")",
                                                                            "")
                if "Write Protect is" in comment:
                    details[key]["writeable"] = "off" in comment
                else:
                    details[key]["writeable"] = True
                name = details[key]["name"] = device.replace("[", "").replace(
                    "]", "")
                # TODO:
                # This line was commented out previously, causing the program to fail. Why was this done?
                details[key]["dev"] = f"/dev/{name}"
                _fdisk = USB.fdisk(name)
                details[key]['readable'] = "cannot open" in _fdisk
                details[key]['empty'] = "linux" in _fdisk
                details[key]['formatted'] = "FAT32" not in _fdisk
                details[key]['active'] = os.path.exists(details[key]['dev'])
        # remove opbets without size

        found = []
        for name in details:
            entry = details[name]
            if 'size' in list(entry.keys()) and (entry['active'] or not pluggedin):
                found.append(entry)

        return found

    @staticmethod
    def check_for_readers():
        if os_is_mac():
            readers = USB.get_dev_from_diskutil()
            if len(readers) == 0:
                print()
                Console.error("Please make sure the reader and the SDCard "
                              "are properly inserted")
                raise ValueError("No card found")
            elif len(readers) > 1:
                print()
                Console.error("At this time we only support one SDCard "
                              "reader/writer for MacOS")
                raise ValueError("Too many cards found")

    @staticmethod
    def get_dev_from_diskutil():
        if os_is_mac():
            import plistlib
            external = subprocess.check_output("diskutil list -plist external".split(" "))

            r = dict(plistlib.loads(external))

            details = []

            if len(r['AllDisksAndPartitions']) == 0:
                Console.error("No partition found")
                return ""

            else:
                for dev in r['AllDisksAndPartitions']:
                    details.append(dev['DeviceIdentifier'])
                return details
        else:
            return None

    @staticmethod
    def get_from_diskutil(device=None):
        import plistlib
        external = subprocess.check_output("diskutil list -plist external".split(" "))

        r = dict(plistlib.loads(external))

        details = []

        if len(r['AllDisksAndPartitions']) == 0:
            Console.error("No partition found")
            return ""

        no = 0
        for cards in r['AllDisksAndPartitions']:

            try:
                for partition in r['AllDisksAndPartitions'][no]['Partitions']:
                    if 'MountPoint' not in partition:
                        partition['MountPoint'] = None
                    if partition['Content'] == 'Linux':
                        partition['Content'] = 'ext4'
                    elif partition['Content'] == 'Windows_FAT_32':
                        partition['Content'] = 'FAT32'

                    info = partition['MountPoint']
                    entry = {
                        "dev": f"/dev/{partition['DeviceIdentifier']}",
                        "active": info is not None,
                        "info": info,
                        "readable": info is not None,
                        "formatted": partition['Content'],
                        "empty": partition['Size'] == 0,
                        "size": humanize.naturalsize(partition['Size']),
                        "direct-access": True,
                        "removable": True,
                        "writeable": 'VolumeName' in partition
                    }
                    if device is None or device in entry["dev"]:
                        details.append(entry)
                no = no + 1
            except KeyError as e:  # noqa: F841
                Console.warning("No partitions found for device")
                partition = r['AllDisksAndPartitions'][no]
                entry = {
                    "dev": f"/dev/{partition['DeviceIdentifier']}",
                    "active": False,
                    "info": "Not Formatted",
                    "readable": False,
                    "formatted": False,
                    "empty": partition['Size'] == 0,
                    "size": partition['Size'],
                    "direct-access": True,
                    "removable": True,
                    "writeable": 'VolumeName' in partition
                }
                details.append(entry)

        return details

    @staticmethod
    def print_details(details, order=None, header=None, output="table"):
        if order is None:
            order = ["dev",
                     "info",
                     "formatted",
                     "size",
                     "active",
                     "readable",
                     "empty",
                     "direct-access",
                     "removable",
                     "writeable"
                     ],
        if header is None:
            header = ["Path",
                      "Info",
                      "Formatted",
                      "Size",
                      "Plugged-in",
                      "Readable",
                      "Empty",
                      "Access",
                      "Removable",
                      "Writeable"
                      ],
        # print(Printer.write(details, order=order, header=header, output=output))
        print(Printer.write(details, order=order[0], header=header[0]))
