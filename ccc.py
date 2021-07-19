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
#  python ccc.py red SSID WIFIPASSWD PASSWD format
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
# echo "$FIRSTUSER:"'{hash}' | chpasswd -e
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


