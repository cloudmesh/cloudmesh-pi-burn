#! /usr/bin/env python3

# noinspection PyPep8
"""
Cloudmesh Raspberry Pi Image Burner.

Usage:
  cm-pi-burn [-v] info [DEVICE]
  cm-pi-burn [-v] detect
  cm-pi-burn [-v] image versions [--refresh]
  cm-pi-burn [-v] image ls
  cm-pi-burn [-v] image delete [IMAGE]
  cm-pi-burn [-v] image get [URL]
  cm-pi-burn [-v]create [--image=IMAGE] [--device=DEVICE] [--hostname=HOSTNAME]
                        [--ipaddr=IP] [--sshkey=KEY] [--blocksize=BLOCKSIZE]
                        [--dryrun]
  cm-pi-burn [-v] burn [IMAGE] [DEVICE] --[dryrun]
  cm-pi-burn [-v] mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn [-v] set hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn [-v] set ip [IP] [MOUNTPOINT]
  cm-pi-burn [-v] set key [KEY] [MOUNTPOINT]
  cm-pi-burn [-v] enable ssh [MOUNTPOINT]
  cm-pi-burn [-v] unmount [DEVICE]
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
from pathlib import Path

from cmburn.pi.util import readfile, writefile
from cmburn.pi.image import Image
import oyaml as yaml
from cmburn.pi.burner import Burner
from cloudmesh.common.StopWatch import StopWatch

debug = True


def analyse(arguments):
    dryrun = arguments["--dryrun"]
    verbose = arguments["-v"]
    
    StopWatch.start("info")
    burner = Burner(dryrun=dryrun)
    StopWatch.stop("info")

    if arguments['detect']:

        StopWatch.start("burn")
        burner.detect()
        StopWatch.stop("burn")

    if arguments['info']:

        StopWatch.start("burn")
        burner.info()
        StopWatch.stop("burn")

    elif arguments['burn']:
        # check_root(dryrun=dryrun)

        image = arguments['IMAGE']
        device = arguments['DEVICE']
        StopWatch.start("burn")
        burner.burn(image, device)
        StopWatch.stop("burn")

    elif arguments['mount']:
        # check_root(dryrun=dryrun)

        device = arguments['DEVICE']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("mount")
        burner.mount(device, mp)
        StopWatch.stop("mount")

    elif arguments['set'] and arguments['hostname']:
        # check_root(dryrun=dryrun)

        hostname = arguments['HOSTNAME']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set hostname")
        burner.set_hostname(hostname, mp)
        StopWatch.stop("set hostname")

    elif arguments['set'] and arguments['ip']:
        # check_root(dryrun=dryrun)

        ip = arguments['IP']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set ip")
        burner.set_static_ip(ip, mp)
        StopWatch.stop("set ip")

    elif arguments['set'] and arguments['key']:
        # check_root(dryrun=dryrun)

        key = arguments['KEY']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set key")
        burner.set_key(key, mp)
        StopWatch.stop("set key")

    elif arguments['enable'] and arguments['ssh']:
        # check_root(dryrun=dryrun)

        mp = arguments['MOUNTPOINT']
        StopWatch.start("enable ssh")
        burner.enable_ssh(mp)
        StopWatch.stop("enable ssh")

    elif arguments['unmount']:
        # check_root(dryrun=dryrun)

        device = arguments['DEVICE']
        StopWatch.start("unmount")
        burner.unmount(device)
        StopWatch.stop("unmount")

    # elif arguments['versions'] and arguments['image']:
    #    image = Image()

    elif arguments['ls'] and arguments['image']:
        StopWatch.start("image ls")
        Image().ls()
        StopWatch.stop("image ls")

    elif arguments['delete'] and arguments['image']:
        StopWatch.start("image rm")
        Image(arguments['IMAGE']).rm()
        StopWatch.stop("image rm")

    elif arguments['get'] and arguments['image']:
        StopWatch.start("image fetch")

        Image(arguments['URL']).fetch()
        StopWatch.stop("image fetch")

    elif arguments['versions'] and arguments['image']:

        StopWatch.start("image versions")

        data = []
        cache = Path(
            os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
        if arguments["--refresh"] or not cache.exists():
            os.system("mkdir -p ~/.cloudmesh/cmburn")
            print("finding repos ...", end="")
            repos = ["https://downloads.raspberrypi.org/raspbian_lite/images/"]
            for repo in repos:
                versions, downloads = Image().versions(repo)
                print("These images are available at")
                for version, download in zip(versions, downloads):
                    print("{}: {}".format(version, download))
                    data.append({version: download})
            writefile(cache, yaml.dump(data))
        else:
            data = yaml.load(readfile(cache), Loader=yaml.SafeLoader)
            for entry in data:
                version = list(entry.keys())[0]
                download = entry[version]
                print("{}: {}".format(version, download))
        StopWatch.stop("image versions")

    elif arguments['create']:

        StopWatch.start("create")

        # check_root(dryrun=dryrun)

        image = arguments['--image']
        device = arguments['--device']
        hostnames = hostlist.expand_hostlist(arguments['--hostname'])
        ips = hostlist.expand_hostlist(arguments['--ipaddr'])
        key = arguments['--sshkey']
        mp = '/mount/pi'
        blocksize = arguments["--blocksize"]

        # don't do the input() after burning the last card
        counter = 1
        for hostname, ip in zip(hostnames[:-1], ips[:-1]):

            print("counter", counter)
            StopWatch.start("fcreate {hostname}")
            burner.burn(image, device, blocksize=blocksize)

            if not dryrun:
                os.system('sleep 3')
            # wait to let the OS detect the filesystems on the newly burned card
            burner.mount(device, mp)
            burner.enable_ssh(mp)
            burner.set_hostname(hostname, mp)
            burner.set_key(key, mp)
            burner.set_static_ip(ip, mp)
            # wait before unmounting
            if not dryrun:
                os.system('sleep 3')
            burner.unmount(device)
            # for some reason, need to do unmount twice for it to work properly
            # wait again before second unmount
            if not dryrun:
                os.system('sleep 3')
            burner.unmount(device)
            StopWatch.start("fcreate {hostname}")

            os.system('tput bel')  # ring the terminal bell to notify user
            print()
            input('Insert next card and press enter...')
            print('Burning next card...')
            print()
            counter = counter + 1

        for hostname, ip in zip(hostnames[-1:], ips[-1:]):
            burner.burn(image, device, blocksize=blocksize)
            if not dryrun:
                os.system('sleep 3')
            burner.mount(device, mp)
            burner.enable_ssh(mp)
            burner.set_hostname(hostname, mp)
            burner.set_key(key, mp)
            burner.set_static_ip(ip, mp)
            if not dryrun:
                os.system('sleep 3')
            burner.unmount(device)
            if not dryrun:
                os.system('sleep 3')
            burner.unmount(device)
            os.system('tput bel')
            print('All done!')

    if verbose:
        StopWatch.benchmark(sysinfo=False, csv=False)


def main():
    """main entrypoint for setup.py"""
    version = 1.0
    arguments = docopt(__doc__, version=version)
    analyse(arguments)


if __name__ == '__main__':
    main()
