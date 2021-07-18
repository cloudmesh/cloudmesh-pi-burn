import os
from cloudmesh.common.util import path_expand
import sys

host = sys.argv[1]
ssid = sys.argv[2]
wifi_password = sys.argv[3]

cmdline = \
    {
        "sdcard": "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh",
        "lite":   "console=serial0,115200 console=tty1 root=PARTUUID=9730496b-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target",
        "full":   "console=serial0,115200 console=tty1 root=PARTUUID=f4481065-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet init=/usr/lib/raspi-config/init_resize.sh splash plymouth.ignore-serial-consoles systemd.run=/boot/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target"
     }

TBD_SSID="dont know yet"
TBD_PASSWD="dont know yet" # needs to be encrypted or cleartext to start
TBD_ENCRYPTED_PASSWD_USER="dont know yet"

# we need to look how anthony did this and build up slowly

# fstring needs to be done carefully ....as there s { in it needs to be masked
firstrun = \
f'''
#!/bin/bash

set +e

CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \t\n\r"`
echo red >/etc/hostname
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\t{host}/g" /etc/hosts
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
echo "$FIRSTUSER:"'TBD_ENCRYPTED_PASSWD_USER' | chpasswd -e
systemctl enable ssh
cat >/etc/wpa_supplicant/wpa_supplicant.conf <<'WPAEOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1

update_config=1
network={{
	ssid={ssid}
	psk={wifi_password}
}}

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

print (firstrun)

sys.exit()

os.system("cms burn sdcard latest-lite --disk=4")
cmdline_file = "f:/firstrun.sh"
writefile(cmdline_file, firstrun.replace('\r\n','\n'))

#os.system(f"cp firstrun.sh /f/")

cmdline_file = "f:/cmdline.txt"
writefile(cmdline_file, cmdline["lite"].replace('\r\n','\n'))

