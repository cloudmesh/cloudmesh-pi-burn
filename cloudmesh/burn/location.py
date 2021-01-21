from pathlib import Path

class Location:

    def __init__(self, os=None, host=None):
        self.os = os or "raspberry"
        self.host = host = "raspberry"

    @property
    def volume(self):
        if self.os == "raspberry" and host =="darwin":
            raise "not supported without paragon"
            # return "/volume/???"

    @property
    def boot(self):
        if host == "darwin":
            if "raspberry" in self.os:
                return  Path("/Volume/boot")
            elif "ubuntu" in self.os:
                return  Path("/Volume/system-boot")
