from cloudmesh.burn.windowssdcard import Diskpart
from cloudmesh.common.Printer import Printer
Diskpart.help()
data = Diskpart.list_disk()
print (Printer.write(data,
                     order=['Disk', '###', 'Status', 'Size', 'Free', 'Dyn', 'Gpt']
))

data = Diskpart.list_volume()
print (Printer.write(data,
                     order=['Volume', '###', 'Ltr', 'Label', 'Fs', 'Type', 'Size', 'Status', 'Info']
                     ))

data = Diskpart.list_partition(disk=0)
print (Printer.write(data,
                     order=['Partition', '###', 'Type', 'Size', 'Offset']))
data = Diskpart.list_partition(disk=1)
print (Printer.write(data,
                     order=['Partition', '###', 'Type', 'Size', 'Offset']))
data = Diskpart.list_partition(disk=2)
print (Printer.write(data,
                     order=['Partition', '###', 'Type', 'Size', 'Offset']))

data = Diskpart.list_device()
print (Printer.write(data, order=['major', 'minor', '#blocks', 'name', 'win-mounts']))

Diskpart.automount(False)
Diskpart.automount(True)
