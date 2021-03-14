import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand, writefile

class Userdata:
    HEADER = "#cloud-config"
    def __init__(self, default=False):
        self.content = {}
        if default:
            self.__default__()

    def __str__(self):
        return Userdata.HEADER + '\n' + yaml.dump(self.content)

    def write(self, filename=None):
        """
        Writes a file to a location. Safe write for files on mounted partitions
        """
        tmp_location = path_expand('~/.cloudmesh/user-data.tmp')
        writefile(tmp_location, str(self))
        Shell.execute('mv', [tmp_location, filename])

    def with_ssh_password_login(self, ssh_pwauth=True):
        if ssh_pwauth is None:
            raise Exception('ssh_pwauth arg supplied is None')
        self.content['ssh_pwauth'] = ssh_pwauth
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
        $ grep -Fv \# /{mountpoint}/user-data
        (Removes comments)
        """
        self.with_default_user().with_ssh_password_login()

"""
d = Userdata()\
    .with_ssh_password_login()\
    .with_locale()\
    .with_hostname(hostname='testserver')\
    .with_default_user()

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


"""
