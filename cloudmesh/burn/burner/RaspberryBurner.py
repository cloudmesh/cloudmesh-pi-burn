import os
import time
from getpass import getpass

from cloudmesh.burn.burner.BurnerABC import AbstractBurner
from cloudmesh.burn.image import Image
from cloudmesh.burn.raspberryos.cmdline import Cmdline
from cloudmesh.burn.raspberryos.runfirst import Runfirst
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.usb import USB
from cloudmesh.burn.wifi.ssid import get_ssid
from cloudmesh.common.Host import Host
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import yn_choice
from cloudmesh.inventory.inventory import Inventory


class Burner(AbstractBurner):
    """
    Burner uses a cloudmesh inventory to create a RaspberryOS cluster

    Inventory should contain information on manager and workers
    """
    def __init__(self, inventory=None, names=None, ssid=None,
                 wifipassword=None, force_inv=False, country=None):
        # Get inventory
        self.ssid = ssid
        self.wifipasswd = wifipassword
        if inventory is None:
            names = Parameter.expand(names)
            manager, workers = Host.get_hostnames(names)
            if workers:
                worker_base_name = ''.join(
                    [i for i in workers[0] if not i.isdigit()])

            cluster_name = manager or worker_base_name
            inventory = path_expand(f'~/.cloudmesh/inventory-{cluster_name}.yaml')

            if not os.path.exists(inventory) or force_inv:
                if not manager:
                    Console.error("No inventory found. Can not create an "
                                  "inventory without a "
                                  "manager.")
                    return ""

                Inventory.build_default_inventory(filename=inventory,
                                                  manager=manager,
                                                  workers=workers)
            inv = Inventory(filename=inventory)

        else:
            inv = Inventory(filename=inventory)
        self.inventory = inv

        # Find managers and workers
        managers = inv.find(service='manager')
        if len(managers) > 0:
            if not self.ssid:
                self.ssid = get_ssid()
                if self.ssid == "":
                    Console.info('Could not determine SSID, skipping wifi '
                                 'config')
                    self.ssid = None
            if not self.wifipasswd and self.ssid:
                self.wifipasswd = getpass(f"Using --SSID={self.ssid}, please "
                                          f"enter wifi password:")
        workers = inv.find(service='worker')
        # No inherenet need to distinguish the configs by service
        configs = managers + workers
        # Create dict for them for easy lookup
        self.configs = dict((config['host'], config) for config in configs)
        self.get_images()
        self.country = country if country else Shell.locale().upper()

    def get_images(self):
        """
        Downloads all tags found in self.configs
        """
        tags = set()
        for config in self.configs.values():
            try:
                tags.add(config['tag'])
            except KeyError as e:
                Console.warning(f'Could not find tag for {config["host"]}. Skipping')

        banner("Downloading Images", figlet=True)

        image = Image()

        for tag in tags:
            Console.info(f'Attempting to download {tag}')
            res = image.fetch(tag=[tag])
            if not res:
                Console.error('Failed Image Fetch.')
                raise Exception('Failed Image Fetch')

    def cluster(self, arguments=None):
        raise NotImplementedError

    def burn(self,
             name=None,
             device=None,
             verbose=False,
             password=None,
             ):
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

        config = self.configs[name]
        sdcard = SDCard(card_os="raspberry")

        try:
            USB.check_for_readers()
        except Exception as e:
            print()
            Console.error(e)
            print()
            return ""

        banner(f"Burn {name}", figlet=True)

        # Confirm card is inserted into device path
        if not yn_choice(f'Is the card to be burned for {name} inserted?'):
            if not yn_choice(f"Please insert the card to be burned for {name}. "
                             "Type 'y' when done or 'n' to terminante"):
                Console.error("Terminating: User Break")
                return ""

        Console.info(f'Burning {name}')
        sdcard.format_device(device=device, yes=True)
        sdcard.unmount(device=device)
        sdcard.burn_sdcard(tag=config['tag'], device=device, yes=True)
        sdcard.mount(device=device, card_os="raspberry")

        # Read and write cmdline.txt
        cmdline = Cmdline()
        # Reading will create the proper script in the cmdline instance
        # No extra work needed
        cmdline.read(filename=f'{sdcard.boot_volume}/cmdline.txt')
        cmdline.write(filename=f'{sdcard.boot_volume}/cmdline.txt')
        # print(cmdline.get())

        # Build the proper runfrist.sh
        runfirst = Runfirst()
        runfirst.set_hostname(config['host'])
        other_hosts, other_ips = self._get_hosts_for(name=config['host'])
        runfirst.set_hosts(names=other_hosts, ips=other_ips)
        if config['ip']:
            # config['router'] and config['dns'] are allowed to be empty String or None to skip its config
            # Default column in inventory is empty string
            runfirst.set_static_ip(ip=config['ip'], router=config['router'], dns=config['dns'])

        if password:
            runfirst.set_password(password=password)

        runfirst.set_locale(timezone=config['timezone'], locale=config['locale'])
        if self.ssid and 'wifi' in config['services']:
            runfirst.set_wifi(self.ssid, self.wifipasswd, self.country)

        runfirst.set_key(key=readfile(config['keyfile']).strip())
        if 'bridge' in config['services']:
            runfirst.enable_bridge()

        runfirst.get(verbose=verbose)
        runfirst.write(filename=f'{sdcard.boot_volume}/{Runfirst.SCRIPT_NAME}')

        time.sleep(1)  # Sleep for 1 seconds to give ample time for writing to finish
        sdcard.unmount(device=device, card_os="raspberry")
        Console.ok(f'Burned {name}')

        return

    def inventory(self, arguments=None):
        return self.inventory

    def multi_burn(self,
                   names=None,
                   devices=None,
                   verbose=False,
                   password=None,
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
                password=password
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
