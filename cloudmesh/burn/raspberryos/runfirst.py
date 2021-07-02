import textwrap
from cloudmesh.common.util import path_expand, readfile, writefile
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from passlib.hash import sha256_crypt
from cloudmesh.burn.util import os_is_windows


def dedent(content):
    return textwrap.dedent(content).strip()


class Runfirst:
    """
    A builder-like class for constructing a firstrun.sh script to be run
    at boot by a Raspberry Pi
    """

    SCRIPT_NAME = 'firstrun.sh'

    def __init__(self):
        self.key = None
        self.hostname = None
        self.timezone = None
        self.ssid = None
        self.wifipasswd = None
        self.locale = None
        self.country = None
        self.script = None
        self.etc_hosts = None
        self.static_ip_info = None
        self.password = None
        self.bridge = None

    def info(self):
        print("Key:     ", self.key[0:20], "...", self.key[-20:].strip())
        print("Hostname:", self.hostname)
        print("Timezone:", self.timezone)
        print("SSID:    ", self.ssid)
        print("Locale:  ", self.locale)
        print("Country: ", self.country)
        print()

    def set_key(self, key=None):
        if key is None:
            self.key = readfile("~/.ssh/id_rsa.pub").strip()
        else:
            self.key = key

    def enable_bridge(self):
        """
        Enables the wifi bridge
        """
        self.bridge = True

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
        self.etc_hosts = dict(zip(names, ips))

    def set_wifi(self, ssid, passwd, country="US"):
        """
        sets the wifi password

        :param ssid:
        :type ssid:
        :param passwd:
        :type passwd:
        :return:
        :rtype:
        """
        # Same as ubuntu/ previous raspberry, write to boot partition and then
        # just add to first run to place it in place
        self.ssid = ssid
        self.wifipasswd = passwd
        self.country = country

    def set_locale(self, timezone=None, locale=None):
        """
        sets the locale of the OS

        :return:
        :rtype:
        """
        # same as ubuntu or previous raspberry os. E.g. get form current
        # machine and create the KBEOF
        # see the get script how they include it.
        #
        if not timezone:
            self.timezone = "America/Indiana/Indianapolis"
        else:
            self.timezone = timezone
        if not locale:
            self.locale = "us"
        else:
            self.locale = locale

    def set_static_ip(self, interface='eth0', ip=None, subnet_mask='24', router=None, dns=None):
        """
        Sets a static IP on the specified interface
        """
        if ip is None:
            raise Exception("Missing ip arg. None supplied")

        self.static_ip_info = [interface, ip, subnet_mask, router, dns]

    def set_password(self, password=None):
        if password is None:
            raise Exception("Missing password arg. None supplied")

        self.password = password

    def _get_bridge_script(self):
        """
        If self.bridge is True, then enable a bridge from eth0 to wlan0
        """
        if self.bridge:
            script = []
            script += ["sudo sed -i 's/#net\\.ipv4\\.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf"]
            script += ["sudo iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT"]
            script += ["sudo iptables -A FORWARD -i wlan0 -o eth0 -m state --state ESTABLISHED,RELATED -j ACCEPT"]
            script += ["sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE"]
            script += ['sh -c "iptables-save > /etc/iptables.ipv4.nat"']
            script += ["sudo sed -i '$i iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local"]
            return '\n'.join(script)
        else:
            return ""

    def _get_password_script(self):
        #
        # BUG: hash should be hash_str, you can not use hash and .hash as function
        #
        script = []
        if not self.password:
            return ""
        # repeatable salt if needed for testing
        # hash = sha256_crypt.using(salt='qY2oeR.YpL', rounds=5000).hash(
        # self.password)
        hash = sha256_crypt.using(rounds=5000).hash(self.password)
        script.append(f'echo "$FIRSTUSER:"\'{hash}\' | chpasswd -e')
        return '\n'.join(script)

    def _get_static_ip_script(self):
        """
        If the self.interface_ip pair is not None, then return the script
        to configure it
        """
        script = []
        if not self.static_ip_info:
            return ""
        interface, ip, mask, router, dns = self.static_ip_info
        script.append(f'echo "interface {interface}" >> /etc/dhcpcd.conf')
        script.append(f'echo "static ip_address={ip}/{mask}" >> /etc/dhcpcd.conf')
        if router:
            script.append(f'echo "static routers={router}" >> /etc/dhcpcd.conf')
        if dns:
            dns = ' '.join(dns)
            script.append(f'echo "static domain_name_servers={dns}" >> /etc/dhcpcd.conf')
        return '\n'.join(script)

    def _get_etc_hosts_script(self):
        """
        If self.etc_hosts is not None, then we must append the known hosts
        to /etc/hosts
        """
        script = []
        if self.etc_hosts:
            for hostname, ip in self.etc_hosts.items():
                script.append(f"echo {ip}\t{hostname} >> /etc/hosts")
        return '\n'.join(script)

    def _get_wifi_config(self):
        if self.ssid:
            script = f"""
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
                done"""
            return dedent(script)
        else:
            return ""

    def _writefile(self, name, content):
        data = dedent(f"""
        cat > {name} <<EOF
        {content}
        EOF
        """)
        return data

    def get_manager(self):
        return self.get()

    def get_worker(self):
        return self.get()

    def write(self, filename=None):
        """
        Write the cmdline config to the specified filename
        """
        if filename is None:
            raise Exception("write called with no filename")
        if self.script is None:
            raise Exception("no script found. Did you run .get() first?")

        tmp_location = path_expand('~/.cloudmesh/cmburn/firstrun.sh.tmp')
        writefile(tmp_location, self.script)
        if os_is_windows():
            Shell.run(f'cat {tmp_location} | tee {filename}')
        else:
            Shell.run(f'cat {tmp_location} | sudo tee {filename}')
        Shell.execute('rm', arguments=[tmp_location])

    def get(self, verbose=False):
        # NEEDS TO BE INDENTED THIS WAY
        # OR ELSE WRITTEN SCRIPT WILL NOT WORK
        self.script = dedent(f'''
#!/bin/bash
set +e
CURRENT_HOSTNAME=`cat /etc/hostname | tr -d " \\t\\n\\r"`
echo {self.hostname} >/etc/hostname
sed -i "s/127\\.0\\.1\\.1.*$CURRENT_HOSTNAME/127.0.1.1\\t{self.hostname}/g" /etc/hosts
{self._get_etc_hosts_script()}
{self._get_static_ip_script()}
FIRSTUSER=`getent passwd 1000 | cut -d: -f1`
FIRSTUSERHOME=`getent passwd 1000 | cut -d: -f6`
install -o "$FIRSTUSER" -m 700 -d "$FIRSTUSERHOME/.ssh"
install -o "$FIRSTUSER" -m 600 <(echo "{self.key}") "$FIRSTUSERHOME/.ssh/authorized_keys"
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
echo 'PasswordAuthentication no' >>/etc/ssh/sshd_config
systemctl enable ssh
{self._get_bridge_script()}
{self._get_password_script()}
{self._get_wifi_config()}
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
rm -f /boot/{Runfirst.SCRIPT_NAME}
sed -i 's| systemd.run.*||g' /boot/cmdline.txt
exit 0
        ''')

        if verbose:
            Console.info(f'{Runfirst.SCRIPT_NAME}.sh for {self.hostname}')
            Console.info(self.script)
        return self.script
