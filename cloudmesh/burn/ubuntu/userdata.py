import yaml

class Userdata:
    HEADER = "#cloud-config"
    def __init__(self):
        self.content = {}

    def __str__(self):
        return Userdata.HEADER + '\n' + yaml.dump(self.content)
    def write(self, filename=None):
        raise NotImplementedError
