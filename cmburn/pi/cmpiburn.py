#! /usr/bin/env python3

# noinspection PyPep8
"""
Cloudmesh Raspberry Pi Image Burner.

Usage:
  cm-pi-burn network list [--ip=IP] [--used]
  cm-pi-burn network address
  cm-pi-burn [-v] info [DEVICE]
  cm-pi-burn [-v] detect
  cm-pi-burn [-v] image versions [--refresh]
  cm-pi-burn [-v] image ls
  cm-pi-burn [-v] image delete [IMAGE]
  cm-pi-burn [-v] image get [URL]
  cm-pi-burn [-v] create [--image=IMAGE]
                         [--device=DEVICE]
                         [--hostname=HOSTNAME]
                         [--ipaddr=IP]
                         [--sshkey=KEY]
                         [--blocksize=BLOCKSIZE]
                         [--dryrun]
                         [--passwd=PASSWD]
                         [--ssid=SSID]
                         [--wifipsk=PSK]
                         [--format]
  cm-pi-burn [-v] burn [IMAGE] [DEVICE] --[dryrun]
  cm-pi-burn [-v] mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn [-v] set hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn [-v] set ip [IP] [MOUNTPOINT]
  cm-pi-burn [-v] set key [KEY] [MOUNTPOINT]
  cm-pi-burn [-v] enable ssh [MOUNTPOINT]
  cm-pi-burn [-v] unmount [DEVICE]
  cm-pi-burn [-v] wifi SSID [PASSWD] [-ni]
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
  cm-pi-burn create

     --passwd=PASSWD

         if the passwd flag is added the default password is
         queried from the commandline and added to all SDCards

         if the flag is ommitted login via the password is disabled and
         only login via the sshkey is allowed

  Network

    cm-pi-burn network list

        Lists the ip addresses that are on the same network

        +------------+---------------+----------+-----------+
        | Name       | IP            | Status   | Latency   |
        |------------+---------------+----------+-----------|
        | Router     | 192.168.1.1   | up       | 0.0092s   |
        | iPhone     | 192.168.1.4   | up       | 0.061s    |
        | red01      | 192.168.1.46  | up       | 0.0077s   |
        | laptop     | 192.168.1.78  | up       | 0.058s    |
        | unkown     | 192.168.1.126 | up       | 0.14s     |
        | red03      | 192.168.1.158 | up       | 0.0037s   |
        | red02      | 192.168.1.199 | up       | 0.0046s   |
        | red        | 192.168.1.249 | up       | 0.00021s  |
        +------------+----------------+----------+-----------+

    cm-pi-burn network list [--used]

        Lists the used ip addresses as a comma separated parameter list

           192.168.50.1,192.168.50.4,...

    cm-pi-burn network address

        Lists the own network address

        +---------+----------------+----------------+
        | Label   | Local          | Broadcast      |
        |---------+----------------+----------------|
        | wlan0   | 192.168.1.12   | 192.168.1.255  |
        +---------+----------------+----------------+

Example:
  cm-pi-burn create --image=2019-09-26-raspbian-buster-lite --device=/dev/mmcblk0
                    --hostname=red[5-7] --ipaddr=192.168.1.[5-7] --sshkey=id_rsa
  cm-pi-burn.py image get latest
  cm-pi-burn.py image delete 2019-09-26-raspbian-buster-lite
  cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
"""

import os
from docopt import docopt
from pathlib import Path
from getpass import getpass

from cmburn.pi.util import readfile, writefile
from cmburn.pi.image import Image
from cmburn.pi.network import Network
import oyaml as yaml
from cmburn.pi.burner import Burner, MultiBurner, gen_strong_pass
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Tabulate import Printer

debug = True


# Accepts arguments of the form
# /dev/sd[a-c] -> [/dev/sda, /dev/sdb, /dev/sdc]
# /dev/sd[a,b,c] -> [/dev/sda, /dev/sdb, /dev/sdc]
def device_parser(expr):
    left = expr.find("[")
    if left < 0:
        return [expr]
    selection = expr[left + 1:expr.find("]")]
    partial_expr = expr[:left]
    results = []
    if "-" in selection:
        selection = selection.split("-")
        for i in range(ord(selection[0]), ord(selection[1]) + 1):
            results.append(partial_expr + chr(i))
    elif "," in selection:
        selection = selection.split(",")
        for l in selection:
            results.append(partial_expr + l)
    else:
        raise NotImplementedError
    return results


def analyse(arguments):
    dryrun = arguments["--dryrun"]
    verbose = arguments["-v"]

    StopWatch.start("info")
    burner = Burner(dryrun=dryrun)
    StopWatch.stop("info")
    StopWatch.status("info", True)


    if arguments["network"]  and arguments["list"]:

        ip = arguments["ip"] or Network.address()[0]['local']

        details = Network.nmap(ip=ip)

        if arguments["--used"]:

            print(','.join([x['ip'] for x in details]))

        else:
            print(Printer.write(
                details,
                order=[
                    'name',
                    "ip",
                    "status",
                    "latency",
                ],
                header=[
                    'Name',
                    "IP",
                    "Status",
                    "Latency",
                ]
                )
            )
        return ""

    if arguments["network"] and arguments["address"]:

        # print (Network.nmap())
        details = Network.address()

        print(Printer.write(
            details,
            order=[
                'label',
                "local",
                "broadcast"],
            header=["Label",
                    "Local",
                    "Broadcast"]
            )
        )
        return ""


    elif arguments['wifi']:

        password = arguments['PASSWD']
        ssid = arguments['SSID']

        if password is None:
            password = getpass("Please enter the Wifi password; ")

        StopWatch.stop("wifi")
        # burner.configure_wifi(ssid, password)
        StopWatch.stop("wifi")
        StopWatch.status("wifi", True)

    elif arguments['detect']:

        StopWatch.start("burn")
        burner.detect()
        StopWatch.stop("burn")
        StopWatch.status("burn", True)

    elif arguments['info']:

        StopWatch.start("burn")
        burner.info()
        StopWatch.stop("burn")
        StopWatch.status("burn", True)

    elif arguments['burn']:
        # check_root(dryrun=dryrun)

        image = arguments['IMAGE']
        device = arguments['DEVICE']
        StopWatch.start("burn")
        burner.burn(image, device)
        StopWatch.stop("burn")
        StopWatch.status("burn", True)

    elif arguments['mount']:
        # check_root(dryrun=dryrun)

        device = arguments['DEVICE']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("mount")
        burner.mount(device, mp)
        StopWatch.stop("mount")
        StopWatch.status("mount", True)

    elif arguments['set'] and arguments['hostname']:
        # check_root(dryrun=dryrun)

        hostname = arguments['HOSTNAME']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set hostname")
        burner.set_hostname(hostname, mp)
        StopWatch.stop("set hostname")
        StopWatch.status("set hostname", True)

    elif arguments['set'] and arguments['ip']:
        # check_root(dryrun=dryrun)

        ip = arguments['IP']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set ip")
        burner.set_static_ip(ip, mp)
        StopWatch.stop("set ip")
        StopWatch.status("set ip", True)

    elif arguments['set'] and arguments['key']:
        # check_root(dryrun=dryrun)

        key = arguments['KEY']
        mp = arguments['MOUNTPOINT']
        StopWatch.start("set key")
        burner.set_key(key, mp)
        StopWatch.stop("set key")
        StopWatch.status("set key", True)

    elif arguments['enable'] and arguments['ssh']:
        # check_root(dryrun=dryrun)

        mp = arguments['MOUNTPOINT']
        StopWatch.start("enable ssh")
        burner.enable_ssh(mp)
        StopWatch.stop("enable ssh")
        StopWatch.status("enable ssh", True)

    elif arguments['unmount']:
        # check_root(dryrun=dryrun)

        device = arguments['DEVICE']
        StopWatch.start("unmount")
        burner.unmount(device)
        StopWatch.stop("unmount")
        StopWatch.status("unmount", True)

    # elif arguments['versions'] and arguments['image']:
    #    image = Image()

    elif arguments['ls'] and arguments['image']:
        StopWatch.start("image ls")
        Image().ls()
        StopWatch.stop("image ls")
        StopWatch.status("image ls", True)


    elif arguments['delete'] and arguments['image']:
        StopWatch.start("image rm")
        Image(arguments['IMAGE']).rm()
        StopWatch.stop("image rm")
        StopWatch.status("image rm", True)

    elif arguments['get'] and arguments['image']:
        StopWatch.start("image fetch")

        Image(arguments['URL']).fetch()
        StopWatch.stop("image fetch")
        StopWatch.status("image fetch", True)

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
        StopWatch.status("image versions", True)

    elif arguments['create']:

        if arguments["--passwd"]:
            passwd = arguments["--passwd"]
        elif "PASSWD" in os.environ:
            passwd = os.environ["PASSWD"]
        else:
            # Shouldn't go here...
            passwd = gen_strong_pass()

        psk = None
        if arguments["--ssid"]:
            ssid = arguments["--ssid"]
            if arguments["--wifipsk"]:
                psk = arguments["--wifipsk"]
            else:
                psk = None
        else:
            if arguments["--wifipsk"]:
                print("Can't have wifi password with no ssid")
                return
            else:
                ssid = None

        # TODO Improve
        fromatting = True if arguments["--format"] else False

        #
        # BUG stopwatch without end
        #
        StopWatch.start("create")

        # check_root(dryrun=dryrun)

        image = arguments['--image']

        devices = device_parser(arguments['--device'])
        # devices = arguments["--device"].split(",")
        
        hostnames = Parameter.expand(arguments['--hostname'])
        ips = None if not arguments['--ipaddr'] else Parameter.expand(
            arguments['--ipaddr'])
        key = arguments['--sshkey']
        mp = '/mount/pi'
        blocksize = arguments["--blocksize"]

        StopWatch.start("total")

        multi = MultiBurner()

        multi.burn_all(
            image=image,
            device=devices,
            blocksize=blocksize,
            progress=True,
            hostnames=hostnames,
            # not difference between names and name, maybe we shoudl allign
            ips=ips,
            key=key,
            password=passwd,
            ssid=ssid,
            psk=psk,
            fromatting=fromatting)
        StopWatch.stop("total")
        StopWatch.status("total", True)

    if verbose:
        StopWatch.benchmark(sysinfo=False, csv=False)


def main():
    """main entrypoint for setup.py"""
    version = 1.0
    arguments = docopt(__doc__, version=version)
    analyse(arguments)


if __name__ == '__main__':
    main()
