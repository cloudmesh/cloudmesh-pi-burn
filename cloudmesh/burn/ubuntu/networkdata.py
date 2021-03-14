import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand, writefile

class Networkdata:
    """
    A builder for content in the network-config file with cloud-init

    https://cloudinit.readthedocs.io/en/latest/topics/network-config.html
    """

    def __init__(self, version=2, default=False):
        # Dict will be dumped into YAML string
        self.content = {"version": 2, "ethernets": {}, "wifis": {}}
        if default:
            self.__default__()

    def __str__(self):
        return yaml.dump(self.content)

    def write(self, filename=None):
        """
        Writes a file to a location. Safe write for files on mounted partitions
        """
        tmp_location = path_expand('~/.cloudmesh/network-data.tmp')
        writefile(tmp_location, str(self))
        Shell.execute('mv', [tmp_location, filename])

    def with_ip(self, interfaces='ethernets', interface='eth0', ip=None):
        if ip is None:
            raise Exception("ip argument supplied is None")

        # If subnet not specified, default to 255.255.255.0
        if "/" not in ip:
            ip += "/24"

        if interface not in self.content[interfaces]:
            self.content[interfaces][interface] = {}

        self.content[interfaces][interface]['addresses'] = [ip] # Expects a list value
        self.content[interfaces][interface]['dhcp4'] = 'no'
        return self

    def with_gateway(self, interfaces='ethernets', interface='eth0', gateway=None):
        if gateway is None:
            raise Exception("gateway argument supplied is None")

        if interface not in self.content[interfaces]:
            self.content[interfaces][interface] = {}

        self.content[interfaces][interface]['gateway4'] = gateway
        return self

    def with_nameservers(self, interfaces='ethernets', interface='eth0', nameservers=None):
        if nameservers is None:
            raise Exception("nameservers argument suppliled is None")
        if type(nameservers) != list:
            raise TypeError("Expected type of nameservers to be a list")

        if interface not in self.content[interfaces]:
            self.content[interfaces][interface] = {}

        self.content[interfaces][interface]['nameservers'] = {'addresses': nameservers}
        return self

    def with_dhcp4(self,interfaces='ethernets', interface='eth0',dhcp4=True):
        if interface not in self.content[interfaces]:
            self.content[interfaces][interface] = {}

        self.content[interfaces][interface]['dhcp4'] = dhcp4

    def with_defaults(self, interfaces='ethernets', interface='eth0'):
        """
        Unsure if this is needed, however these params were included in the default config, so we keep
        """
        if interface not in self.content[interfaces]:
            self.content[interfaces][interface] = {}

        self.content[interfaces][interface]['match'] = {"driver": "bcmgenet smsc95xx lan78xx"}
        self.content[interfaces][interface]['set-name'] = interface
        return self
    
    def __default__(self):
        """
        Set the default configuration the one that comes burnt with the ubuntu server OS

        Captured with
        $ grep - Fv \  # /{mountpoint}/network-config
        (Removes comments)
        """
        self.content['ethernets'] = {
            "eth0": {
                "match": {
                    "driver": "bcmgenet smsc95xx lan78xx"
                },
                "set-name": "eth0",
                "dhcp4": True,
                "optional": True
            }
        }

"""
Example:
d = Networkdata()\
    .with_ip(ip="10.1.1.10")\
    .with_gateway(gateway="10.1.1.1")\
    .with_nameservers(nameservers=['8.8.8.8', '8.8.4.4'])\
    .with_defaults()

print(d)

To write to file:
d = Networkdata()\
    .with_ip(ip='10.1.1.10')\
    .with_gateway(gateway='10.1.1.1')\
    .with_nameservers(nameservers=['8.8.8.8', '8.8.4.4'])\
    .with_defaults().write(filename='test.tmp')

Verification of config syntax:

On an ubuntu machine with cloud-init, the following can be taken to verify syntax

1. Paste string output of build() into an arbitrary file (test.txt)
2. Run the following command on an ubuntu machine with cloud-init

cloud-init devel schema --config-file test.txt

"""
