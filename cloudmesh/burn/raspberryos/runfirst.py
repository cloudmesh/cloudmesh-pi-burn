import textwrap
from cloudmesh.common.util import readfile


def dedent(content):
    return textwrap.dedent(content).strip()


class Runfirst:

    def __init__(self):
        self.key = None
        self.hostname = None
        self.timezone = None

    def info(self):
        print ("Key:     ", self.key[0:20], "...", self.key[-20:].strip())
        print ("Hostname:", self.hostname)
        print ("Timezone:", self.timezone)
        print()

    def set_key(self, key=None):
        if key == None:
            self.key = readfile("~/.ssh/id_rsa.pub")
        else:
            self.key = key

    def set_hostname(self, name):
        #
        # I do not yet know how they write the hostname ... into /etc/hostname
        #
        self.hostname = name

    def set_hosts(self, names, ips):
        """
        Sets the /etc/hosts file information

        :param names: list of names
        :type names: list
        :param ips: list of ips
        :type ips: list
        """
        pass

    def set_wifi(self, ssid, passwd, country="US"):
        """
        sets the wifi password

        :param ssid:
        :type ssid:
        :param password:
        :type password:
        :return:
        :rtype:
        """
        # Same as ubuntu/ previous raspberry, write to boot partition and then
        # just add to first run to place it in place
        self.ssid = ssid
        self.wifipasswd = passwd
        self.country = country

    def set_locale(self):
        """
        sets the locale of the OS

        :return:
        :rtype:
        """
        # same as ubuntu or previous raspberry os. E.g. get form current
        # machine and create the KBEOF
        # see the get script how they include it.
        #
        self.timezone = "America/Indianapolis"
        self.locale = "us"

    def _writefile(self, name, content):
        data = dedent(f"""
        cat > {name} <<EOF
        {content}
        EOF
        """)

    def get_manager(self):
        return self.get()

    def get_worker(self):
        return self.get()

    def get(self):
        self.script = dedent(f'''
        #!/bin/bash
        set +e
        CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \\t\\n\\r"`
        echo {self.hostname} >/etc/hostname
        sed -i "s/127\\.0\\.1\\.1.*$CURRENT_HOSTNAME/127.0.1.1\\t{self.hostname}/g" /etc/hosts
        FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
        FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
        install -o "$FIRSTUSER" -m 700 -d "$FIRSTUSERHOME/.ssh"
        install -o "$FIRSTUSER" -m 600 <(echo "{self.key}") "$FIRSTUSERHOME/.ssh/authorized_keys"
        echo 'PasswordAuthentication no' >>/etc/ssh/sshd_config
        systemctl enable ssh
        cat >/etc/wpa_supplicant/wpa_supplicant.conf <<WPAEOF
        country={self.country}
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        ap_scan=1
        update_config=1
        network={{
            ssid="{self.ssid}"
            psk="{self.wifipasswd}"
        }}
        WPAEOF
        chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
        rfkill unblock wifi
        for filename in /var/lib/systemd/rfkill/*:wlan ; do
          echo 0 > $filename
        done
        rm -f /etc/xdg/autostart/piwiz.desktop
        rm -f /etc/localtime
        echo "{self.timezone}" >/etc/timezone
        dpkg-reconfigure -f noninteractive tzdata
        cat >/etc/default/keyboard <<KBEOF
        XKBMODEL="pc105"
        XKBLAYOUT="{self.locale}"
        XKBVARIANT=""
        XKBOPTIONS=""
        KBEOF
        dpkg-reconfigure -f noninteractive keyboard-configuration
        rm -f /boot/firstrun.sh
        sed -i 's| systemd.run.*||g' /boot/cmdline.txt
        exit 0
        ''')

        return self.script

