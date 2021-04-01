import os
# import wget

from cloudmesh.burn.image import Image
from cloudmesh.common.Shell import Shell


class Iso:
    distribution = {
        "latest": "https://downloads.raspberrypi.org/rpd_x86/images/rpd_x86-2021-01-12/2021-01-11-raspios-buster-i386.iso"  # noqa: E501
    }

    @staticmethod
    def get(tag="latest"):
        url = Iso.distribution[tag]
        destination = Image().directory + os.path.basename(url)

        Shell.download(url, destination, provider='system')
        # wget.download(url, out=destination)
        # os.system(f'wget -O {destination} {url}')
