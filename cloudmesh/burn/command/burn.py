import os
from getpass import getpass
from pathlib import Path

import oyaml as yaml
from cloudmesh.burn.burner import Burner
from cloudmesh.burn.burner import MultiBurner
from cloudmesh.burn.burner import gen_strong_pass
from cloudmesh.burn.image import Image
from cloudmesh.burn.network import Network
from cloudmesh.burn.util import readfile
from cloudmesh.burn.util import writefile
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class BurnCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_burn(self, args, arguments):
        """
        ::

            Usage:
              burn network list [--ip=IP] [--used]
              burn network
              burn info [--device=DEVICE]
              burn detect
              burn image versions [--refresh]
              burn image ls
              burn image delete [--image=IMAGE]
              burn image get [--url=URL]
              burn backup [--device=DEVICE] [--to=DESTINATION]
              burn copy [--device=DEVICE] [--from=DESTINATION]
              burn shrink [--image=DESTINATION]
              burn create [--image=IMAGE]
                          [--device=DEVICE]
                          [--hostname=HOSTNAME]
                          [--ip=IP]
                          [--sshkey=KEY]
                          [--blocksize=BLOCKSIZE]
                          [--dryrun]
                          [--passwd=PASSWD]
                          [--ssid=SSID]
                          [--wifipassword=PSK]
                          [--format]
              burn sdcard [--image=IMAGE] [--device=DEVICE] [--dryrun]
              burn mount [--device=DEVICE] [--mount=MOUNTPOINT]
              burn set [--hostname=HOSTNAME]
                       [--ip=IP]
                       [--key=KEY]
                       [--mount=MOUNTPOINT]
              burn enable ssh [--mount=MOUNTPOINT]
              burn unmount [--device=DEVICE]
              burn wifi SSID [--passwd=PASSWD] [-ni]

            Options:
              -h --help              Show this screen.
              --version              Show version.
              --image=IMAGE          The image filename,
                                     e.g. 2019-09-26-raspbian-buster.img
              --device=DEVICE        The device, e.g. /dev/mmcblk0
              --hostname=HOSTNAME    The hostname
              --ip=IP                The IP address
              --key=KEY              The name of the SSH key file
              --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

            Files:
              This is not fully thought through and needs to be documented
              ~/.cloudmesh/images
                Location where the images will be stored for reuse

            Description:
                cms burn create --passwd=PASSWD

                     if the passwd flag is added the default password is
                     queried from the commandline and added to all SDCards

                     if the flag is ommitted login via the password is disabled
                     and only login via the sshkey is allowed

              Network

                cms burn network list

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

                cms burn network list [--used]

                    Lists the used ip addresses as a comma separated parameter
                    list

                       192.168.50.1,192.168.50.4,...

                cms burn network address

                    Lists the own network address

                     +---------+----------------+----------------+
                     | Label   | Local          | Broadcast      |
                     |---------+----------------+----------------|
                     | wlan0   | 192.168.1.12   | 192.168.1.255  |
                     +---------+----------------+----------------+

            Examples: ( \ is not shown)

               > cms burn create --image=2019-09-26-raspbian-buster-lite
               >                 --device=/dev/mmcblk0
               >                 --hostname=red[5-7]
               >                 --ip=192.168.1.[5-7]
               >                 --sshkey=id_rsa

               > cms burn image get latest

               > cms burn image get https://downloads.raspberrypi.org/
               >   raspbian_lite/images/
               >   raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip

               > cms burn image delete 2019-09-26-raspbian-buster-lite

        """

        map_parameters(arguments,
                       "refresh",
                       "device",
                       "hostname",
                       "ip",
                       "sshkey",
                       "blocksize",
                       "dryrun",
                       "ssid",
                       "url",
                       "key",
                       "passwd",
                       "wifipassword",
                       "version",
                       "to")
        arguments.mountpoint = arguments["--mount"]
        arguments.FORMAT = arguments["--format"]
        arguments.FROM = arguments["--from"]

        VERBOSE(arguments)

        def execute(label, function):
            StopWatch.start(label)
            function
            StopWatch.stop(label)
            StopWatch.status(label, True)

        dryrun = arguments['--dryrun']

        StopWatch.start("info")
        burner = Burner(dryrun=dryrun)
        StopWatch.stop("info")
        StopWatch.status("info", True)

        if arguments.versions and arguments['image']:

            StopWatch.start("image versions")
            image = Image()
            data = {
                "lite": [],
                "full": []
            }
            cache = Path(
                os.path.expanduser("~/.cloudmesh/cmburn/distributions.yaml"))
            if arguments["--refresh"] or not cache.exists():
                os.system("mkdir -p ~/.cloudmesh/cmburn")
                print("finding lite repos ...", end="")
                repos = [f"{image.raspberry_lite_images}"]
                for repo in repos:
                    versions, downloads = Image().versions(repo)
                    print("These images are available at")
                    for version, download in zip(versions, downloads):
                        entry = {
                            "version": version,
                            "url": download,
                            "date": version.split("-", 1)[1]
                        }
                        data["lite"].append(entry)

                print("finding lite repos ...", end="")
                repos = [f"{image.raspberry_full_images}"]
                for repo in repos:
                    versions, downloads = Image().versions(repo)
                    print("These images are available at")
                    for version, download in zip(versions, downloads):
                        entry = {
                            "version": version,
                            "url": download,
                            "date": version.split("-", 1)[1]
                        }
                        data["full"].append(entry)
                writefile(cache, yaml.dump(data))
            else:
                # data = yaml.load(readfile(cache), Loader=yaml.SafeLoader)
                # for entry in data:
                #   version = list(entry.keys())[0]
                #    download = entry[version]
                #    print(f"{version}: {download}")
                data = readfile(cache)
                print(data)
            StopWatch.stop("image versions")
            StopWatch.status("image versions", True)
            return ""

        elif arguments.network and arguments["list"]:

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

        elif arguments.network:

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

            password = arguments.passwd
            ssid = arguments.ssid

            if password is None:
                password = getpass("Please enter the Wifi password; ")

            StopWatch.stop("wifi")
            # burner.configure_wifi(ssid, password)
            StopWatch.stop("wifi")
            StopWatch.status("wifi", True)
            return ""

        elif arguments.detect:

            execute("detect", burner.detect())
            return ""

        elif arguments.info:

            execute("info", burner.info())
            return ""

        elif arguments.shrink:

            execute("burn", burner.shrink(to_file=arguments.image))

        elif arguments.backup:

            execute("burn",
                    burner.backup(device=arguments.device, to_file=arguments.to))

        elif arguments.copy:

            execute("copy",
                    burner.copy(device=arguments.device, from_file=arguments.FROM))

        elif arguments.sdcard:
            # check_root(dryrun=dryrun)

            image = arguments.image
            device = arguments.device
            execute("sdcard", burner.burn_sdcard(image, device))
            return ""

        elif arguments.mount:
            # check_root(dryrun=dryrun)

            device = arguments.device
            mp = arguments.mountpoint
            execute("mount", burner.mount(device, mp))
            return ""

        elif arguments.set:

            if arguments.host:
                # check_root(dryrun=dryrun)

                hostname = arguments.hostname
                mp = arguments.mountpoint
                execute("set hostname", burner.set_hostname(hostname, mp))

            if arguments.ip:
                # check_root(dryrun=dryrun)

                ip = arguments.ip
                mp = arguments.mountpoint
                execute("set ip", burner.set_static_ip(ip, mp))

            if arguments.key:
                # check_root(dryrun=dryrun)

                key = arguments.key
                mp = arguments.mountpoint
                execute("set key", burner.set_key(key, mp))
                return ""

        elif arguments.enable and arguments.ssh:
            # check_root(dryrun=dryrun)

            mp = arguments.mountpoint
            execute("enable ssh", burner.enable_ssh(mp))
            return ""

        elif arguments.unmount:
            # check_root(dryrun=dryrun)

            device = arguments.device
            execute("unmount", burner.unmount(device))
            return ""

        # elif arguments.versions and arguments.image:
        #    image = Image()

        elif arguments.ls and arguments['image']:
            execute("image ls", Image().ls())
            return ""

        elif arguments.delete and arguments['image']:
            execute("image rm", Image(arguments.image).rm())
            return ""

        elif arguments.get and arguments['image']:
            execute("image fetch", Image(arguments.url).fetch())
            return ""

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

            image = 'latest' if not arguments['image'] else arguments['image']

            environ_DEV = os.environ['DEV'] if 'DEV' in os.environ else None
            devices = arguments["--device"] or environ_DEV or None

            if devices is not None:
                devices = Parameter.expand_string(devices)

            hostnames = Parameter.expand(arguments.hostname)

            ips = None if not arguments.ip else Parameter.expand(arguments.ip)
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
            return ""

        Console.error("see manual page: cms help burn")
        return ""
