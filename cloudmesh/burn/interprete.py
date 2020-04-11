#! /usr/bin/env python3

# noinspection PyPep8


import os
from getpass import getpass
from pathlib import Path

import oyaml as yaml
from cloudmesh.burn.burner import Burner, MultiBurner, gen_strong_pass
from cloudmesh.burn.image import Image
from cloudmesh.burn.network import Network
from cloudmesh.burn.util import readfile, writefile
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer


def execute(label, function):
    StopWatch.start(label)
    function
    StopWatch.stop(label)
    StopWatch.status(label, True)

def interprete(arguments):
    dryrun = arguments.dryrun

    StopWatch.start("info")
    burner = Burner(dryrun=dryrun)
    StopWatch.stop("info")
    StopWatch.status("info", True)



    if arguments.network and arguments["list"]:

        ip = arguments.ip or Network.address()[0]['local']

        details = Network.nmap(ip=ip)

        if arguments.used:

            print(','.join([x['ip'] for x in details]))

        else:
            print(Printer.write(
                details,
                order=['name', "ip", "status", "latency", ],
                header=['Name', "IP", "Status", "Latency", ]
            )
            )
        return ""

    if arguments.network and arguments.address:

        # print (Network.nmap())
        details = Network.address()

        print(Printer.write(
            details,
            order=['label', "local", "broadcast"],
            header=["Label", "Local", "Broadcast"]
        )
        )
        return ""


    elif arguments.wifi:

        password = arguments.PASSWD
        ssid = arguments.SSID

        if password is None:
            password = getpass("Please enter the Wifi password; ")

        StopWatch.stop("wifi")
        # burner.configure_wifi(ssid, password)
        StopWatch.stop("wifi")
        StopWatch.status("wifi", True)

    elif arguments.detect:

        execute("burn", burner.detect())


    elif arguments.info:

        execute("burn", burner.info())

    elif arguments.burn:
        # check_root(dryrun=dryrun)

        image = arguments.IMAGE
        device = arguments.DEVICE
        execute("burn", burner.burn(image, device))

    elif arguments.mount:
        # check_root(dryrun=dryrun)

        device = arguments.DEVICE
        mp = arguments.MOUNTPOINT
        execute("mount", burner.mount(device, mp))

    elif arguments.set and arguments.host:
        # check_root(dryrun=dryrun)

        hostname = arguments.HOSTNAME
        mp = arguments.MOUNTPOINT
        execute("set hostname",        burner.set_hostname(hostname, mp))

    elif arguments.set and arguments.ip:
        # check_root(dryrun=dryrun)

        ip = arguments.IP
        mp = arguments.MOUNTPOINT
        execute("set ip",        burner.set_static_ip(ip, mp))

    elif arguments.set and arguments.key:
        # check_root(dryrun=dryrun)

        key = arguments.KEY
        mp = arguments.MOUNTPOINT
        execute("set key", burner.set_key(key, mp))

    elif arguments.enable and arguments.ssh:
        # check_root(dryrun=dryrun)

        mp = arguments.MOUNTPOINT
        execute("enable ssh",         burner.enable_ssh(mp))

    elif arguments.unmount:
        # check_root(dryrun=dryrun)

        device = arguments.DEVICE
        execute("unmount",         burner.unmount(device))

    # elif arguments.versions and arguments.image:
    #    image = Image()

    elif arguments.ls and arguments.image:
        execute("image ls",         Image().ls())


    elif arguments.delete and arguments.image:
        execute("image rm",        Image(arguments.IMAGE).rm())

    elif arguments.get and arguments.image:
        execute("image fetch",        Image(arguments.URL).fetch())

    elif arguments.versions and arguments.image:

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

    elif arguments.create:

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
            if arguments["--wifipassword"]:
                psk = arguments["--wifipassword"]
            else:
                psk = None
        else:
            if arguments["--wifipassword"]:
                print("Can't have wifi password with no ssid")
                return
            else:
                ssid = None

        # check_root(dryrun=dryrun)

        image = 'latest' if not arguments.image else arguments.image

        environ_DEV = os.environ['DEV'] if 'DEV' in os.environ else None
        devices = arguments["--device"] or environ_DEV or None

        if devices is not None:
            devices = Parameter.expand_string(devices)

        hostnames = Parameter.expand(arguments.hostname)

        ips = None if not arguments.ipaddr else Parameter.expand(
            arguments.ipaddr)
        key = arguments.sshkey
        mp = '/mount/pi'
        blocksize = arguments.blocksize

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
            psk=psk)

        StopWatch.stop("total")
        StopWatch.status("total", True)

        StopWatch.benchmark(sysinfo=False, csv=False)
