import os
import pytest

from cloudmesh.burn.ubuntu.configure import Configure
from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.common.util import readfile, path_expand
from cloudmesh.inventory.inventory import Inventory

@pytest.mark.incremental
class Test_Configure:
	def test_build_user_data(self):
		inv_file = '~/.cloudmesh/config_test.yaml'
		inv = Inventory(inv_file)
		inv.add(host='test_host1', keyfile='~/.ssh/id_rsa.pub', service='manager')
		inv.add(host='test_host2', service='worker')
		inv.save()

		c = Configure(inventory='~/.cloudmesh/config_test.yaml')
		b1 = c.build_user_data(name='test_host1')
		b2 = c.build_user_data(name='test_host2')

		keys = readfile(filename='~/.ssh/id_rsa.pub').strip().split('\n')
		t1 = Userdata()\
			.with_default_user()\
			.with_authorized_keys(keys=keys)\
			.with_ssh_password_login(ssh_pwauth=False)\
			.with_locale()\
			.with_net_tools()\
			.with_hostname(hostname='test_host1')

		t2 = Userdata()\
			.with_default_user()\
			.with_ssh_password_login()\
			.with_locale()\
			.with_net_tools()\
			.with_hostname(hostname='test_host2')
		
		assert(t1.content == b1.content)
		assert(t2.content == b2.content)
		os.system("rm -f " + path_expand(inv_file))
