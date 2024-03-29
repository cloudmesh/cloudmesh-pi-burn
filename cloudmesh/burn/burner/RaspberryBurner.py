import time
import os

from cloudmesh.burn.burner.BurnerABC import AbstractBurner
from cloudmesh.burn.raspberryos.cmdline import Cmdline
from cloudmesh.burn.raspberryos.runfirst import Runfirst
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.usb import USB
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import readfile
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
from cloudmesh.inventory.inventory import Inventory
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.burn.windowssdcard import Diskpart


class Burner(AbstractBurner):
    """
    Burner uses a cloudmesh inventory to create a RaspberryOS cluster

    Inventory should contain information on manager and workers
    """

    def __init__(self, inventory=None):
        # Get inventory
        if inventory is None:
            inv = Inventory()
        else:
            inv = Inventory(filename=inventory)

        # Find managers and workers
        managers = inv.find(service='manager')
        workers = inv.find(service='worker')

        # No inherent need to distinguish the configs by service
        configs = managers + workers
        # Create dict for them for easy lookup
        self.configs = dict((config['host'], config) for config in configs)

    def cluster(self, arguments=None):
        raise NotImplementedError

    def burn(self,
             name=None,
             device=None,
             verbose=False,
             password=None,
             ssid=None,
             wifipasswd=None,
             country=None,
             withimage=True,
             network="internal"):
        """
        Given the name of a config, burn device with RaspberryOS and configure properly
        """
        if device is None:
            Console.error('Device not specified')
            return
        if name is None:
            Console.error('Name to burn is not specified')
            return
        if name not in self.configs:
            Console.error(f'Could not find {name} in Inventory. Is the service column marked as "manager" or "worker"?')
            return
        if country is None:
            country = "US"

        config = self.configs[name]
        sdcard = SDCard(card_os="raspberry")

        # This block only works for Macs
        try:
            r = USB.check_for_readers()
        except Exception as e:
            print()
            Console.error(e)
            print()
            return ""

        banner(txt=f"Create RUNFIRST {name}", figlet=True)

        # Build the proper runfrist.sh
        runfirst = Runfirst()
        runfirst.set_hostname(config['host'])
        other_hosts, other_ips = self._get_hosts_for(name=config['host'])
        if network in ['internal']:
            runfirst.set_hosts(names=other_hosts, ips=other_ips)
            if config['ip']:
                # config['router'] and config['dns'] are allowed to be empty String or None to skip its config
                # Default column in inventory is empty string
                runfirst.set_static_ip(ip=config['ip'], router=config['router'], dns=config['dns'])

        if password:
            runfirst.set_password(password=password)

        runfirst.set_locale(timezone=config['timezone'], locale=config['locale'])
        if ssid:
            runfirst.set_wifi(ssid, wifipasswd, country=country)

        runfirst.set_key(key=readfile(config['keyfile']).strip())
        if 'bridge' in config['services'] and network in ['internal']:
            runfirst.enable_bridge()

        runfirst.get(verbose=verbose)

        runfirst.info()

        print(runfirst.script)

        banner(txt=f"Burn {name}", figlet=True)

        card = SDCard().info(print_os=False, print_stdout=False)
        if device not in card:
            label = "device"

            if os_is_windows():
                label = "disk"

            SDCard().info(print_stdout=True)

            error = f"The {label} {device} could not be found in the list of possible SD Card readers"
            Console.error(error)

            if not yn_choice("Would you like to continue?"):
                raise ValueError(error)

        # Confirm card is inserted into device path
        if not yn_choice(f'Is the card to be burned for {name} inserted?'):
            if not yn_choice(f"Please insert the card to be burned for {name}. "
                             "Type 'y' when done or 'n' to terminate. Continue"):
                Console.error("Terminating: User Break")
                return ""

        Console.info(f'Burning {name}')

        if os_is_windows():
            if withimage:
                sdcard.format_device(device=device, unmount=True)
                banner("Burn image", color="GREEN")
                sdcard.burn_sdcard(name=name, tag=config['tag'], device=device, yes=True)

            detail = Diskpart.detail(disk=device)
            letter = detail["Ltr"]

            # sdcard instance needs the drive letter in order to use
            # sdcard.boot_volume later (windows)
            sdcard.set_drive(drive=letter)

            # print(f"Letter {letter}")
            # yn_choice("Burn completed. Continue")

        else:
            if withimage:
                sdcard.format_device(device=device, yes=True)
                sdcard.unmount(device=device)
                banner("Burn image", color="GREEN")
                sdcard.burn_sdcard(name=name, tag=config['tag'], device=device, yes=True)
            sdcard.mount(device=device, card_os="raspberry")

        # Read and write cmdline.txt
        cmdline = Cmdline()
        # Reading will create the proper script in the cmdline instance
        # No extra work needed
        # This gets rid of whitespace in cmdline.txt file?
        cmdline.update(filename=f'{sdcard.boot_volume}/cmdline.txt')
        cmdline.write(filename='tmp-cmdline.txt')
        # print("--- cmdline.txt ---")
        # print(cmdline.script)
        # print("---")

        #
        # write the run first
        #
        runfirst.write(filename=f'{sdcard.boot_volume}/{Runfirst.SCRIPT_NAME}')
        os.system(f"chmod a+x {sdcard.boot_volume}/{Runfirst.SCRIPT_NAME}")

        if not os_is_windows():
            time.sleep(1)  # Sleep for 1 seconds to give ample time for writing to finish
            sdcard.unmount(device=device, card_os="raspberry")
        else:
            time.sleep(2)  # Sleep for 1 seconds to give ample time for writing to finish
            os.system(f"cat {sdcard.boot_volume}/{Runfirst.SCRIPT_NAME}")
        Console.ok(f'Burned {name}')

        return

    def inventory(self, arguments=None):
        raise NotImplementedError

    def multi_burn(self,
                   names=None,
                   devices=None,
                   verbose=False,
                   password=None,
                   ssid=None,
                   wifipasswd=None,
                   country=None,
                   withimage=True,
                   network="internal"
                   ):
        """
        Given multiple names, burn them
        """
        if devices is None:
            Console.error('Device not specified.')
            return
        if names is None:
            Console.error('Names to burn not specified')
            return

        names = Parameter.expand(names)
        devices = Parameter.expand(devices)

        if len(devices) > 1:
            Console.error('We do not yet support burning on multiple devices')
            return

        for name in names:
            self.burn(
                name=name,
                device=devices[0],
                verbose=verbose,
                password=password,
                ssid=ssid,
                wifipasswd=wifipasswd,
                country=country,
                withimage=withimage,
                network=network
            )
        Console.ok('Finished burning all cards')

    def _get_hosts_for(self, name=None):
        """
        Given a name, return the list of hostnames and ips to go into /etc/hosts
        """
        if name is None:
            raise Exception('name is None')
        if self.configs is None:
            raise Exception('no configs supplied yet')

        host_names = []
        ips = []

        for host_name in self.configs:
            if name != host_name and self.configs[host_name]['ip']:
                host_names += [host_name]
                ips += [self.configs[host_name]['ip']]
        return host_names, ips
