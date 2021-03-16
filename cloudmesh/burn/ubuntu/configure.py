import os
import time

from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.burn.ubuntu.networkdata import Networkdata
from cloudmesh.common.console import Console
from cloudmesh.common.util import readfile
from cloudmesh.inventory.inventory import Inventory
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand

class Configure:
    """
    This class serves to build cloud-init config files for entries in a cloudmesh inventory file.
    This accepts two params for init:
    inventory = INVENTORY_FILE
    cluster = CLUSTER_NAME

    If inventory arg is None, then default ~/.cloudmesh/inventory.yaml is used

    if cluster arg is not None, then nodes are found by searching via the
    "cluster" column in inventory

    if cluster arg is None, then nodes are found by searching for "worker" and "manager" in the
    "service" column in inventory

    Usage:
    config_generator = Configure()
    Configure.build_user_data(name=NAME) returns a Userdata builder object
    where NAME is the hostname of an entry in inventory.yaml with corresponding config options
    """

    def __init__(self, inventory=None, cluster=None, debug=False):
        self.debug = debug

        if inventory:
            self.inventory = Inventory(inventory)
        else:
            self.inventory = Inventory()

        if cluster is not None:
            self.nodes = self.inventory.find(cluster=cluster)
        else:
            self.nodes = self.inventory.find(service='manager') + self.inventory.find(service='worker')

        self.manager_public_key = None

    def build_user_data(self, name=None, with_defaults=True, country=None,
                        add_manager_key=False, upgrade=False):
        """
        Given a name, get its config from self.inventory and create a Userdata object
        """
        if name is None:
            raise Exception('name arg supplied is None')
        elif not self.inventory.has_host(name):
            raise Exception(f'Could not find {name} in {self.inventory.filename}')
        if country is not None and len(country) != 2:
            raise Exception(f'Country code is not 2 characters.')

        # Get the current configurations from inventory
        hostname = self.inventory.get(name=name, attribute='host')
        keyfile = self.inventory.get(name=name, attribute='keyfile')
        if keyfile:
            keys = readfile(keyfile).strip().split('\n')
        else:
            keys = None

        if keys is None and add_manager_key:
            keys = [self.manager_public_key]
        elif add_manager_key:
            keys.append(self.manager_public_key)

        service = self.inventory.get(name=name, attribute='service')

        # Build Userdata
        user_data = Userdata()

        if with_defaults:
            user_data.with_locale().with_net_tools().with_packages(
                packages='avahi-daemon')
        if upgrade:
            user_data.with_package_update().with_package_upgrade()
        if hostname:
            user_data.with_hostname(hostname=hostname)
        if keys:
            # Disable password auth in favor of key auth
            user_data.with_ssh_password_login(ssh_pwauth=False)
            user_data.with_authorized_keys(keys=keys)
        else:
            user_data.with_default_user().with_ssh_password_login()
        # Add known hosts
        user_data.with_hosts(hosts=self.get_hosts_for(name=name))
        if country:
            user_data.with_set_wifi_country(country=country)
        if service == 'manager':
            #generate and store the ssh pub key to add to workers
            priv_key,pub_key = self.generate_ssh_key(hostname=name)
            user_data.with_write_files(content=priv_key,
                                       path='/home/ubuntu/.ssh/id_rsa',
                                       permissions='0600')
            user_data.with_write_files(content=pub_key,
                                       path='/home/ubuntu/.ssh/id_rsa.pub',
                                       permissions='0644')
            user_data.with_fix_user_dir_owner(user='ubuntu')

        if self.debug:
            Console.info(f'User data for {name}:\n' + str(user_data))


        return user_data

    def build_network_data(self, name=None, ssid=None, password=None,
                           with_defaults=True):
        """
        Given a name, get its config from self.inventory and create a Networkdata object
        """
        if name is None:
            raise Exception('name arg supplied is None')
        elif not self.inventory.has_host(name):
            raise Exception(f'Could not find {name} in {self.inventory.filename}')
        if ssid or password:
            if not ssid or not password:
                raise Exception("ssid or password supplied with no corresponding ssid or password")

        # Get the current configurations from inventory
        eth0_ip = self.inventory.get(name=name, attribute='ip')
        eth0_nameservers = self.inventory.get(name=name, attribute='dns')
        eth0_gateway = self.inventory.get(name=name, attribute='router')

        network_data = Networkdata()

        if with_defaults:
            network_data.with_defaults()
        if eth0_ip:
            network_data.with_ip(ip=eth0_ip)
        if eth0_nameservers:
            network_data.with_nameservers(nameservers=eth0_nameservers)
        if eth0_gateway:
            network_data.with_gateway(gateway=eth0_gateway)
        if ssid and password:
            Console.info(f'Providing WiFi access to {name}')
            network_data.with_access_points(ssid=ssid, password=password)\
            .with_dhcp4(interfaces='wifis', interface='wlan0', dhcp4=True)\
            .with_optional(interfaces='wifis', interface='wlan0', optional=True)

        if self.debug:
            Console.info(f'Network data for {name}:\n' + str(network_data))

        return network_data

    def get_hosts_for(self, name=None):
        """
        Given a hostname, return a list of ':' separated strings of the form:

        ip:hostname

        for all hosts with ips in the inventory. Also includes mapping for own hostname in the form of 127.0.0.1:{name}

        For example, if inventory has worker001 with ip 10.1.1.1, worker002 with ip 10.1.1.2, worker003 with ip 10.1.1.3,
        then:

        self.get_hosts_for(name='worker001') returns ['127.0.0.1:worker001', '10.1.1.2:worker002', '10.1.1.3:worker003']

        Do not rely on the order of the result here
        """
        if name is None:
            raise Exception('name arg supplied is None')
        if not self.inventory.has_host(name):
            raise Exception(f'{name} could not be found in {self.inventory.filename}')

        result = [f'127.0.0.1:{name}']
        for node in self.nodes:
            if node['ip'] and name != node['host']:
                host = node['host']
                ip = node['ip']
                result += [f'{ip}:{host}']
        return result

    def generate_ssh_key(self,hostname):
        Shell.execute('mkdir', '-p ~/.cloudmesh/cmburn')
        Shell.run(f'ssh-keygen -q -N "" -C "ubuntu@{hostname}" -f '
                  f'~/.cloudmesh/cmburn/id_rsa')
        priv_key = readfile('~/.cloudmesh/cmburn/id_rsa').strip()
        pub_key = readfile('~/.cloudmesh/cmburn/id_rsa.pub').strip()
        self.manager_public_key = pub_key
        Shell.execute('rm', path_expand('~/.cloudmesh/cmburn/id_rsa'))
        Shell.execute('rm', path_expand('~/.cloudmesh/cmburn/id_rsa.pub'))
        return priv_key,pub_key

