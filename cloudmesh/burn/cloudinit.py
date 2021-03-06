import textwrap

from cloudmesh.common.Host import Host
from cloudmesh.common.parameter import Parameter


class Cloudinit:

    def __init__(self):
        self.content = []
        self.runcmd = []
        self.user = []
        self.apt = []  # not yet sure how to do that

        # runcmd must be at end and only run once

    def get(self):
        users = ""
        runcmd = ""
        content = ""
        if len(self.runcmd) > 0:
            runcmd = textwrap.dedent("""
            runcmd:
              - """ + "  - ".join(self.runcmd))

        if len(self.user) > 0:
            users = textwrap.dedent("""
            users:
            """ + "  - ".join(self.user))

        if len(self.content) > 0:
            content = "\n".join(self.content)

        return content + users + runcmd

    def __str__(self):
        return self.get()

    def __repr__(self):
        return self.get()

    def add(self, what, content):
        comment = f"#\n# Set {what}\n#\n"
        self.content.append(comment + textwrap.dedent(content).strip())

    def wifi(self):
        content = """
        # This file is generated from information provided by
        # the datasource.  Changes to it will not persist across an instance.
        # To disable cloud-init's network configuration capabilities, write a file
        # /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
        # network: {config: disabled}
        network:
            version: 2
            ethernets:
                eth0:
                    optional: true
                    dhcp4: true
            # add wifi setup information here ...
            wifis:
                wlan0:
                    optional: true
                    access-points:
                        "YOUR-SSID-NAME":
                            password: "YOUR-NETWORK-PASSWORD"
                    dhcp4: true
                """
        self.add("wifi", content)

    def static_network(self, *, hostnames, ips):
        content = """
        network-interfaces: |
          auto eth0
          iface eth0 inet static
          address 192.168.1.10
          network 192.168.1.0
          netmask 255.255.255.0
          broadcast 192.168.1.255
          gateway 192.168.1.1
        """
        self.add("static network addresses", content)

    def nameserver(self):
        content = """
        manage_resolv_conf: true
        resolv_conf:
          nameservers: ['8.8.4.4', '8.8.8.8']
          searchdomains:
            - foo.example.com
            - bar.example.com
          domain: example.com
          options:
            rotate: true
            timeout: 1
        """
        self.add("name server", content)

    def ntp(self):
        content = """
        ntp:
          servers:
            - ntp1.example.com
            - ntp2.example.com
            - ntp3.example.com
        runcmd:
          - /usr/bin/systemctl enable --now ntpd
          """
        self.add("ntp", content)

    def dhcp(self):
        # not sure how to dod this
        # we may not need immediatly as we do static
        raise NotImplementedError

    def keyboard(self):
        self.runcmd.append(
            "/usr/bin/localectl set-keymap de-latin1-nodeadkeys"
        )

    def locale(self):
        # see keyboaad and timezone
        # may need consideration for wifi country
        # not yet sure if we eneed this as it may just be done as
        # part of the other methods
        raise NotImplementedError

    def hostname(self, name):
        content = f"""
        preserve_hostname: false
        hostname: {name}
        """
        self.add("hostname", content)

    def etc_hosts(self):
        content = """
        write_files:
          - path: /etc/hosts
            permissions: '0644'
            content: |
              #Host file
              127.0.0.1   localhost localhost.localdomain

              10.252.0.1 vm0-ib0
              10.252.0.2 vm1-ib0
              10.252.0.3 vm2-ib1
        """
        self.add("/etc/hosts", content)

    def startup(self):
        # not sure if we need that
        raise NotImplementedError

    def set_key(self):
        # set key wudl be the host key?
        raise NotImplementedError

    def add_key(self):
        content = """
        #
        # Add keys
        #

        ssh_deletekeys: False
        ssh_pwauth: True
        ssh_authorized_keys:
          - ssh-rsa XXXKEY mail@example.com
        """
        self.add("keys", content)

    def add_user(self, *, name, gecos, group, groups, expire, passwd):
        """

        :param self:
        :type self:
        :param name:
        :type name:
        :param gecos: Firstname Lastname
        :type gecos: str
        :param group:
        :type group:
        :param groups:
        :type groups:
        :param expire:
        :type expire:
        :param passwd:
        :type passwd:
        :return:
        :rtype:
        """
        user = f"""
        name: {name}
        gecos: {gecos}
        primary_group: {group}
        groups: {groups}
        # selinux_user: staff_u
        # expiredate: '2012-09-01'
        # ssh_import_id: foobar
        lock_passwd: false
        passwd: {passwd}
        """
        self.user.append(user)

    def enable_ssh(self):
        # apt install need to be done differently
        # ther is a special section for that
        ssh = textwrap.dedent("""
        sudo apt install openssh-server
        sudo systemctl enable --now ssh
        sudo ufw allow ssh
        sudo ufw enable
        """).strip()
        for line in ssh:
            self.runcmd.append(line)

    def disable_password(self):
        raise NotImplementedError

    def configure_manager(self):
        raise NotImplementedError
        # use the calls above for a single easy to use method

    def configure_worker(self):
        raise NotImplementedError
        # use the calls above for a single easy to use method

    #
    # POST INSTALATION
    #
    def firmware(self):
        raise NotImplementedError


if __name__ == "__main__":
    hostnames = Parameter.expand("red,red[01-02]")
    ips = Parameter.expand("10.0.0.[1-3]")
    manager, workers = Host.get_hostnames(hostnames)

    cloudinit = Cloudinit()
    cloudinit.hostname(manager)
    cloudinit.etc_hosts()  # manager, workers, IPS
    cloudinit.keyboard()  # locale as parameter

    print("cloudinit")
    #
    # ADD WHAT IS NEEDED
    print(cloudinit)
