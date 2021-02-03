import glob
import os
import subprocess

import requests
import usb

from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


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

    def get_product(self, vendor, product):
        """
        internal method used to retrive the vendor, product string
        :param vendor: the vendor name
        :type vendor: str
        :param product: the product name
        :type product: str
        :return: the vendor product string
        :rtype: str
        """
        try:
            return self.vendors[vendor][product]
        except Exception as e:
            return "unkown"

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
        content = self.get_vendor().splitlines()
        for line in content:
            try:
                if line.startswith("#") or line.startswith("]") or line is None:
                    pass
                elif line.startswith("\t"):
                    product_id, product = line.strip().split(" ", 1)
                    print(vendor_id, product_id, product)
                    data[vendor_id][product_id] = {
                        'vendor_id': vendor_id,
                        'product_id': product_id,
                        'vendor': vendor,
                        'product': product
                    }
                else:
                    vendor_id, vendor = line.strip().split(" ", 1)
                    data[vendor_id] = {}
            except Exception as e:
                pass
        self.vendors = data
        return data

    def get_vendor(self):
        """
        Retrives the names of vendors from linux-usb.org

        :return: the content of the file
        :rtype: str
        """
        filename = 'usb.ids'

        if not os.path.isfile(filename):
            r = requests.get(f'http://www.linux-usb.org/{filename}')
            content = r.text
            writefile(filename, content)
        else:
            content = readfile('usb.ids')
        return content

    @staticmethod
    def get_devices():
        """
        finds all devices starting with /dev/sd?

        :return: list
        :rtype: list of devices
        """
        return glob.glob("/dev/sd?")

    @staticmethod
    def fdisk(dev):
        """
        calls fdosk on the specified device

        :param dev: device, example /dev/sdz
        :type dev: str
        :return: the output from the fdisk command
        :rtype: str
        """
        return subprocess.getoutput(f"sudo fdisk -l {dev}")

    @staticmethod
    def get_from_usb():
        """
        TODO: explain differnce to get_from_lsusb

        Finds the information about attached USB devices from lsusb
        Attributes of the devices found include

            'comment'
            "hVendor"
            "hProduct"
            "serach"

        :return: list of dicts
        :rtype: list
        """

        #
        # in future we also look up the vendor
        #
        # v = USB()
        # v.load_vendor_description()

        # pprint (v.vendors)

        def h(d, a):
            v = hex(d[a])
            return v.replace("0x", "0")

        lsusb = USB.get_from_lsusb()
        busses = usb.busses()

        details = []
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                data = dev.__dict__
                data.update(dev.dev.__dict__)
                data['comment'] = lsusb[f"{dev.bus}-{dev.address}"]["comment"]
                del data['configurations']
                data["hVendor"] = h(data, "idVendor")
                data["hProduct"] = h(data, "idProduct")
                data["serach"] = "tbd"
                details.append(data)
        return details

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

        all = {}
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
                all[f"{bus}-{addr}"] = data
            except Exception as e:
                pass

        return all

    @staticmethod
    def get_from_dmesg(pluggedin=True):
        """
        Get information for USB and other direct attached devices from
        dmsg. It includes information such if the device is readable or writable,
        and if a card is formatted with FAT32.

        :param pluggedin: Only listed the plugged in USB devices
        :type pluggedin: bool
        :return: list of dicts
        :rtype: lits of dicts
        """

        lines = subprocess.getoutput("dmesg -t").splitlines()

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
                    details[key]["removable"] = True
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
                dev = details[key]["dev"] = f"/dev/{name}"
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

        '''
        # print (devices)
        details = []
        for device in devices:
            name = os.path.basename(device)
            dmesg = result = subprocess.getoutput(command)
            _fdisk = USB.fdisk(name)
            result = result.replace("Write Protect is", "write_protection:")
            result = result.replace("Attached SCSI removable disk",
                                    "removable_disk: True")
            result = result.replace("(", "")
            result = result.replace(")", "")
            result = result.splitlines()
            _dmesg = [x.split(f"[{name}]", 1)[1].strip() for x in result]
            size = _get_attribute("logical blocks:", _dmesg)
            if size is not None:
                details.append({
                    'dmesg': dmesg,
                    'fdisk': _fdisk,
                    'name': name,
                    'dev': device,
                    'removable_disk': _get_attribute("removable_disk:", _dmesg),
                    'write_protection': \
                        _get_attribute("write_protection:",
                                       _dmesg) is not "off",
                    'size': size,
                    
                })
        return details
        '''
