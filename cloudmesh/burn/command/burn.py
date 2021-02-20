import os
from getpass import getpass

from cloudmesh.burn.burner import Burner
from cloudmesh.burn.burner import MultiBurner
from cloudmesh.burn.burner import gen_strong_pass
from cloudmesh.burn.image import Image
from cloudmesh.burn.network import Network
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_linux
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import Console
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
# from cloudmesh.common.debug import VERBOSE
from cloudmesh.burn.Imager import Imager


class BurnCommand(PluginCommand):

    @command
    def do_burn(self, args, arguments):
        """
        ::

            Usage:
              burn firmware check
              burn firmware update
              burn install
              burn load --device=DEVICE
              burn format --device=DEVICE
              burn imager [TAG...]
              burn mount [--device=DEVICE] [--os=OS]
              burn unmount [--device=DEVICE] [--os=OS]
              burn network list [--ip=IP] [--used]
              burn network
              burn info [--device=DEVICE]
              burn image versions [--refresh] [--yaml]
              burn image ls
              burn image delete [--image=IMAGE]
              burn image get [--url=URL] [TAG...]
              burn backup [--device=DEVICE] [--to=DESTINATION]
              burn copy [--device=DEVICE] [--from=DESTINATION]
              burn shrink [--image=IMAGE]
              burn cluster --device=DEVICE --hostname=HOSTNAME
                           [--ip=IP]
                           [--ssid=SSID]
                           [--wifipassword=PSK]
                           [--bs=BLOCKSIZE]
                           [-y]
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
                          [--tag=TAG]
                          [--inventory=INVENTORY]
                          [--name=NAME]
              burn sdcard [TAG...] [--device=DEVICE] [--dryrun]
              burn set [--hostname=HOSTNAME]
                       [--ip=IP]
                       [--key=KEY]
                       [--keyboard=COUNTRY]
              burn enable ssh
              burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]
              burn check [--device=DEVICE]
              burn mac --hostname=HOSTNAME

            Options:
              -h --help              Show this screen.
              --version              Show version.
              --image=IMAGE          The image filename,
                                     e.g. 2019-09-26-raspbian-buster.img
              --device=DEVICE        The device, e.g. /dev/sdX
              --hostname=HOSTNAME    The hostname
              --ip=IP                The IP address
              --key=KEY              The name of the SSH key file
              --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

            Arguments:
                TAG                  Keyword tags to identify an image
                                     [default: latest]
            Files:
              This is not fully thought through and needs to be documented
              ~/.cloudmesh/images
                Location where the images will be stored for reuse

            Description:
                cms burn create --inventory=INVENTORY --device=DEVICE --name=NAME

                    Will refer to a specified cloudmesh inventory file (see cms help inventory).
                    Will search the configurations for NAME inside of INVENTORY and will burn
                    to DEVICE. Supports parameter expansion.

                cms burn create --passwd=PASSWD

                     if the passwd flag is added the default password is
                     queried from the commandline and added to all SDCards

                     if the flag is omitted login via the password is
                     disabled and only login via the sshkey is allowed

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

                cms burn firmware check

                    checks if the firmware on the Pi is up to date

                cms burn firmware update

                    checks and updates the firmware on the Pi

                cms burn install

                    installs a program to shrink img files. THis is
                    useful, after you created a backup to make the
                    backup smaller and allow faster burning in case of
                    recovery

                cms burn load --device=DEVICE

                    loads the sdcard into the USB drive. Thi sis similar to
                    loading a cdrom drive. It s the opposite to eject

                cms burn format --device=DEVICE

                    formats the SDCard in the specified device. Be
                    careful it is the correct device.  cms burn info
                    will help you to identifying it

                cms burn mount [--device=DEVICE] [--os=OS]

                    mounts the file systems available on the SDCard

                cms burn unmount [--device=DEVICE] [--os=OS]

                    unmounts the mounted file systems from the SDCard

                cms burn info [--device=DEVICE]

                    provides useful information about the SDCard

                cms burn image versions [--refresh] [--yaml]

                    The images that you like to burn onto your SDCard
                    can be cached locally with the image command.  The
                    available images for the PI can be found when
                    using the --refresh option. If you do not specify
                    it it reads a copy of the image list from our
                    cache

                cms burn image ls

                    Lists all downloaded images in our cache. You can
                    download them with the cms burn image get command

                cms burn image delete [--image=IMAGE]

                    deletes the specified image. The name can be found
                    with the image ls command

                cms burn image get [--url=URL] [TAG...]

                    downloads a specific image or the latest
                    image. The tag are a number of words separated by
                    a space that must occur in the tag that you find
                    in the versions command

                cms burn backup [--device=DEVICE] [--to=DESTINATION]

                    backs up a SDCard to the given location

                cms burn copy [--device=DEVICE] [--from=DESTINATION]

                    copies the file form the destination on the SDCard
                    this is the same as the SDCard command. we will in
                    future remove one

                cms burn shrink [--image=IMAGE]

                    shrinks the size of a backup or image file that
                    is on your local file system. It can only be used
                    for .img files

                cms burn create [--image=IMAGE]
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

                    This command  not only can format the SDCard, but
                    also initializes it with specific values

                cms burn sdcard [TAG...] [--device=DEVICE] [--dryrun]

                    this burns the sd card, see also copy and create

                cms burn set [--hostname=HOSTNAME]
                             [--ip=IP]
                             [--key=KEY]
                             [--mount=MOUNTPOINT]
                             [--keyboard=COUNTRY]

                    this sets specific values on the sdcard after it
                    has ben created with the create, copy or sdcard
                    command

                    a --ssh is missing from this command

                cms burn enable ssh [--mount=MOUNTPOINT]

                    this enables the ssh server once it is booted

                cms burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]

                    this sets the wifi ssid and password after the card
                    is created, copied, or the sdcard is used.

                    The option country option expects an ISO 3166-1
                    two digit country code. The default is "US" and
                    the option not required if suitable. See
                    https://en.wikipedia.org/wiki/ISO_3166-1 for other
                    countries.

                cms burn check [--device=DEVICE]

                    this command lists the parameters that were set
                    with the set or create command

            Examples: ( \\ is not shown)

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
                       # "output",
                       "ssid",
                       "url",
                       "key",
                       "keyboard",
                       "passwd",
                       "wifipassword",
                       "version",
                       "to",
                       "os",
                       "country",
                       "inventory",
                       "name",
                       "bs")
        # arguments.MOUNTPOINT = arguments["--mount"]
        arguments.FORMAT = arguments["--format"]
        arguments.FROM = arguments["--from"]
        arguments.IMAGE = arguments["--image"]
        arguments.output = "table"  # hard code for now
        arguments.bs = arguments.bs or "4M"

        # VERBOSE(arguments)

        def execute(label, function):
            StopWatch.start(label)
            result = function
            StopWatch.stop(label)
            StopWatch.status(label, True)
            return result

        dryrun = arguments['--dryrun']

        StopWatch.start("info")
        burner = Burner(dryrun=dryrun)
        StopWatch.stop("info")
        StopWatch.status("info", True)

        if arguments.imager:

            arguments.TAG = arguments.TAG or ["latest-lite"]

            Console.msg(f"Tags: {arguments.TAG}")
            try:
                file = Imager.fetch(tag=arguments.TAG)
            except:
                pass

            try:
                Imager.launch(file=file)
            except Exception as e:
                Console.error(f"could not find image with the tag {arguments.TAG}\n\n{e}\n")

            return ""

        elif arguments.firmware and arguments.check:

            execute("firmware check", burner.firmware(action="check"))
            return ""

        elif arguments.firmware and arguments.update:

            execute("firmware update", burner.firmware(action="update"))
            return ""

        if arguments.check:

            execute("check", burner.check(device=arguments.device))
            return ""

        elif arguments.versions and arguments['image']:

            StopWatch.start("image versions")

            result = Image.create_version_cache(refresh=arguments["--refresh"])

            output = "table"
            if arguments["--yaml"]:
                output = "yaml"

            print(Printer.write(
                result,
                order=["tag", 'date', "type", 'version', "url"],
                header=["Tag", 'Date', "Type", 'Version', "Url"],
                output=output
            )
            )

            StopWatch.stop("image versions")
            StopWatch.status("image versions", True)
            return ""

        elif arguments.load:
            execute("load", burner.load_device(device=arguments.device))
            return ""

        elif arguments["format"]:  # as format is a python word, we need to use an index
            execute("format", burner.format_device(device=arguments.device, unmount=True))
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
            country = arguments.country

            if password is None:
                password = getpass("Please enter the Wifi password or enter "
                                   "for no password: ")

            if os_is_mac():
                host = "macos"
            elif os_is_linux():
                host = "linux"
            elif os_is_pi():
                host = "raspberry"
            else:
                Console.error("This command is not yet implemented for your OS")
                return ""

            burner.configure_wifi(ssid, psk=password, country=country, host=host)

            return ""

        elif arguments.info:

            output = arguments.output or "table"
            execute("info", burner.info(output=output))
            return ""

        elif arguments.install:

            execute("install", burner.install())
            return ""

        elif arguments.shrink:

            execute("shrink", burner.shrink(image=arguments.IMAGE))
            return ""

        elif arguments.backup:
            execute("backup", burner.backup(device=arguments.device, to_file=arguments.to))
            return ""

        elif arguments["copy"]:  # as copy is a reserved word we need to use the index
            execute("copy", burner.copy(device=arguments.device, from_file=arguments.FROM))
            return ""

        elif arguments.sdcard:
            arguments.TAG = arguments.TAG or ["latest-lite"]

            execute("sdcard", burner.burn_sdcard(tag=arguments.TAG, device=arguments.device))
            return ""

        elif arguments.mount:
            execute("mount", burner.mount(device=arguments.device,
                                          card_os=arguments.os))
            return ""

        elif arguments.unmount:
            execute("unmount", burner.unmount(device=arguments.device,
                                              card_os=arguments.os))
            return ""

        elif arguments.mac:

            hostnames = Parameter.expand(arguments.hostname)

            execute("mac", burner.mac(hostnames=hostnames))
            return ""

        elif arguments.set:

            if arguments.hostname:
                execute("set hostname", burner.set_hostname(arguments.hostname))

            if arguments.ip:
                execute("set ip", burner.set_static_ip(arguments.ip))

            if arguments.key:
                execute("set key", burner.set_key(arguments.key))

            if arguments.keyboard:
                execute("set keyboard", burner.set_keyboard(country=arguments.keyboard))

            return ""

        elif arguments.enable and arguments.ssh:

            execute("enable ssh", burner.enable_ssh())
            return ""

        # elif arguments.versions and arguments.image:
        #    image = Image()

        elif arguments.ls and arguments['image']:
            execute("image ls", Image().ls())
            return ""

        elif arguments.delete and arguments.IMAGE:
            execute("image rm", Image().rm(arguments.IMAGE))
            return ""

        elif arguments["get"] and arguments['image'] and arguments["--url"]:
            image = Image()
            execute("image fetch", image.fetch(url=arguments.url))
            return ""

        elif arguments["get"] and arguments['image'] and arguments["TAG"]:

            tag = arguments["TAG"]
            if "latest" in tag and ("full" in tag or "lite" in tag):
                result = Image.create_version_cache(refresh=arguments["--refresh"])

            image = Image()
            execute("image fetch", image.fetch(tag=arguments["TAG"]))
            return ""

        elif arguments["get"] and arguments['image']:
            image = Image()
            execute("image fetch", image.fetch(tag="latest"))
            return ""

        elif arguments.cluster:

            # is true when
            #
            # cms burn cluster --hostname=red,red00[1-2]
            #                  --device=/dev/sdb
            #                  --ip=10.1.1.[1-3]
            #                  --ssid=myssid
            #                  --wifipassword=mypass
            #
            arguments.yes = arguments["-y"]

            execute("cluster", burner.cluster(arguments=arguments))
            return ""

        elif arguments.create and arguments.inventory:
            if not os_is_pi():
                Console.error("This command has only been safely tested on Raspberry Pis. Terminating for caution")
                return
            if not arguments.name:
                Console.error("Missing --name parameter. See cms help burn for usage")
                return ""
            if not arguments.device:
                Console.error("Missing --device parameter. See cms help burn for usage")
                return ""

            StopWatch.start("burn inventory")
            multi_burner = MultiBurner()
            # Perhaps we want to change the path at some point
            inventory = f"~/.cloudmesh/{arguments.inventory}"
            multi_burner.burn_inventory(
                inventory=inventory,
                name=arguments.name,
                device=arguments.device)
            StopWatch.stop("burn inventory")
            StopWatch.status("burn inventory", True)
            StopWatch.benchmark(sysinfo=False, csv=False)
            return ""

        elif arguments.create:

            if arguments["--passwd"]:
                passwd = arguments["--passwd"]
            elif "PASSWD" in os.environ:
                passwd = os.environ["PASSWD"]
            else:
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

            image = 'latest' or arguments.IMAGE

            dev = os.environ['DEV'] if 'DEV' in os.environ else None
            devices = arguments["--device"] or dev or None

            if devices is not None:
                devices = Parameter.expand_string(devices)

            hostnames = Parameter.expand(arguments.hostname)

            ips = None if not arguments.ip else Parameter.expand(arguments.ip)
            key = arguments.sshkey
            tag = arguments['--tag']

            if os_is_pi() or os_is_linux():
                blocksize = arguments.blocksize
                StopWatch.start("total")

                multi = MultiBurner()
                multi.burn_all(
                    image=image,
                    device=devices,
                    blocksize=blocksize,
                    progress=True,
                    hostnames=hostnames,
                    # not difference between names and name, maybe we should align
                    ips=ips,
                    key=key,
                    password=passwd,
                    ssid=ssid,
                    psk=psk,
                    tag=tag)

                StopWatch.stop("total")
                StopWatch.status("total", True)

                StopWatch.benchmark(sysinfo=False, csv=False)
            else:
                Console.error("This command is only supported ona Pi and Linux")
            return ""

        Console.error("see manual page: cms help burn")
        return ""
