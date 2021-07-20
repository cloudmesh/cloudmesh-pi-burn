import os
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.burn.raspberryos.cmdline import Cmdline
from passlib.hash import sha256_crypt

import sys
import io
from passlib.utils import pbkdf2
import binascii, sys

# USE
#  python ddd.py red SSID WIFIPASSWD PASSWD format
#

def psk_encrypt(ssid, password):
    value = pbkdf2.pbkdf2(str.encode(password), str.encode(ssid), 4096, 32)
    return binascii.hexlify(value).decode("utf-8")


#def encrypt_user_passwd(passwd):
#    hash = sha512_crypt.encrypt(passwd)
#    return hash

def encrypt_user_passwd(password):
    # repeatable salt if needed for testing
    # hash = sha256_crypt.using(salt='qY2oeR.YpL', rounds=5000).hash(
    # self.password)
    hash = sha256_crypt.using(rounds=5000).hash(password)
    return hash

letter = "f"
disk = "4"
host = sys.argv[1]
ssid = sys.argv[2]
wifi_password = sys.argv[3]
user_password = sys.argv[4]
try:
    with_format = sys.argv[5] == "format"
except:
    with_format = False

encrypted_wifi_password = psk_encrypt(ssid, wifi_password)

hash = encrypt_user_passwd(user_password)
print(hash)

# echo "$FIRSTUSER:"'{hash}' | chpasswd -e
# fstring needs to be done carefully ....as there s { in it needs to be masked

firstrun = \
f'''
#!/bin/bash

set +e

CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \\t\\n\\r"`
echo red >/etc/hostname
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\\t{host}/g" /etc/hosts
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
echo "$FIRSTUSER:"'{hash}' | chpasswd -e
systemctl enable ssh
cat >/etc/wpa_supplicant/wpa_supplicant.conf <<'WPAEOF'
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1

update_config=1
network={{
	ssid="{ssid}"
	psk="{encrypted_wifi_password}"
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

sshkey = readfile(path_expand("~/.ssh/id_rsa.pub"))

# BUG the script from anthony country=None was set and not country=US

# SSH KEY read from ~/.ssh/id_rsa.pub
#FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
#FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
#install -o "$FIRSTUSER" -m 700 -d "$FIRSTUSERHOME/.ssh"
#install -o "$FIRSTUSER" -m 600 <(echo "{sshkey}") "$FIRSTUSERHOME/.ssh/authorized_keys"
#cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
#echo 'PasswordAuthentication no' >>/etc/ssh/sshd_config


firtsrun = '''
#!/bin/bash
set +e
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \\t\\n\\r"`
echo red >/etc/hostname
sed -i "s/127.0.1.1.*$CURRENT_HOSTNAME/127.0.1.1\\t{host}/g" /etc/hosts
echo 10.1.1.2   red01 >> /etc/hosts
echo "interface eth0" >> /etc/dhcpcd.conf
echo "static ip_address=10.1.1.1/24" >> /etc/dhcpcd.conf
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
echo "$FIRSTUSER:"'{hash}' | chpasswd -e
systemctl enable ssh
sudo sed -i 's/#net\.ipv4\.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"
sudo sed -i '$i iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

cat >/etc/wpa_supplicant/wpa_supplicant.conf <<WPAEOF
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
ap_scan=1
update_config=1
network={{
	ssid="{ssid}"
	psk="{encrypted_wifi_password}"
}}
WPAEOF
chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
rfkill unblock wifi
for filename in /var/lib/systemd/rfkill/*:wlan ; do
    echo 0 > $filename
done
rm -f /etc/xdg/autostart/piwiz.desktop
rm -f /etc/localtime
echo "America/Indiana/Indianapolis" >/etc/timezone
dpkg-reconfigure -f noninteractive tzdata
cat >/etc/default/keyboard <<KBEOF
XKBMODEL="pc105"
XKBLAYOUT="en_US.UTF-8"
XKBVARIANT=""
XKBOPTIONS=""
KBEOF
dpkg-reconfigure -f noninteractive keyboard-configuration
rm -f /boot/firstrun.sh
sed -i 's| systemd.run.*||g' /boot/cmdline.txt
exit 0
#
'''

firstrun = firstrun.strip().splitlines()
firstrun = "\n".join(firstrun) + "\n"





def writefile(filename, content):
    """
    writes the content into the file
    :param filename: the filename
    :param content: the content
    :return:
    """
    outfile = io.open(path_expand(filename), 'w', newline='\n')
    outfile.write(content)
    outfile.flush()
    os.fsync(outfile)

print (firstrun)


if with_format:
    os.system(f"cms burn sdcard latest-lite --disk={disk}")

cmdline_file = letter + ":/cmdline.txt"
cmdline = Cmdline()
cmdline.update(cmdline_file, version="lite")

firstrun_file = letter + ":/firstrun.sh"
writefile(firstrun_file, firstrun)

#os.system(f"cp firstrun.sh /{letter}/")


