#!/usr/bin/env python

"""
Cloudmesh Raspberry Pi Image Burner.

Usage:
  cm-pi-burn create [--image=IMAGE] [--device=DEVICE] [--hostname=HOSTNAME] [--ipaddr=IP] [--sshkey=KEY]
  cm-pi-burn burn [IMAGE] [DEVICE]
  cm-pi-burn mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn set hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn set ip [IP] [MOUNTPOINT]
  cm-pi-burn set key [KEY] [MOUNTPOINT]
  cm-pi-burn enable ssh [MOUNTPOINT]
  cm-pi-burn unmount [DEVICE]
  cm-pi-burn image versions
  cm-pi-burn image ls
  cm-pi-burn image delete [IMAGE]
  cm-pi-burn image get [URL]
  cm-pi-burn (-h | --help)
  cm-pi-burn --version

Options:
  -h --help           Show this screen.
  --version           Show version.
  --image=IMAGE       The image filename, e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE     The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME The hostname
  --ipaddr=IP         The IP address
  --key=KEY           The name of the SSH key file [default: id_rsa]

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
    Location where the images will be stored for reuse

Description:
  cm-pi-burn

Example:
  cm-pi-burn create --image=2019-09-26-raspbian-buster-lite --device=/dev/mmcblk0
                    --hostname=red[5-7] --ipaddr=192.168.1.[5-7] --key=id_rsa
  cm-pi-burn.py image get latest
  cm-pi-burn.py image delete 2019-09-26-raspbian-buster-lite
  cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
"""

import os
import wget
import hostlist
from docopt import docopt
from pprint import pprint
import requests
from pathlib import Path
import sys
import zipfile
from glob import glob
import requests

debug = True

try:
    columns, lines = os.get_terminal_size()
except:
    columns = 80
    lines = 24

# noinspection PyPep8Naming
def WARNING(*args, **kwargs):
    print("WARNING:", *args, file=sys.stderr, **kwargs)

#
# Example image link
#
# https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip

class Image(object):

    def __init__(self, name="latest"):
        self.directory = os.path.expanduser('~/.cloudmesh/images')
        os.system('mkdir -p ' + self.directory)
        self.image_name = name

    def versions(self, repo):
        # image locations
        #
        # https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/

        #
        # versions can be found with https://downloads.raspberrypi.org/raspbian_lite/images/
        #

        result = requests.get(repo)
        lines = result.text.split(' ')
        d = []
        v = []
        for line in lines:
            if 'href="' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('/')[0]
                v.append(line)
                download = self.find_image_zip(line)
                d.append(download)
        return v, d

    def find_image_zip(self, version):

        url = f"https://downloads.raspberrypi.org/raspbian_lite/images/{version}/"

        result = requests.get(url)
        lines = result.text.split(' ')
        v = []
        for line in lines:
            if '.zip"' in line and "</td>" in line:
                line = line.split('href="')[1]
                line = line.split('"')[0]
                link = f"https://downloads.raspberrypi.org/raspbian_lite/images/{version}/{line}"
                return link
        return None

    def fetch(self):
        latest = False
        if self.image_name == 'latest':
            latest = True
            self.image_name = "https://downloads.raspberrypi.org/raspbian_lite_latest"
        debug = True

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        os.chdir(self.directory)
        # find redirectionlink
        source_url = requests.head(self.image_name, allow_redirects=True).url
        size = requests.get(self.image_name, stream=True).headers['Content-length']
        zip_filename = os.path.basename(source_url)
        img_filename = zip_filename.replace('.zip', '.img')

        if os.path.exists(img_filename):
            WARNING("file already downloaded. Found at:",
                    Path(Path(self.directory) / Path(zip_filename)))
            return

        img_file = Path(Path(self.directory) / Path(img_filename))
        if os.path.isfile(img_file):
            WARNING("file already downloaded. Found at:",
                    Path(Path(self.directory) / Path(zip_filename)))
            return

        wget.download(self.image_name)
        print()
        if latest:
            Path('raspbian_lite_latest').rename(zip_filename)

        self.unzip_image(zip_filename)
        Path(zip_filename).unlink()

    def unzip_image(self, zip_filename):
        os.chdir(self.directory)
        img_filename = zip_filename.replace('.zip', '.img')
        zipfile.ZipFile(zip_filename).extractall()

    def verify(self):
        # verify if the image is ok, use SHA
        raise NotImplementedError

    def rm(self):
        # remove the downloaded image
        Path(Path(self.directory) / Path(self.image_name + '.img')).unlink()

    def ls(self):
        images_dir = Path(self.directory)
        images = [str(x).replace(self.directory + '/', '').replace('.img', '') for x in images_dir.glob('*.img')]
        print('Available images')
        print(columns * '=')
        print('\n'.join(images))

class Burner(object):

    @staticmethod
    def burn(image, device):
        """
        burns the SD Card
        :param image: name of the image
        """
        os.system('sudo cat ' + image + ' >' + device)

    @staticmethod
    def set_hostname(hostname, mountpoint):
        """
        sets the hostname on the sd card
        :param hostname:
        """
        # write the new hostname to /etc/hostname
        with open(mountpoint + '/etc/hostname', 'w') as f:
            f.write(hostname + '\n')

        # change last line of /etc/hosts to have the new hostname
        # 127.0.1.1 raspberrypi   # default
        # 127.0.1.1 red47         # new
        with open(mountpoint + '/etc/hosts', 'r') as f: # read /etc/hosts
            lines = [l for l in f.readlines()][:-1] # ignore the last line
            newlastline = '127.0.1.1 ' + hostname + '\n'

        with open(mountpoint + '/etc/hosts', 'w') as f: # and write the modified version
            for line in lines:
                f.write(line)
            f.write(newlastline)

    @staticmethod
    def set_static_ip(ip, mountpoint):
        """
        Sets the static ip on the sd card
        :param ip:
        """
        with open(mountpoint + '/etc/hosts') as f:
            lines = [l for l in f.readlines()]
        with open(mountpoint + '/etc/hosts', 'w') as f:
            for line in lines:
                f.write(line)
            f.write('interface eth0\n')
            f.write('static ip_address=' + ip + '/24')

    @staticmethod
    def set_key(name, mountpoint):
        """
        copies the public key into the .ssh/authorized_keys file on the sd card
        """
        # name should be something like 'id_rsa'
        os.system('cp ~/.ssh/' + name + '.pub ' + mountpoint + '/home/pi/.ssh/authorized_keys')

    @staticmethod
    def mount(device, mountpoint):
        """
        mounts the current SD card
        """
        os.system('sudo rmdir ' + mountpoint)
        os.system('sudo mkdir ' + mountpoint)
        os.system('sudo mount ' + device + 'p2 ' + mountpoint)
        os.system('sudo mount ' + device + 'p1 ' + mountpoint + '/boot')

    @staticmethod
    def unmount(device):
        """
        unmounts the current SD card
        """
        os.system('sudo umount ' + device + 'p1')
        try:
            os.system('sudo umount ' + device + 'p1')
        except:
            pass
        os.system('sudo umount ' + device + 'p2')

    @staticmethod
    def enable_ssh(mountpoint):
        """
        Enables ssh on next boot of sd card
        """
        # touch /media/pi/boot/ssh
        os.system('sudo touch ' + mountpoint + '/boot/ssh')


def analyse(arguments):
    if arguments['burn']:
        image = arguments['IMAGE']
        device = arguments['DEVICE']
        Burner.burn(image, device)
    elif arguments['mount']:
        device = arguments['DEVICE']
        mp = arguments['MOUNTPOINT']
        Burner.mount(device, mp)
    elif arguments['set'] and arguments['hostname']:
        hostname = arguments['HOSTNAME']
        mp = arguments['MOUNTPOINT']
        Burner.set_hostname(hostname, mp)
    elif arguments['set'] and arguments['ip']:
        ip = arguments['IP']
        mp = arguments['MOUNTPOINT']
        Burner.set_static_ip(ip, mp)
    elif arguments['set'] and arguments['key']:
        key = arguments['KEY']
        mp = arguments['MOUNTPOINT']
        Burner.set_key(key, mp)
    elif arguments['enable'] and arguments['ssh']:
        mp = arguments['MOUNTPOINT']
        Burner.enable_ssh(mp)
    elif arguments['unmount']:
        device = arguments['DEVICE']
        Burner.unmount(device)
    elif arguments['ls']:
        Image().ls()
    elif arguments['delete']:
        Image(arguments['IMAGE']).rm()
    elif arguments['get']:
        Image(arguments['URL']).fetch()
    elif arguments['versions']:
        repos = ["https://downloads.raspberrypi.org/raspbian_lite/images/"]
        for repo in repos:
            versions, downloads = Image().versions(repo)
            print("These images are available at")
            for version, download in zip(versions, downloads):
                print("{} at {}".format(version, download))
    elif arguments['create']:
        image = arguments['--image']
        device = arguments['--device']
        hostnames = hostlist.expand_hostlist(arguments['--hostname'])
        ips = hostlist.expand_hostlist(arguments['--ipaddr'])
        key = arguments['--sshkey']
        mp = '/mount/pi'

        for hostname, ip in zip(hostnames, ips):
            Burner.burn(image, device)
            Burner.mount(device, mp)
            Burner.enable_ssh(mp)
            Burner.set_hostname(hostname, mp)
            Burner.set_key(key, mp)
            Burner.set_static_ip(ip, mp)
            Burner.unmount(device)
            input('Insert next card and press enter...')


def main():
    """main entrypoint for setup.py"""
    VERSION = 1.0
    arguments = docopt(__doc__, version=VERSION)
    analyse(arguments)

if __name__ == '__main__':
    main()
