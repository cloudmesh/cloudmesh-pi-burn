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

    def __init__(self):
        self.vendors = None

    def get_product(self, vendor, product):
        try:
            return self.vendors[vendor][product]
        except:
            return "unkown"

    def load_vendor_description(self):
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
            except:
                pass
        self.vendors = data
        return data

    def get_vendor(self):
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
        return glob.glob("/dev/sd?")

    @staticmethod
    def fdisk(dev):
        return subprocess.getoutput(f"sudo fdisk -l {dev}")

    @staticmethod
    def get_from_usb():

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
        lsusb = subprocess.getoutput("lsusb").splitlines()
        all = {}
        for line in lsusb:
            line = line.replace("Bus ", "")
            line = line.replace("Device ", "")
            line = line.replace("ID ", "")
            line = line.replace(":", "", 1)
            line = line.replace(":", " ", 1)
            content = line.split(" ")
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

        return all

    @staticmethod
    def get_from_dmesg():

        lines = subprocess.getoutput("dmesg -t").splitlines()

        details = {}
        for line in lines:
            if line.startswith("scsi") and "Direct-Access" in line:
                sdci, key, what = line.split(" ", 2)
                comment = line.split("Direct-Access")[1].strip()
                what = " ".join(comment.split("  ")[:2])
                try:
                    details[key] = {}
                except:
                    pass
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
                name = details[key]["name"] = device.replace("[", "").replace(
                    "]", "")
                dev = details[key]["dev"] = f"/dev/{name}"
                _fdisk = USB.fdisk(name)
                details[key]['readable'] = "cannot open" in _fdisk
                details[key]['empty'] = "linux" in _fdisk
                details[key]['formatted'] = "FAT32" not in _fdisk
        # remove opbets without size

        found = []
        for name in details:
            entry = details[name]
            if 'size' in list(entry.keys()):
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
