from cloudmesh.common.util import sudo_readfile
from cloudmesh.common.util import sudo_writefile
from cloudmesh.common.sudo import Sudo
import os

"""
hostname = "red"
content = sudo_readfile("/Volumes/rootfs/etc/hosts", split=False)
content = content.replace("raspberrypi", f"{hostname}\n#")

print(content)

sudo_writefile("/Volumes/rootfs/etc/hosts", content)
"""



# Sudo.expire()
Sudo.password()
#result = Sudo.execute("cat /etc/hosts", debug=True)

#result = Sudo.execute("cat /etc/hosts", decode=False, debug=True)

content = Sudo.readfile("/Volumes/rootfs/etc/hosts", split=True, decode=True)


print ("content")
print(content)

hostname = "red"

data = "\n".join(
    ['127.0.0.1\tlocalhost',
     '::1\t\tlocalhost ip6-localhost ip6-loopback',
     'ff02::1\t\tip6-allnodes',
     'ff02::2\t\tip6-allrouters',
     '',
     f'127.0.1.1\t\t{hostname}',
     '#',
     '10.1.1.1\tred',
     '10.1.1.2\tred01',
     "#"]
)

print(data)


result = Sudo.writefile("/Volumes/rootfs/etc/hosts", data)
print(result)

print()
os.system("cat /Volumes/rootfs/etc/hosts")
print()
