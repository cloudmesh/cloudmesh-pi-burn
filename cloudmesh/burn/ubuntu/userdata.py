import yaml

from cloudmesh.burn.sdcard import SDCard
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand, writefile

class Userdata:
    HEADER = "#cloud-config"
    def __init__(self):
        self.content = {}

    def __str__(self):
        return Userdata.HEADER + '\n' + yaml.dump(self.content)

    def write(self, filename=None):
        """
        Writes a file to a location. Safe write for files on mounted partitions
        """
        tmp_location = path_expand('~/.cloudmesh/user-data.tmp')
        writefile(tmp_location, str(self))
        Shell.execute('mv', [tmp_location, filename])
