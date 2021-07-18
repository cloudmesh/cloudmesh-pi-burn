import os
from cloudmesh.common.util import path_expand
import sys

ssid = sys.argv[0]
password = sys.argv[1]

cmdline = \
    {
        "sdcard": "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh",
        "lite": "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target",
        "full": "console=serial0,115200 console=tty1 root=PARTUUID=f4481065-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh splash plymouth.ignore-serial-consoles systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target"
     }

TBD_SSID="dont know yet"
TBD_PASSWD="dont know yet" # needs to be encrypted or cleartext to start
TBD_ENCRYPTED_PASSWD_USER="dont know yet"

# we need to look how anthony did this and build up slowly

# fstring needs to be done carefully ....as there s { in it needs to be masked
firstrun = \
'''
#!/bin/bash

set +e

CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
echo red >/etc/hostname
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\tred/g" /etc/hosts
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
echo "$FIRSTUSER:"'TBD_ENCRYPTED_PASSWD_USER' | chpasswd -e
systemctl enable ssh
cat >/etc/wpa_supplicant/wpa_supplicant.conf <<'WPAEOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1

update_config=1
network={
	ssid="TBD_SSID"
	psk=TBD_PASSWD
}

WPAEOF
chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
rfkill unblock wifi
for filename in /var/lib/systemd/rfkill/*:wlan ; do
  echo 0 > $filename
done
rm -f /boot/firstrun.sh
sed -i 's| systemd.run.*||g' /boot/cmdline.txt
exit 0
'''

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
