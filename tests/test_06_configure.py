import os
import pytest

from cloudmesh.burn.ubuntu.configure import Configure
from cloudmesh.burn.ubuntu.networkdata import Networkdata
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

	def test_build_networkdata(self):
		inv_file = '~/.cloudmesh/config_test.yaml'
		inv = Inventory(inv_file)
		inv.add(host='test_host1', keyfile='~/.ssh/id_rsa.pub', service='manager', ip='10.1.1.11', router='10.1.1.1', dns=['8.8.8.8', '8.8.4.4'])
		inv.add(host='test_host2', service='worker', ip='10.1.1.10', router='10.1.1.1', dns=['8.8.8.8', '8.8.4.4'])
		inv.save()

		c = Configure(inventory='~/.cloudmesh/config_test.yaml')
		b1 = c.build_network_data(name='test_host1')
		b2 = c.build_network_data(name='test_host2')

		keys = readfile(filename='~/.ssh/id_rsa.pub').strip().split('\n')
		t1 = Networkdata()\
			.with_defaults()\
			.with_ip(ip='10.1.1.11')\
			.with_nameservers(nameservers=['8.8.8.8', '8.8.4.4'])\
			.with_gateway(gateway='10.1.1.1')

		t2 = Networkdata()\
			.with_defaults()\
			.with_ip(ip='10.1.1.10')\
			.with_nameservers(nameservers=['8.8.8.8', '8.8.4.4'])\
			.with_gateway(gateway='10.1.1.1')

		assert(t1.content == b1.content)
		assert(t2.content == b2.content)
		os.system("rm -f " + path_expand(inv_file))
