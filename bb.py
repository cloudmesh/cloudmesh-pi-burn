import os
from cloudmesh.common.util import path_expand

cmdline = \
    {
        "sdcard": "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh",
        "lite": "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target",
        "full": "console=serial0,115200 console=tty1 root=PARTUUID=f4481065-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh splash plymouth.ignore-serial-consoles systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target"
     }

def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: teh content
    :return:
    """
    outfile = open(path_expand(filename), 'w')
    outfile.write(content)
    outfile.flush()
    os.fsync(outfile)


os.system("cms burn sdcard latest-lite --disk=4")
os.system(f"cp firstrun.sh /f/")

cmdline_file = "f:/cmdline.txt"
writefile(cmdline_file, cmdline["lite"])
