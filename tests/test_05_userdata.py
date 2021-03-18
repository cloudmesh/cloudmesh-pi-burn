###############################################################
# pytest -v --capture=no tests/test_05_userdata.py
# pytest -v  tests/test_05_userdata.py
# pytest -v --capture=no tests/test_05_userdata.py::Test_burn::test_info
###############################################################
import pytest
import yaml

from cloudmesh.burn.ubuntu.userdata import Userdata
from cloudmesh.common.util import HEADING

@pytest.mark.incremental
class Test_Userdata:
	def test_empty_conf(self):
		HEADING()
		d = Userdata()
		correct = {}
		correct = Userdata.HEADER + '\n' + yaml.dump(correct)
		assert(correct == str(d))

	def test_method_order(self):
		HEADING()
		d = Userdata().with_default_user().with_hostname(hostname='pytest').with_locale().with_ssh_password_login()
		e = Userdata().with_hostname(hostname='pytest').with_locale().with_ssh_password_login().with_default_user()
		f = Userdata().with_locale().with_ssh_password_login().with_default_user().with_hostname(hostname='pytest')
		g = Userdata().with_ssh_password_login().with_default_user().with_hostname(hostname='pytest').with_locale()

		d, e, f, g = d.content, e.content, f.content, g.content

		assert(d == e)
		assert(e == f)
		assert(f == g)
