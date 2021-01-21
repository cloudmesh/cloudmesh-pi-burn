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
        if self.os == "raspberry" and host =="darwin":
            raise Path("/Volume/boot")
            # return "/volume"
