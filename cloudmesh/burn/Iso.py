import os
from cloudmesh.burn.image import Image


class Iso:
    distribution = {
        "latest": "https://downloads.raspberrypi.org/rpd_x86/images/rpd_x86-2021-01-12/2021-01-11-raspios-buster-i386.iso"
    }

    @staticmethod
    def get(tag="latest"):
        url = Iso.distribution[tag]
        destination = Image().directory + os.path.basename(url)

        os.system(f'wget -O {destination} {url}')
