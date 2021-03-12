from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.burn.ubuntu.networkdata import Networkdata
from cloudmesh.burn.ubuntu.cloudinit import Cloudinit

class Configure:

    def __init__(self, inventory=None):
        self.network_conf = None # Some call to Networkdata.build()
        self.user_data_conf = None # Some call to Userdata.build()

    def write(self):
        cloudinit = Cloudinit()
        userdata = Userdata()
        networkdata = Networkdata()

        cloudinit.write()
        userdata.write()
        networkdata.write()
