from cloudmesh.burn.windowssdcard import WindowsSDCard
from cloudmesh.common.util import yn_choice
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.common.console import Console

device = SDCard()
card = WindowsSDCard()
info = card.info()
if len(info) > 1:
    Console.error("Too many SD Cards found")
drive = info[0]["drive"]
print(device.info())
answer = yn_choice(f"Is the drive {drive}: the drive you would like to format")

if answer:
    print("Great!")
    r = card.format_drive(drive=drive,unmount=False)
    print(r)

# card = WindowsSDCard()
# # card.automount()
# # card.mount(drive="D:")
# card.mount(label="UNTITLED")
# # print("aaa")
# # # card.unmount("D:")
# # print("bbb")
#
# # card.assign_drive("UNTITLED")
#
# # card.diskmanager()
