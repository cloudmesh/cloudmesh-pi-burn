import textwrap
class Cloudinit:

    def __init__(self):
        self.content = ""
        self.runcmd = ""

        # runcmd must be at end and only run once

    def get(self):
        runcmd = """
        runcmd:
        """ + "  - ".joun(self.runcmd)

        content = self.content + self.runcmd
        return content

    def __str__(self):
        return self.get()

    def __repr__(self):
        return self.get()

    def add(self, content):
        self.content = self.content + "\n" + textwrap.dedent(content).strip()

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
        raise NotImplementedError

    def static_network(self, *, hostnames, ips):
        content = """
        #
        # Set static network addresses
        #
        network-interfaces: |
          auto eth0
          iface eth0 inet static
          address 192.168.1.10
          network 192.168.1.0
          netmask 255.255.255.0
          broadcast 192.168.1.255
          gateway 192.168.1.1
        """
        raise NotImplementedError

    def nameserver(self):
        content = """
        #
        # Set name server
        #
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
        raise NotImplementedError

  def ntp(self):
        script = """
        #
        # Set ntp
        #
        ntp:
          servers:
            - ntp1.example.com
            - ntp2.example.com
            - ntp3.example.com
        runcmd:
          - /usr/bin/systemctl enable --now ntpd
          """
        raise NotImplementedError

    def dhcp(self):
        raise NotImplementedError

    def keyboard(self):
        self.runcmd.append(
            "/usr/bin/localectl set-keymap de-latin1-nodeadkeys"
        )
        raise NotImplementedError

    def locale(self):
        raise NotImplementedError

    def hostname(self, name):
        content = """
        #
        # Set hostname
        #
        preserve_hostname: false
        hostname: {name}
        """
        self.add(name)

    def etc_hosts(self):
        content = """
        #
        # Set /etc/hosts
        #
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
        raise NotImplementedError

    def startup(self):
        raise NotImplementedError

    def cloud_config(self):
        raise NotImplementedError

    def set_key(self):
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
        raise NotImplementedError

    def permissions(self):
        raise NotImplementedError

    def add_user(self):
        raise NotImplementedError

    def enable_ssh(self):
        raise NotImplementedError

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
