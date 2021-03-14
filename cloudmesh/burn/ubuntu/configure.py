from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.burn.ubuntu.networkdata import Networkdata
from cloudmesh.burn.ubuntu.cloudinit import Cloudinit
from cloudmesh.common.util import readfile
from cloudmesh.inventory.inventory import Inventory

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

    def __init__(self, inventory=None, cluster=None):
        self.network_conf = None # Some call to Networkdata.build()
        self.user_data_conf = None # Some call to Userdata.build()

        if inventory:
            self.inventory = Inventory(inventory)
        else:
            self.inventory = Inventory()

        if cluster is not None:
            self.nodes = self.inventory.find(cluster=cluster)
        else:
            self.nodes = self.inventory.find(service='manager') + self.inventory.find(service='worker')

    def build_user_data(self, name=None, with_defaults=True):
        """
        Given a name, get its config from self.inventory and create a Userdata object
        """
        if name is None:
            raise Exception('name arg supplied is None')
        elif not self.inventory.has_host(name):
            raise Exception(f'Could not find {name} in {self.inventory.filename}')

        # Get the current configurations from inventory
        hostname = self.inventory.get(name=name, attribute='host')
        keyfile = self.inventory.get(name=name, attribute='keyfile')
        if keyfile:
            keys = readfile(keyfile).strip().split('\n')
        else:
            keys = None

        # Build Userdata
        user_data = Userdata()

        if with_defaults:
            user_data.with_locale().with_net_tools()
        if hostname:
            user_data.with_hostname(hostname=hostname)
        if keys:
            # Disable password auth in favor of key auth
            user_data.with_ssh_password_login(ssh_pwauth=False)
            user_data.with_authorized_keys(keys=keys)
        else:
            user_data.with_default_user().with_ssh_password_login()
        return user_data

    def build_network_data(self, name=None, ssid=None, password=None, with_defaults=True):
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
            network_data.with_access_points(ssid=ssid, password=password)\
            .with_dhcp4(interfaces='wifis', interface='wlan0', dhcp4=True)\
            .with_optional(interfaces='wifis', interface='wlan0', optional=True)

        return network_data

    def write(self):
        cloudinit = Cloudinit()
        userdata = Userdata()
        networkdata = Networkdata()

        cloudinit.write()
        userdata.write()
        networkdata.write()
