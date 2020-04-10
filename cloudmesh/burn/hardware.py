import os
import socket


class Hardware(object):

    @staticmethod
    def is_pi():
        return \
            os.uname()[4][:3] == 'arm' and \
            'Raspberry' in Hardware.model()

    @staticmethod
    def get_mac(interface='eth0'):
        # noinspection PyBroadException
        try:
            address = open('/sys/class/net/%s/address' % interface).read()
        except:
            address = "00:00:00:00:00:00"
        return address[0:17]

    @staticmethod
    def get_ethernet():
        interface = None
        # noinspection PyBroadException
        try:
            for root, dirs, files in os.walk('/sys/class/net'):
                for directory in dirs:
                    if directory[:3] == 'enx' or directory[:3] == 'eth':
                        interface = directory
        except:
            interface = "None"
        return interface

    @staticmethod
    def model():
        # noinspection PyBroadException
        try:
            model_str = open('/sys/firmware/devicetree/base/model').read()
        except:
            model_str = "unkown"

        return model_str

    @staticmethod
    def hostname():
        return socket.gethostname()

    @staticmethod
    def fqdn():
        return socket.getfqdn()


"""
eth0 = Hardware.get_mac('eth0')
wan = Hardware.get_mac('wlan0')

print(eth0)

print(wan)

print(os.uname()[4][:3] == 'arm')

print(Hardware.model())
print(Hardware.is_pi())
print(Hardware.hostname())
print(Hardware.fqdn())
"""
