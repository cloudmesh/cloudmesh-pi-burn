import oyaml as yaml

from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand, writefile


class Userdata:
    """
    A Builder class for cloud-config Userdata

    A Builder class follows the Builder design pattern. This design pattern allows
    users of the class to construct a complex data structure using purely instance
    methods. This is very useful in that the user of the class need not concern
    themselves with the underlying implementation of the class. Consequentially,
    changes to this class can be made without needing a refactor of all existing calls.

    Examples:

    d = Userdata()\
    .with_ssh_password_login()\
    .with_locale()\
    .with_hostname(hostname='testserver')\
    .with_default_user()\
    .with_authorized_keys(key=['ssh-rsa AAAA.....user@laptop'])\
    .with_set_wifi_country(country='US')\
    .with_write_files(path='/home/ubuntu/.ssh/id_rsa', content='this is a ssh key', permissions='0600')\
    .with_write_files(path='/home/ubuntu/.ssh/id_rsa.pub', content='this is a pub key', permissions='0644')\
    .with_fix_user_dir_owner(user='ubuntu')

    print(d)

    #cloud-config
    ssh_pwauth: yes
    locale: en_US
    preserve_hostname: false
    hostname: testserver
    chpasswd:
    expire: true
    list:
    - ubuntu: ubuntu
    ssh_authorized_keys:
    - ssh-rsa AAAA.....user@laptop
    bootcmd:
    - - sudo
      - iw
      - reg
      - set
      - US
    runcmd:
    - - sh
      - -xc
      - sudo echo REGDOMAIN=US | sudo tee /etc/default/crda > /dev/null
    - - sh
      - -xc
      - sudo chown -R ubuntu:ubuntu /home/ubuntu
    write_files:
    - content: this is a ssh key
      path: /home/ubuntu/.ssh/id_rsa
      permissions: '0600'
    - content: this is a pub key
      path: /home/ubuntu/.ssh/id_rsa.pub
      permissions: '0644'

    """

    HEADER = "#cloud-config"

    def __init__(self, default=False):
        self.content = {}
        if default:
            self.__default__()

    def __str__(self):
        return Userdata.HEADER + '\n' + yaml.dump(self.content)

    def with_authorized_keys(self, keys=None):
        """
        Adds a list of authorized keys for default user ubuntu
        """
        if keys is None:
            raise Exception('keys arg supplied is None')
        if type(keys) != list:
            raise TypeError('Expected type of keys to be a list')

        if 'ssh_authorized_keys' not in self.content:
            self.content['ssh_authorized_keys'] = keys
        else:
            #
            # BUG: this has no effect
            #
            self.content['ssh_authorized_keys']
        return self

    def write(self, filename=None):
        """
        Writes a file to a location. Safe write for files on mounted partitions
        """
        if filename is None:
            raise Exception('filename arg supplied is None')
        tmp_location = path_expand('~/.cloudmesh/user-data.tmp')
        writefile(tmp_location, str(self))
        Console.info(f'Writing to {filename}')
        Shell.run(f'cat {tmp_location} | sudo tee {filename}')

    def with_ssh_password_login(self, ssh_pwauth=True):
        if ssh_pwauth is None:
            raise Exception('ssh_pwauth arg supplied is None')
        self.content['ssh_pwauth'] = ssh_pwauth
        return self

    def with_package_update(self, update=True):
        self.content['package_update'] = update
        return self

    def with_package_upgrade(self, upgrade=True):
        self.content['package_upgrade'] = upgrade
        return self

    def with_set_wifi_country(self, country=None):
        if country is None:
            raise Exception('the country arg supplied is none')

        cmd = f"sudo iw reg set {country}"
        self.with_bootcmd(cmd)

        cmd = f"sudo echo REGDOMAIN={country} | sudo tee /etc/default/crda > /dev/null"
        self.with_runcmd(cmd)
        return self

    def with_hosts(self, hosts=None):
        """
        Give a list of ip:hostname formatted strings, add to /etc/hosts
        """
        if not hosts:
            raise Exception('hosts arg passed is None')

        for hostpair in hosts:
            if ':' not in hostpair:
                raise Exception('Expected hosts to be a list of ip:hostname strings')
            ip, hostname = hostpair.split(':')
            self.with_bootcmd(cmd=f'echo {ip} {hostname} >> /etc/hosts')
        return self

    def with_bootcmd(self, cmd=None):
        if cmd is None:
            raise Exception('the command arg supplied is none')

        if 'bootcmd' in self.content:
            if type(cmd) == str:
                self.content['bootcmd'].append(cmd)
            elif type(cmd) == list:
                self.content['bootcmd'].extend(cmd)
        else:
            if type(cmd) == str:
                self.content['bootcmd'] = [cmd]
            elif type(cmd) == list:
                self.content['bootcmd'] = cmd
        return self

    def with_runcmd(self, cmd=None):
        if cmd is None:
            raise Exception('the command arg supplied is none')

        if 'runcmd' in self.content:
            if type(cmd) == str:
                self.content['runcmd'].append(cmd)
            elif type(cmd) == list:
                self.content['runcmd'].extend(cmd)
        else:
            if type(cmd) == str:
                self.content['runcmd'] = [cmd]
            elif type(cmd) == list:
                self.content['runcmd'] = cmd
        return self

    def with_access_point_bridge(self, priv_interface='eth0', ext_interface='wlan0'):
        """
        Uses iptables to configure an access point bridge where devices on priv_interface
        can route internet traffice through the priv_interface of the device towards ext_interface

        Often, this is practical for providing an entire cluster internet through a centralized point (the manager)
        """
        self.with_packages(packages=["iptables-persistent"])
        # Enable ipv4 forwarding and configure ip tables rules
        #
        # BUG: Should / be // ?
        #
        self.with_runcmd(cmd="sudo sysctl -w net.ipv4.ip_forward=1")\
            .with_runcmd(cmd="sudo sed -i 's/#net\.ipv4\.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf")\
            .with_runcmd(cmd=f"sudo iptables -A FORWARD -i {priv_interface} -o {ext_interface} -j ACCEPT")\
            .with_runcmd(cmd=f"sudo iptables -A FORWARD -i {ext_interface} -o {priv_interface} "
                             "-m state --state ESTABLISHED,RELATED -j ACCEPT")\
            .with_runcmd(cmd=f"sudo iptables -t nat -A POSTROUTING -o {ext_interface} -j MASQUERADE")\
            .with_runcmd(cmd="iptables-save > /etc/iptables/rules.v4")  # nqa: E501

        return self

    def with_write_files(self,
                         encoding=None,
                         content=None,
                         owner=None,
                         path=None,
                         permissions=None):
        arguments = locals()
        arguments['self'] = None
        arguments = [(k, v) for k, v in arguments.items() if v is not None]

        if path is None:
            raise Exception('the path arg supplied is none')
        if content is None:
            raise Exception('the content supplied is none')

        # supports multiline strings, keeps newlines
        if '\n' in content:
            content = '|\n' + content

        file = {}
        for arg in arguments:
            file[arg[0]] = arg[1]

        if 'write_files' in self.content:
            self.content['write_files'].append(file)
        else:
            self.content['write_files'] = [file]

        return self

    def with_fix_user_dir_owner(self, user=None):
        if user is None:
            raise Exception('the user arg supplie is none')

        cmd = f'sudo chown -R {user}:{user} /home/{user}'
        self.with_runcmd(cmd=cmd)
        return self

    def with_packages(self, packages=None):
        """
        Given a list of packages or single package as string, add to the installation list. Can be called multiple times
        """
        if packages is None:
            raise Exception('ssh_pwauth arg supplied is None')
        if type(packages) != list and type(packages) != str:
            raise Exception('Type of packages expected to be a list or str')
        if 'packages' not in self.content:
            self.content['packages'] = []

        if type(packages) == list:
            self.content['packages'] += packages
        elif type(packages) == str:
            self.content['packages'] += [packages]
        return self

    def with_net_tools(self):
        """
        Adds net-tools and inetutils-traceroute to package installation list

        For useful network commands such as route and traceroute
        """
        self.with_packages(packages=['net-tools', 'inetutils-traceroute'])
        return self

    def with_locale(self, locale='en_US'):
        if locale is None:
            raise Exception('locale arg supplied is None')
        self.content['locale'] = locale
        return self

    def with_hostname(self, hostname=None):
        if hostname is None:
            raise Exception('hostname arg supplied is None')
        self.content['preserve_hostname'] = False
        self.content['hostname'] = hostname
        return self

    def with_default_user(self):
        """
        Include default user ubuntu with default password ubuntu. Prompt password change upon first access
        """
        if 'chpasswd' not in self.content:
            self.content['chpasswd'] = {}

        self.content['chpasswd']['expire'] = True
        self.content['chpasswd']['list'] = ['ubuntu:ubuntu']
        return self

    def __default__(self):
        """
        Set the default configuration the one that comes burnt with the ubuntu server OS

        Captured with
        $ grep -Fv \\# /{mountpoint}/user-data
        (Removes comments)
        """
        self.with_default_user().with_ssh_password_login()
