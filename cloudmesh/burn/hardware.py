import os
import socket


class Hardware(object):

    @staticmethod
    def is_pi():
        """
        Checks if its called on a PI

        :return: returns true if this is called on a Pi
        :rtype: bool
        """
        return os.uname()[4][:3] == 'arm' and 'Raspberry' in Hardware.model()

    @staticmethod
    def get_mac(interface='eth0'):
        """
        Get the mac address

        :param interface: the network interface name
        :type interface: str
        :return: mac address
        :rtype: str
        """
        # noinspection PyBroadException
        try:
            address = open('/sys/class/net/%s/address' % interface).read()
        except Exception as e:
            address = "00:00:00:00:00:00"
        return address[0:17]

    @staticmethod
    def get_ethernet():
        """
        TODO: describe

        :return:
        :rtype:
        """
        interface = None
        # noinspection PyBroadException
        try:
            for root, dirs, files in os.walk('/sys/class/net'):
                for directory in dirs:
                    if directory[:3] == 'enx' or directory[:3] == 'eth':
                        interface = directory
        except Exception as e:
            interface = "None"
        return interface

    @staticmethod
    def model():
        """
        TODO: describe

        :return:
        :rtype:
        """
        # noinspection PyBroadException
        try:
            model_str = open('/sys/firmware/devicetree/base/model').read()
        except Exception as e:
            model_str = "unkown"

        return model_str

    @staticmethod
    def hostname():
        """
        The hostname

        :return: the hostname
        :rtype: str
        """
        return socket.gethostname()

    @staticmethod
    def fqdn():
        """
        TODO: describe

        :return:
        :rtype:
        """
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
