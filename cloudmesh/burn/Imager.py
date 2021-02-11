import os
from cloudmesh.common.Shell import Shell

class Imager:


    def installed():
        r = Shell.which("rpi-imager")
        return r is not None
    
    @staticmethod
    def install():
        # TODO: if installed skip
        os.system("sudo apt install -y rpi-imager")

    @staticmethod
    def install(force=false):
        if not installed or force:
            os.system("sudo apt uninstall -y rpi-imager")

    def format(file=None):

        if file is not None:
            if not os.path.exists(file):
                raise ValueError("image file does not exist")

            if not file.endswith(".img")
               raise ValueError("file {file} does not end with .img")
            
        elif file is None:
            file = ""
            
        Imager.install()
        os.system("sudo rpi-imager {file}")
