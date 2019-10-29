#!/usr/bin/env python3

"""Cloudmesh Raspberry Pi Mass Image Burner.
Usage:
  cm-pi-burn create [--image=IMAGE] [--group=GROUP] [--names=HOSTS]
                 [--ips=IPS] [--key=PUBLICKEY] [--ssid=SSID] [--psk=PSK]
                 [--domain=DOMAIN]
                 [--bootdrive=BOOTDRIVE] [--rootdrive=ROOTDRIVE]
                 [-n --dry-run] [-i --interactive]
  cm-pi-burn ls [-ni]
  cm-pi-burn rm IMAGE [-ni]
  cm-pi-burn get [URL]
  cm-pi-burn update
  cm-pi-burn check install
  cm-pi-burn hostname [HOSTNAME] [-ni]
  cm-pi-burn ssh [PUBLICKEY] [-ni]
  cm-pi-burn ip IPADDRESS [--domain=DOMAIN] [-ni]
  cm-pi-burn wifi SSID [PASSWD] [-ni]
  cm-pi-burn info [-ni]
  cm-pi-burn image [--image=IMAGE] [--device=DEVICE]
                [-ni]
  cm-pi-burn (-h | --help)
  cm-pi-burn --version

Options:

  -h --help         Show this screen.
  -n --dry-run      Show output of commands but don't execute them
  -i --interactive  Confirm each change before doing it
  --version         Show version.
  --key=KEY         the path of the public key [default: ~/.ssh/id_rsa.pub].
  --ips=IPS         the IPs in hostlist format
  --image=IMAGE     the image [default: 2019-09-26-raspbian-buster.img]

Description:

  Previously default: 2018-06-27-raspbian-stretch.img
  Other images can be found at
  https://downloads.raspberrypi.org/raspbian/images/
  Files:
    This is not fully thought through and needs to be documented
    ~/.cloudmesh/images
    ~/.cloudmesh/inventory
    Location where the images will be stored for reuse
  BUG:
    bootdrive and rootdrive will be removed in a future release as they are self
    discoverable
  Description:
    cm-burn
    cm-burn create [--image=IMAGE] [--group=GROUP] [--names=HOSTS]
                   [--ips=IPS] [--key=PUBLICKEY] [--ssid=SSID]
                   [--psk=PSK] [--bootdrive=BOOTDRIVE] [--rootdrive=ROOTDRIVE]
    cm-burn update
          updates the downloaded images if new once are available
    cm-burn ls
          lists the downloaded images
    cm-burn rm IMAGE
          remove the image
    cm-burn get URL
          downloads the image at the given URL
    cm-burn get jessie
          abbreviation to download a specific version of an image.
          Identify what would be useful.
    cm-burn hostname HOSTNAME
          writes the HOSTNAME as hostname on the currently inserted SD Card
    cm-burn hostname
          reads the hostname form the current SD card
  Example:
    cm-burn create --group=red --names=red[5-6] --ip=192.168.1.[5-6]
"""

"""
3. cp -r /home/pi/.ssh /media/pi/rootfs/home/pi/ .
4. chmod -R pi /media/pi/rootfs/home/pi/.ssh
	 chgrp -R pi /media/pi/rootfs/home/pi/.ssh
5. Figure out how to add static IP to Raspberry Pi
6. Figure out how to umount from /media/pi
7. Check cm-burn
"""

import os
import wget
from docopt import docopt
from pprint import pprint

class Image(object):

	def __init__(self, name):
		if name == "latest":
			self.url = 'https://downloads.raspberrypi.org/raspbian_lite_latest'
			self.directory = '.'
			self.image_name = '2019-09-26-raspbian-buster-lite.img'
			self.expected_sha = 'a50237c2f718bd8d806b96df5b9d2174ce8b789eda1f03434ed2213bbca6c6ff'

	def fetch(self):
		# if image is already there skip
		# else downlod from url using python requests
		# see cmburn.py you can copy form there
		if os.path.isfile(self.image_name):
			return
		source = requests.head(self.url, allow_redirects=True).url
		size = requests.get(self.url, stream=True).headers['Content-length']
		destination = os.path.basename(source)
		if debug:
			print(self.url)
			print(destination)
		download = True
		if os.path.exists(destination):
			if int(os.path.getsize(destination)) == int(size):
				WARNING("file already downloaded. Found at:", pathlib.Path(self.directory / destination))
				download = False
		if download:
			wget.download(image)

		# uncompressing
		image_name = destination.replace(".zip", "") + ".img"
		image_file = pathlib.Path(self.directory / image_name)
		if not os.path.exists(image_file):
			self.unzip_image(image_name)
		else:
			WARNING("file already downloaded. Found at:", pathlib.Path(self.directory / image_name))
		self.image = pathlib.Path(self.directory / image_name)
		return self.image

	def unzip_image(self, source):
		tmp = pathlib.Path(self.cloudmesh_images) / "."
		os.chdir(tmp)
		image_zip = str(pathlib.Path(self.cloudmesh_images / source)).replace(".img", ".zip")
		print("unzip image", image_zip)
		zipfile.ZipFile(image_zip).extractall()

	def verify(self):
		# verify if the image is ok, use SHA
		raise NotImplementedError

	def rm(self):
		# remove the downloaded image
		os.system('rm ' + self.image_name)

class Burner(object):

	def __init__(self, device):
		self.device = '/dev/mmcblk0'
		self.mountpoint = '/media/pi/'

	def burn(self, image):
		"""
		burns the SD Card
		:param image: name of the image
		"""
		os.system('sudo cat ' + image + ' >' + self.device)

	def set_hostname(self, hostname):
		"""
		sets the hostname on the sd card
		:param hostname:
		"""
		# write the new hostname to /etc/hostname
		with open(self.mountpoint + 'etc/hostname', 'w') as f:
			f.write(hostname + '\n')

		# change last line of /etc/hosts to have the new hostname
		# 127.0.1.1 raspberrypi   # default
		# 127.0.1.1 red47         # new
		with open(self.mountpoint + 'etc/hosts', 'r') as f: # read /etc/hosts
			lines = [l for l in f.readlines()][:-1] # ignore the last line
			newlastline = '127.0.1.1 ' + hostname + '\n'

		with open(self.mountpoint + 'etc/hosts', 'w') as f: # and write the modified version
			for line in lines:
				f.write(line)
			f.write(newlastline)

	def set_static_ip(self, ip):
		"""
		Sets the static ip on the sd card
		:param ip:
		"""
		with open(self.mountpoint + 'etc/hosts') as f:
			lines = [l for l in f.readlines()]
		with open(self.mountpoint + 'etc/hosts', 'w') as f:
			for line in lines:
				f.write(line)
			f.write('interface eth0\n')
			f.write('static ip_address=' + ip + '/24')

	def set_keys(self, name='id_rsa'):
		"""
		copies the public key into the .ssh/authorized_keys file on the sd card
		"""
		os.system('mkdir ' + self.mountpoint + 'home/raspberrypi/.ssh')
		os.system('cp ~/.ssh/' + name + '.pub ' + self.mountpoint + 'home/raspberrypi/.ssh/')

	def mount(self):
		"""
		mounts the current SD card
		"""
		os.system('sudo mount ' + self.device + ' ' + self.mountpoint)

	def unmount(self):
		"""
		unmounts the current SD card
		"""
		os.system('sudo umount ' + self.device)

	def enable_ssh(self):
		"""
		Enables ssh on next boot of sd card
		"""
		# touch /media/pi/boot/ssh
		os.system('touch ' + self.mountpoint + 'boot/ssh')

"""
if __name__ == "__main__":

	device = "FINDME"

	image = Image(name="latest")
	image.fetch()
	image.verify()

	sdcard = Burner(None)
	sdcard.burn(image)
	sdcard.mount()
	sdcard.enable_ssh()
	sdcard.set_hostname()
	sdcard.set_keys()
	sdcard.set_static_ip()
	sdcard.unmount()
"""

def analyse(arguments):
    pprint(arguments)
    # Set global dry-run to disable executing (potentially dangerous) commands
    """
    if arguments["--interactive"]:
        global interactive
        interactive = True

    if arguments["--dry-run"]:
        global dry_run
        dry_run = True
        print("DRY RUN - nothing will be executed.")

    """
    if arguments["ls"]:
        #burner = PiBurner()
        #burner.ls()
        print('ls')
    """
    elif arguments["get"]:
        burner = PiBurner()
        burner.get()
    elif arguments["create"]:
        burner = PiBurner()
        wifipass = None
        bootdrv = None
        rootdrv = None
        if "--bootdrive" in arguments:
            bootdrv = arguments["--bootdrive"]
        if "--rootdrive" in arguments:
            rootdrv = arguments["--rootdrive"]
        image = arguments["--image"]
        if not burner.image_exists(image):
            ERROR("The image {image} does not exist".format(image=image))
            sys.exit()
        else:
            burner.image = pathlib.Path(
                burner.home / ".cloudmesh" / "images" / image)
        burner.create(burner.image,
                      names=arguments["--names"],
                      key=arguments["--key"],
                      ips=arguments["--ips"],
                      domain=arguments["--domain"],
                      ssid=arguments["--ssid"],
                      psk=arguments["--psk"],
                      bootdrive=bootdrv,
                      rootdrive=rootdrv)

    elif arguments["check"] and arguments["install"]:
        ERROR("not yet implemented")

    elif arguments["hostname"]:
        host = arguments["HOSTNAME"]
        burner = PiBurner()

        if host is not None:
            print("Set host to:", host)
            burner.write_hostname(host)
        else:
            print(burner.read_hostname())

    elif arguments["wifi"]:
        ssid = arguments["SSID"]
        passwd = arguments["PASSWD"]
        if passwd is None:
            passwd = getpass.getpass()
        print(ssid)
        print(passwd)
        burner = PiBurner()
        burner.configure_wifi(ssid, passwd)

    elif arguments["image"]:
        image = arguments["--image"]
        device = arguments["--device"]
        burner = PiBurner()
        # check if image exists
        if not burner.image_exists(image):
            ERROR("The image {image} does not exist".format(image=image))
            sys.exit(1)
        else:
            burner.image = pathlib.Path(
                burner.home / ".cloudmesh" / "images" / image)

        # TODO: check if device exists
        if not burner.check_device(device):
            ERROR("The device {device} does not exist or not available".format(
                device=device))
            sys.exit()
        burner.burn(burner.image, device)

    elif arguments["ip"]:
        burner = PiBurner()

        ip = arguments["IPADDRESS"]
        print("Use ip:", ip)
        burner.set_ip(ip)

        domain = arguments["--domain"]
        if domain is not None:
            print("Use domain:", domain)
        burner.domain = domain

        burner.configure_static_ip()

    elif arguments["ssh"]:
        key = arguments["PUBLICKEY"]
        if key is None:
            key = os.path.expanduser("~") + "/.ssh/id_rsa.pub"
        print("Use ssh key:", key)
        burner = PiBurner()
        burner.activate_ssh(key)

    elif arguments["info"]:
        burner = PiBurner()
        burner.info()
    """

def main():
    """main entrypoint for setup.py"""
    VERSION = 1.0
    arguments = docopt(__doc__, version=VERSION)
    # if debug:
    #   print(arguments) # just for debugging
    analyse(arguments)
    #print('Hello, world!')


if __name__ == '__main__':
    main()
