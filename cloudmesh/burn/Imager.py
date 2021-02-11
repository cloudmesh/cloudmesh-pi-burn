import os
from cloudmesh.common.Shell import Shell

from cloudmesh.burn.image import Image
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_pi
from cloudmesh.common.console import Console

class Imager:


    def installed():
        r = Shell.which("rpi-imager")
        return r is not None
    
    @staticmethod
    def install(force=False):
        if not installed or force:
            if os_is_linux() or os_is_pi():
                os.system("sudo apt uninstall -y rpi-imager")
            else:
                Console.warning("Instalation is not supported")
    @staticmethod
    def download(tag=["latest-lite"]):
        pass

    @staticmethod
    def format(file=None):

        if file is not None:
            if not os.path.exists(file):
                raise ValueError(f"image file {file} does not exist")

            if not file.endswith(".img"):
               raise ValueError(f"file {file} does not end with .img")
            
        elif file is None:
            file = ""
            
        Imager.install()

        os.system(f"sudo rpi-imager {file}")
