from cloudmesh.burn.windowssdcard import WindowsSDCard
from cloudmesh.burn.sdcard import SDCard

device = SDCard()
card = WindowsSDCard()

# print(card.disk_info())

# print(card.get_disk(volume="5"))

print(card.info())
