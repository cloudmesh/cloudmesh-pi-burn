import os
import time
from getpass import getpass

# from cloudmesh.common.debug import VERBOSE
from cloudmesh.burn.Imager import Imager
from cloudmesh.burn.burner.Burner import Burner
from cloudmesh.burn.burner.RaspberryBurner import Burner as RaspberryBurner
from cloudmesh.burn.burner.raspberryos import MultiBurner
from cloudmesh.burn.image import Image
from cloudmesh.burn.network import Network
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.ubuntu.configure import Configure
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_windows
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.security import generate_strong_pass
from cloudmesh.common.util import Console
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import banner
from cloudmesh.inventory.inventory import Inventory
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.burn.usb import USB
from cloudmesh.common.debug import VERBOSE
from cloudmesh.burn.wifi.ssid import get_ssid
from cloudmesh.common.Host import Host
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell

if os_is_windows():
    from cloudmesh.burn.windowssdcard import Diskpart
    from cloudmesh.burn.windowssdcard import Wmic


class BurnCommand(PluginCommand):

    # noinspection PyBroadException
    @command
    def do_burn(self, args, arguments):
        """
        ::

            Usage:
              burn gui [--hostname=HOSTNAME]
                       [--ip=IP]
                       [--ssid=SSID]
                       [--wifipassword=PSK]
                       [--bs=BLOCKSIZE]
                       [--dryrun]
                       [--no_diagram]
              burn ubuntu NAMES [--inventory=INVENTORY] [--ssid=SSID]
                                [--wifipassword=PSK] [-v] --device=DEVICE [--country=COUNTRY]
                                [--upgrade]
              burn raspberry NAMES [--device=DEVICE]
                                   [--disk=DISK]
                                   [--inventory=INVENTORY]
                                   [--ssid=SSID]
                                   [--wifipassword=PSK]
                                   [--country=COUNTRY]
                                   [--password=PASSWORD]
                                   [-v]
                                   [-f]
                                   [--timezone=TIMEZONE]
              burn firmware check
              burn firmware update
              burn install
              burn load --device=DEVICE
              burn format [--device=DEVICE] [--disk=DISK]
              burn imager [TAG...]
              burn mount [--volume=VOLUME] [--device=DEVICE] [--os=OS]
              burn unmount [--device=DEVICE] [--os=OS]
              burn network list [--ip=IP] [--used]
              burn network
              burn info [--device=DEVICE] [--manager]
              burn image versions [--details] [--refresh] [--yaml]
              burn image ls
              burn image delete [--image=IMAGE]
              burn image get [--url=URL] [TAG...]
              burn backup [--device=DEVICE] [--to=DESTINATION]
              burn copy [--device=DEVICE] [--from=DESTINATION]
              burn shrink [--image=IMAGE]
              burn cluster --device=DEVICE --hostname=HOSTNAME
                           [--burning=BURNING]
                           [--ip=IP]
                           [--ssid=SSID]
                           [--wifipassword=PSK]
                           [--bs=BLOCKSIZE]
                           [--os=OS]
                           [-y]
                           [--imaged]
                           [--set_passwd]
              burn create [--image=IMAGE]
                          [--device=DEVICE]
                          [--burning=BURNING]
                          [--hostname=HOSTNAME]
                          [--ip=IP]
                          [--sshkey=KEY]
                          [--blocksize=BLOCKSIZE]
                          [--passwd=PASSWD]
                          [--ssid=SSID]
                          [--wifipassword=PSK]
                          [--format]
                          [--tag=TAG]
                          [--inventory=INVENTORY]
                          [--name=NAME]
                          [-y]
              burn sdcard [TAG...] [--device=DEVICE] [--disk=DISK] [-y]
              burn set [--hostname=HOSTNAME]
                       [--ip=IP]
                       [--key=KEY]
                       [--keyboard=COUNTRY]
                       [--cmdline=CMDLINE]
              burn enable ssh
              burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]
              burn check [--device=DEVICE]
              burn mac --hostname=HOSTNAME
              burn drive rm DRIVE
              burn drive assign VOLUME DRIVE



            Options:
              -h --help              Show this screen.
              --version              Show version.
              --image=IMAGE          The image filename,
                                     e.g. 2019-09-26-raspbian-buster.img
              --device=DEVICE        The device, e.g. /dev/sdX
              --hostname=HOSTNAME    The hostnames of the cluster
              --ip=IP                The IP addresses of the cluster
              --key=KEY              The name of the SSH key file
              --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]
              --burning=BURNING      The hosts to be burned

            Arguments:
               TAG                   Keyword tags to identify an image

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

                    Checks if the firmware on the Pi is up to date

                cms burn firmware update

                    Checks and updates the firmware on the Pi

                cms burn install

                    Installs a program to shrink img files. THis is
                    useful, after you created a backup to make the
                    backup smaller and allow faster burning in case of
                    recovery

                    This command is not supported on MacOS

                cms burn load --device=DEVICE

                    Loads the sdcard into the USB drive. Thi sis similar to
                    loading a cdrom drive. It s the opposite to eject

                cms burn format --device=DEVICE

                    Formats the SDCard in the specified device. Be
                    careful it is the correct device.  cms burn info
                    will help you to identifying it

                cms burn mount [--device=DEVICE] [--os=OS]

                    Mounts the file systems available on the SDCard

                cms burn unmount [--device=DEVICE] [--os=OS]

                    Unmounts the mounted file systems from the SDCard

                cms burn info [--device=DEVICE]

                    Provides useful information about the SDCard

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

                    Deletes the specified image. The name can be found
                    with the image ls command

                cms burn image get [--url=URL] [TAG...]

                    Downloads a specific image or the latest
                    image. The tag are a number of words separated by
                    a space that must occur in the tag that you find
                    in the versions command

                cms burn backup [--device=DEVICE] [--to=DESTINATION]

                    This command requires you to install pishrink previously with

                        cms burn install

                    Backs up a SDCard to the given location.

                cms burn copy [--device=DEVICE] [--from=DESTINATION]

                    Copies the file form the destination on the SDCard
                    this is the same as the SDCard command. we will in
                    future remove one

                cms burn shrink [--image=IMAGE]

                    Shrinks the size of a backup or image file that
                    is on your local file system. It can only be used
                    for .img files

                   This command is not supported on MacOS.

                cms burn create [--image=IMAGE]
                                [--device=DEVICE]
                                [--hostname=HOSTNAME]
                                [--ip=IP]
                                [--sshkey=KEY]
                                [--blocksize=BLOCKSIZE]
                                [--passwd=PASSWD]
                                [--ssid=SSID]
                                [--wifipassword=PSK]
                                [--format]

                    This command  not only can format the SDCard, but
                    also initializes it with specific values

                cms burn sdcard [TAG...] [--device=DEVICE]

                    this burns the sd card, see also copy and create

                cms burn set [--hostname=HOSTNAME]
                             [--ip=IP]
                             [--key=KEY]
                             [--mount=MOUNTPOINT]
                             [--keyboard=COUNTRY]
                             [--cmdline=CMDLINE]

                    Sets specific values on the sdcard after it
                    has ben created with the create, copy or sdcard
                    command

                    a --ssh is missing from this command

                cms burn enable ssh [--mount=MOUNTPOINT]

                    Enables the ssh server once it is booted

                cms burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]

                    Sets the wifi ssid and password after the card
                    is created, copied, or the sdcard is used.

                    The option country option expects an ISO 3166-1
                    two digit country code. The default is "US" and
                    the option not required if suitable. See
                    https://en.wikipedia.org/wiki/ISO_3166-1 for other
                    countries.

                cms burn check [--device=DEVICE]

                    Lists the parameters that were set
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
                       "details",
                       "refresh",
                       "device",
                       "dryrun",
                       "burning",
                       "hostname",
                       "ip",
                       "sshkey",
                       "blocksize",
                       "ssid",
                       "url",
                       "imaged",
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
                       "bs",
                       "set_passwd",
                       "cmdline",
                       "upgrade",
                       "no_diagram")

        # arguments.MOUNTPOINT = arguments["--mount"]
        arguments.FORMAT = arguments["--format"]
        arguments.FROM = arguments["--from"]
        arguments.IMAGE = arguments["--image"]
        arguments.output = "table"  # hard code for now
        arguments.bs = arguments.bs or "4M"
        arguments.yes = arguments["-y"]
        if len(arguments.TAG) == 0:
            arguments.TAG = "latest"

        # VERBOSE(arguments)

        def execute(label, function):
            StopWatch.start(label)
            result = function
            StopWatch.stop(label)
            StopWatch.status(label, True)
            return result

        burner = Burner()
        sdcard = SDCard()

        if arguments.drive and arguments.rm:

            Diskpart.remove_drive(arguments["DRIVE"])

        if arguments.drive and arguments.assign:

            Diskpart.assign_drive(volume=arguments["VOLUME"], letter=arguments["DRIVE"])


        elif arguments.imager:

            arguments.TAG = arguments.TAG or ["latest-lite"]

            Console.msg(f"Tags: {arguments.TAG}")
            try:
                file = Imager.fetch(tag=arguments.TAG)
            except:  # noqa: E722
                pass

            try:
                Imager.launch(file=file)
            except Exception as e:
                Console.error(f"could not find image with the tag {arguments.TAG}\n\n{e}\n")

            return ""

        elif arguments.gui:

            from cloudmesh.burn.gui import Gui
            VERBOSE(arguments)
            g = Gui(hostname=arguments.hostname,
                    ip=arguments.ip,
                    dryrun=arguments.dryrun,
                    no_diagram=arguments.no_diagram)

            g.run()

            return ""

        elif arguments.raspberry:
            banner(txt="RaspberryOS Burn", figlet=True)

            arguments.device = arguments["--device"] or arguments["--disk"]
            names = Parameter.expand(arguments.NAMES)
            manager, workers = Host.get_hostnames(names)
            ssid = arguments['--ssid']
            wifipasswd = arguments['--wifipassword']

            if arguments.inventory:
                burner = RaspberryBurner(inventory=arguments.inventory)
            else:
                if workers:
                    worker_base_name = ''.join(
                        [i for i in workers[0] if not i.isdigit()])

                cluster_name = manager or worker_base_name
                inventory = path_expand(f'~/.cloudmesh/inventory-{cluster_name}.yml')

                if not os.path.exists(inventory) or arguments['-f']:
                    if not manager:
                        Console.error("No inventory found. Can not create an "
                                      "inventory without a "
                                      "manager.")
                        return ""

                    _build_default_inventory(filename=inventory,
                                             manager=manager, workers=workers)

                burner = RaspberryBurner(inventory=inventory)

                if manager:
                    if not ssid:
                        ssid = get_ssid()
                        if ssid == "":
                            Console.info('Could not determine SSID, skipping wifi '
                                         'config')
                    if not wifipasswd and not ssid == "":
                        wifipasswd = getpass(f"Using --SSID={ssid}, please "
                                             f"enter wifi password:")

            execute("burn raspberry", burner.multi_burn(
                names=arguments.NAMES,
                devices=arguments.device,
                verbose=arguments['-v'],
                password=arguments['--password'],
                ssid=ssid,
                wifipasswd=wifipasswd,
                country=arguments['--country']
            ))
            return ""

        elif arguments.ubuntu:
            banner(txt="Ubuntu Burn with cloud-init", figlet=True)
            names = Parameter.expand(arguments.NAMES)
            if len(Parameter.expand(arguments.device)) > 1:
                Console.error("Too many devices specified. Please only specify one")
                return ""

            if arguments.inventory:
                c = Configure(inventory=arguments.inventory, debug=arguments['-v'])
                inv = Inventory(filename=arguments.inventory)
            else:
                c = Configure(debug=arguments['-v'])
                inv = Inventory()

            # Probably not the best way to get the tag, but we assume all tags
            # are the same for each row for now
            if inv.has_host(names[0]):
                tag = inv.get(name=names[0], attribute='tag')
            else:
                Console.error(f'Could not find {names[0]} in inventory {inv.filename}')
                return ""
            if 'ubuntu' not in tag:
                Console.error("This command only supports burning ubuntu cards")
                return ""
            sdcard = SDCard(card_os="ubuntu")

            # Code below taken from arguments.sdcard
            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            # determine if we are burning a manager, as this needs to be done
            # first to get the ssh public key
            manager = False
            for name in names:
                if not inv.has_host(name):
                    Console.error(f'Could not find {name} in inventory {inv.filename}')
                    return ""
                service = inv.get(name=name, attribute='service')
                if service == 'manager' and not manager:
                    manager = name
                    # make manager first in names
                    names.remove(name)
                    names.insert(0, name)
                elif service == 'manager' and manager:
                    raise Exception('More than one manager detected in NAMES')

            for name in names:
                if not yn_choice(f'Is the card to be burned for {name} inserted?'):
                    if not yn_choice(f"Please insert the card to be burned for {name}. "
                                     "Type 'y' when done or 'n' to terminante"):
                        Console.error("Terminating: User Break")
                        return ""

                service = inv.get(name=name, attribute='service')
                # Make sure bridge is only enabled if WiFi enabled
                if service == 'manager':
                    services = inv.get(name=name, attribute='services')
                    if 'bridge' in services and not arguments.ssid:
                        Console.error('Service bridge can only be configured if WiFi'
                                      ' is enabled with --ssid and --wifipassword')
                        return ""
                    else:
                        enable_bridge = 'bridge' in services

                Console.info(f'Burning {name}')
                sdcard.format_device(device=arguments.device, yes=True)
                if os_is_windows:
                    sdcard.burn_sdcard(tag=tag, device=arguments.device,yes=True)
                else:
                    sdcard.unmount(device=arguments.device)
                    sdcard.burn_sdcard(tag=tag, device=arguments.device, yes=True)
                    sdcard.mount(device=arguments.device, card_os="ubuntu")
                if service == 'manager':
                    # Generate a private public key pair for the manager that will be persistently used
                    priv_key, pub_key = c.generate_ssh_key(name)
                    # Write priv_key and pub_key to /boot/id_rsa and /boot/id_rsa.pub
                    SDCard.writefile(filename=f'{sdcard.boot_volume}/id_rsa', content=priv_key)
                    SDCard.writefile(filename=f'{sdcard.boot_volume}/id_rsa.pub', content=pub_key)
                    c.build_user_data(name=name,
                                      country=arguments.country,
                                      upgrade=arguments.upgrade,
                                      with_bridge=enable_bridge).write(
                        filename=sdcard.boot_volume + '/user-data')
                    c.build_network_data(name=name, ssid=arguments.ssid, password=arguments.wifipassword)\
                        .write(filename=sdcard.boot_volume + '/network-config')
                else:
                    c.build_user_data(name=name, add_manager_key=manager,
                                      upgrade=arguments.upgrade).write(
                        filename=sdcard.boot_volume + '/user-data')
                    c.build_network_data(name=name).write(filename=sdcard.boot_volume + '/network-config')
                time.sleep(1)  # Sleep for 1 seconds to give ample time for writing to finish
                sdcard.unmount(device=arguments.device, card_os="ubuntu")

                Console.info("Remove card")

            Console.ok(f"Burned {len(names)} card(s)")
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

            order = ["tag", 'date', "os", "type", 'version']
            header = ["Tag", 'Date', "OS", "Type", 'Version']
            if arguments.details:
                order = ["tag", 'date', "os", "type", 'version', "url"]
                header = ["Tag", 'Date', "OS", "Type", 'Version', "Url"]

            print(Printer.write(result, order=order, header=header, output=output))

            StopWatch.stop("image versions")
            StopWatch.status("image versions", True)
            return ""

        elif arguments.load:
            execute("load", sdcard.load_device(device=arguments.device))
            return ""

        elif arguments["format"]:  # as format is a python word, we need to use an index

            arguments.device = arguments.device or arguments["--disk"]

            if arguments.drive is None:
                Console.error("drive or device is not set")
                return ""
            execute("format", sdcard.format_device(device=arguments.device, unmount=True))

            return ""

        elif arguments.network and arguments["list"]:

            if os_is_mac():
                Console.error("Not yet implemented on MacOS")
                return ""

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

            if os_is_mac():
                Console.error("Not yet implemented on MacOS")
                return ""

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
            ssid = arguments.ssid or get_ssid()
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
            card = SDCard()
            execute("info", card.info(output=output))

            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            if os_is_windows() and arguments["--manager"]:
                Diskpart.manager()
            elif not os_is_windows() and arguments["--manager"]:
                Console.error("--manager is only supported on windows")
            return ""


        elif arguments.install:

            if os_is_mac():
                Console.error("Not yet implemented on MacOS")
                return ""

            execute("install", burner.install())
            return ""

        elif arguments.shrink:

            if os_is_mac():
                Console.error("Not yet implemented on MacOS")
                return ""

            execute("shrink", burner.shrink(image=arguments.IMAGE))
            return ""

        elif arguments.backup:
            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""
            execute("backup", sdcard.backup(device=arguments.device, to_file=arguments.to))
            return ""

        elif arguments["copy"]:  # as copy is a reserved word we need to use the index
            USB.check_for_readers()
            execute("copy", sdcard.copy(device=arguments.device, from_file=arguments.FROM))
            return ""

        elif arguments.sdcard:

            arguments.device = arguments.device or arguments["--disk"]

            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            if arguments.device is None:
                card = SDCard()
                card.info()
                Console.error("Please specify a device")
                return ""

            arguments.TAG = arguments.TAG or ["latest-lite"]
            if any("ubuntu" in tag for tag in arguments.TAG):
                sdcard = SDCard(card_os="ubuntu")

            execute("format", sdcard.format_device(device=arguments.device, unmount=True))
            if not os_is_windows():
                execute("unmount", sdcard.unmount(device=arguments.device))

            execute("sdcard", sdcard.burn_sdcard(tag=arguments.TAG,
                                                 device=arguments.device,
                                                 yes=arguments.yes))
            return ""

        elif arguments.mount:

            if arguments.device is None:
                card = SDCard
                card.info()
                Console.error("Please specify a device")
                return ""

            if arguments.volume is not None:
                execute("mount",sdcard.mount(device=arguments.device,volume=arguments.volume, card_os = arguments.os))
                return ""

            execute("mount", sdcard.mount(device=arguments.device, card_os=arguments.os))
            return ""

        elif arguments.unmount:

            card = SDCard(card_os=arguments.os)
            execute("unmount", card.unmount(device=arguments.device, card_os=arguments.os))
            return ""

        elif arguments.mac:

            hostnames = Parameter.expand(arguments.hostname)

            execute("mac", burner.mac(hostnames=hostnames))
            return ""

        elif arguments.set:

            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            if arguments.hostname:
                execute("set hostname", burner.set_hostname(arguments.hostname))

            if arguments.ip:
                execute("set ip", burner.set_static_ip(arguments.ip))

            if arguments.key:
                execute("set key", burner.set_key(arguments.key))

            if arguments.keyboard:
                execute("set keyboard", burner.keyboard(country=arguments.keyboard))

            if arguments.cmdline:
                execute("set cmdline", burner.set_cmdline(arguments.cmdline))

            return ""

        elif arguments.enable and arguments.ssh:
            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

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

            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""
            execute("cluster", burner.cluster(arguments=arguments))
            return ""

        elif arguments.create and arguments.inventory:
            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            if not os_is_pi():
                print()
                Console.error("This command has only been written for a  Raspberry Pis. "
                              "Terminating for caution")
                print()
                if yn_choice("Continue anyways?"):
                    pass
                else:
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
                device=arguments.device,
                yes=arguments.yes,
                passwd=arguments.passwd
            )
            StopWatch.stop("burn inventory")
            StopWatch.status("burn inventory", True)
            StopWatch.benchmark(sysinfo=False, csv=False)
            return ""

        elif arguments.create:

            try:
                USB.check_for_readers()
            except Exception as e:
                print()
                Console.error(e)
                print()
                return ""

            if arguments["--passwd"]:
                passwd = arguments["--passwd"]
            elif "PASSWD" in os.environ:
                passwd = os.environ["PASSWD"]
            else:
                passwd = generate_strong_pass()

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

            image = 'latest' or arguments.IMAGE

            dev = os.environ['DEV'] if 'DEV' in os.environ else None
            devices = arguments["--device"] or dev or None

            if devices is not None:
                devices = Parameter.expand_string(devices)

            hostnames = Parameter.expand(arguments.hostname)

            if arguments.burnimg is None:
                burning = hostnames
            else:
                burning = arguments.burning

            VERBOSE(arguments)

            ips = None if not arguments.ip else Parameter.expand(arguments.ip)
            key = arguments.sshkey
            tag = arguments['--tag']

            if os_is_pi() or os_is_linux():
                blocksize = arguments.blocksize
                StopWatch.start("total")

                multi = MultiBurner()
                multi.burn_all(
                    burning=burning,
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
                    tag=tag,
                    yes=arguments.yes
                )

                StopWatch.stop("total")
                StopWatch.status("total", True)

                StopWatch.benchmark(sysinfo=False, csv=False)
            else:
                Console.error("This command is only supported ona Pi and Linux")
            return ""

        Console.error("see manual page: cms help burn")
        return ""


def _build_default_inventory(filename, manager, workers, ips=None, images=None):
    # cms inventory add red --service=manager --ip=10.1.1.1 --tag=latest-lite
    # --timezone="America/Indiana/Indianapolis" --locale="us"
    # cms inventory set red services to "bridge" --listvalue
    # cms inventory add "red0[1-3]" --service=worker --ip="10.1.1.[2-4]"
    # --router=10.1.1.1 --tag=latest-lite  --timezone="America/Indiana/Indianapolis" --locale="us"
    # cms inventory set "red0[1-3]" dns to "8.8.8.8,8.8.4.4" --listvalue

    Console.info("No inventory found or forced rebuild. Buidling inventory "
                 "with defaults.")
    Shell.execute("rm", arguments=[
                  '-f', filename])
    i = Inventory(filename=filename)
    timezone = Shell.timezone()
    locale = Shell.locale()
    manager_ip = ips[0] if ips else '10.1.1.1'
    image = images[0] if images else 'latest-lite'
    element = {}
    element['host'] = manager
    element['status'] = 'inactive'
    element['service'] = 'manager'
    element['ip'] = manager_ip
    element['tag'] = image
    element['timezone'] = timezone
    element['locale'] = locale
    element['services'] = ['bridge', 'wifi']
    element['keyfile'] = '~/.ssh/id_rsa.pub'
    i.add(**element)
    i.save()

    last_octet = 2
    index = 1
    for worker in workers:
        ip = ips[index] if ips else f'10.1.1.{last_octet}'
        image = images[index] if images else 'latest-lite'
        element = {}
        element['host'] = worker
        element['status'] = 'inactive'
        element['service'] = 'worker'
        element['ip'] = ip
        element['tag'] = image
        element['timezone'] = timezone
        element['locale'] = locale
        element['router'] = manager_ip
        element['dns'] = ['8.8.8.8', '8.8.4.4']
        element['keyfile'] = '~/.ssh/id_rsa.pub'
        i.add(**element)
        i.save()
        last_octet += 1
        index += 1

    print(i.list(format="table"))
