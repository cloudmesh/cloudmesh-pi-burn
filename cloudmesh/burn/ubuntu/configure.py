from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.burn.ubuntu.networkdata import Networkdata
from cloudmesh.burn.ubuntu.cloudinit import Cloudinit

class Configure:

    def __init__(self):
        raise NotImplementedError

    def write(self, filename=None):
        cloudinit = Cloudinit()
        userdata = Userdata()
        networkdata = Networkdata()

        cloudinit.write()
        userdata.write()
        networkdata.write()
