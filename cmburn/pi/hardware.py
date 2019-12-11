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
    try:
      str = open('/sys/class/net/%s/address' %interface).read()
    except:
      str = "00:00:00:00:00:00"
    return str[0:17]

  @staticmethod
  def get_ethernet():
    try:
      for root,dirs,files in os.walk('/sys/class/net'):
        for dir in dirs:
          if dir[:3]=='enx' or dir[:3]=='eth':
            interface=dir
    except:
      interface="None"
    return interface
  
  @staticmethod
  def model():
    try:
      str = open('/sys/firmware/devicetree/base/model').read()
    except:
      str = "unkown"

    return str

  def hostname():
      return socket.gethostname()

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
