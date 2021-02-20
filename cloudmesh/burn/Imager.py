import os
from cloudmesh.common.Shell import Shell

from cloudmesh.burn.image import Image
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_pi
from cloudmesh.burn.util import os_is_mac
from cloudmesh.common.console import Console
from cloudmesh.common.sudo import Sudo


class Imager:

    @staticmethod
    def installed():
        r = Shell.which("rpi-imager")
        return r is not None

    @staticmethod
    def install(force=False):
        if os_is_mac():
            return
        if not Imager.installed() or force:
            if os_is_linux() or os_is_pi():
                Sudo.password()
                os.system("sudo apt uninstall -y rpi-imager")
            else:
                Console.warning("Installation is not supported")

    @staticmethod
    def fetch(tag=["latest-lite"]):
        Image.create_version_cache()
        file = Image().fetch(tag=tag)

        return file

    @staticmethod
    def launch(file=None):

        if file is not None:

            if not str(file).endswith(".img"):
                raise ValueError(f"file {file} does not end with .img")

            if not os.path.exists(file):
                raise ValueError(f"image file {file} does not exist")

        elif file is None:
            file = ""

        Imager.install()

        if os_is_linux() or os_is_pi():
            Sudo.password()
            os.system(f"sudo rpi-imager {file}")
        elif os_is_mac():
            os.system(f"/Applications/Raspberry\ Pi\ Imager.app/Contents/MacOS/rpi-imager {file} "  # noqa: W605
                      "> /dev/null 2>&1")  # noqa: W605
