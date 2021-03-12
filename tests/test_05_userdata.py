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


