from cloudmesh.burn.windowssdcard import WindowsSDCard
from cloudmesh.burn.sdcard import SDCard

device = SDCard()
card = WindowsSDCard()

#
#
# card.assign_drive(volume=5,drive="D")
# injecting a volume that is already injected
print("r_inject")
r_inject = card.inject(volume="5")

# formatting mounted and injected volume
# r_format = card.format_drive(drive="D")
# print("r_format",r_format)

# # Should list a card without label or volume
# card.ls()
#
# print('aaa')
# # injecting recently formatted card
# r_inject = card.inject(volume=5)

# mounting injected card



#
# def inject_all():
#     #get all volumes
#     info = card.info()
#     #filter for volumes that aren't injected
#     info = WindowsSDCard.filter_info(info,{"type":"Removable","label":"","drive":""})
#     print(info)
#
#
#     for device in info:
#         card.diskpart(command=f"select volume {device['volume']}")
#         card.diskpart(command="online volume")
#         if device["drive"] != "":
#             r_mount = card.mount(drive=device["drive"],label=device["label"])
#             print("r_mount",r_mount)
#         else:
#             r_mount = card.mount(label=device["label"])
#             print("r_mount",r_mount)
#
# inject(volume=)
# card.ls()
