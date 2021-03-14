import pytest
import yaml

from cloudmesh.burn.ubuntu.userdata import Userdata

@pytest.mark.incremental
class Test_Userdata:
	def test_empty_conf(self):
		d = Userdata()
		correct = {}
		correct = Userdata.HEADER + '\n' + yaml.dump(correct)
		assert(correct == str(d))

	def test_method_order(self):
		d = Userdata().with_default_user().with_hostname(hostname='pytest').with_locale().with_ssh_password_login()
		e = Userdata().with_hostname(hostname='pytest').with_locale().with_ssh_password_login().with_default_user()
		f = Userdata().with_locale().with_ssh_password_login().with_default_user().with_hostname(hostname='pytest')
		g = Userdata().with_ssh_password_login().with_default_user().with_hostname(hostname='pytest').with_locale()

		d, e, f, g = d.content, e.content, f.content, g.content

		assert(d == e)
		assert(e == f)
		assert(f == g)
