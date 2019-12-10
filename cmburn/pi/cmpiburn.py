#!/usr/bin/env python3

"""
Cloudmesh Raspberry Pi Image Burner.

Usage:
  cm-pi-burn image versions [--refresh]
  cm-pi-burn image ls
  cm-pi-burn image delete [IMAGE]
  cm-pi-burn image get [URL]
  cm-pi-burn create [--image=IMAGE] [--device=DEVICE] [--hostname=HOSTNAME]
                    [--ipaddr=IP] [--sshkey=KEY] [--blocksize=BLOCKSIZE]
                    [--dryrun]
  cm-pi-burn burn [IMAGE] [DEVICE] --[dryrun]
  cm-pi-burn mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn set hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn set ip [IP] [MOUNTPOINT]
  cm-pi-burn set key [KEY] [MOUNTPOINT]
  cm-pi-burn enable ssh [MOUNTPOINT]
  cm-pi-burn unmount [DEVICE]
  cm-pi-burn (-h | --help)
  cm-pi-burn --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --image=IMAGE          The image filename, e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE        The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME    The hostname
  --ipaddr=IP            The IP address
  --key=KEY              The name of the SSH key file [default: id_rsa]
  --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
    Location where the images will be stored for reuse

Description:
  cm-pi-burn

Example:
  cm-pi-burn create --image=2019-09-26-raspbian-buster-lite --device=/dev/mmcblk0
                    --hostname=red[5-7] --ipaddr=192.168.1.[5-7] --sshkey=id_rsa
  cm-pi-burn.py image get latest
  cm-pi-burn.py image delete 2019-09-26-raspbian-buster-lite
  cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
"""

import os
import hostlist
from docopt import docopt
from pprint import pprint
import requests
from pathlib import Path
import sys
import zipfile
from glob import glob
import requests

from cmburn.pi.util import WARNING, readfile, writefile
from cmburn.pi.image import Image
from cmburn.pi import columns, lines
import oyaml as yaml
from cmburn.pi.burner import Burner

debug = True

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
    # elif arguments['versions'] and arguments['image']:
    #    image = Image()

    elif arguments['ls']:
        Image().ls()

    elif arguments['delete']:
        Image(arguments['IMAGE']).rm()

    elif arguments['get']:
        Image(arguments['URL']).fetch()

    elif arguments['versions']:

        data = []
        cache = Path(os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        if arguments["--refresh"] or not cache.exists():
            os.system("mkdir -p ~/.cloudmesh/cmburn")
            print ("finding repos ...", end="")
            repos = ["https://downloads.raspberrypi.org/raspbian_lite/images/"]
            for repo in repos:
                versions, downloads = Image().versions(repo)
                print("These images are available at")
                for version, download in zip(versions, downloads):
                    print(f"{version}: {download}")
                    data.append({version: download})
            writefile(cache, yaml.dump(data))
        else:
            data = yaml.load(readfile(cache), Loader=yaml.SafeLoader)
            for entry in data:
                version = list(entry.keys())[0]
                download = entry[version]
                print(f"{version}: {download}")

    elif arguments['create']:

        image = arguments['--image']
        device = arguments['--device']
        hostnames = hostlist.expand_hostlist(arguments['--hostname'])
        ips = hostlist.expand_hostlist(arguments['--ipaddr'])
        key = arguments['--sshkey']
        mp = '/mount/pi'
        blocksize = arguments["--blocksize"]

        dryrun = arguments["--dryrun"]
        # don't do the input() after burning the last card
        for hostname, ip in zip(hostnames[:-1], ips[:-1]):
            Burner.burn(image, device, blocksize=blocksize, dryrun=dryrun)

            if not dryrun:
                os.system('sleep 3')
            # wait to let the OS detect the filesystems on the newly burned card
            Burner.mount(device, mp, dryrun=dryrun)
            Burner.enable_ssh(mp, dryrun=dryrun)
            Burner.set_hostname(hostname, mp, dryrun=dryrun)
            Burner.set_key(key, mp, dryrun=dryrun)
            Burner.set_static_ip(ip, mp, dryrun=dryrun)
            # wait before unmounting
            if not dryrun:
                os.system('sleep 3')
            Burner.unmount(device, dryrun=dryrun)
            # for some reason, need to do unmount twice for it to work properly
            # wait again before second unmount
            if not dryrun:
                os.system('sleep 3')
            Burner.unmount(device, dryrun=dryrun)
            os.system('tput bel')  # ring the terminal bell to notify user
            print()
            input('Insert next card and press enter...')
            print('Burning next card...')
            print()

        for hostname, ip in zip(hostnames[-1:], ips[-1:]):
            Burner.burn(image, device, blocksize=blocksize, dryrun=dryrun)
            if not dryrun:
                os.system('sleep 3')
            Burner.mount(device, mp, dryrun=dryrun)
            Burner.enable_ssh(mp, dryrun=dryrun)
            Burner.set_hostname(hostname, mp, dryrun=dryrun)
            Burner.set_key(key, mp, dryrun=dryrun)
            Burner.set_static_ip(ip, mp, dryrun=dryrun)
            if not dryrun:
                os.system('sleep 3')
            Burner.unmount(device, dryrun=dryrun)
            if not dryrun:
                os.system('sleep 3')
            Burner.unmount(device, dryrun=dryrun)
            os.system('tput bel')
            print('All done!')


def main():
    """main entrypoint for setup.py"""
    VERSION = 1.0
    arguments = docopt(__doc__, version=VERSION)
    analyse(arguments)


if __name__ == '__main__':
    main()
