###############################################################
# pytest -v --capture=no tests/test_04_networkdata.py
# pytest -v  tests/test_04_networkdata.py
# pytest -v --capture=no tests/test_04_networkdata.py::Test_burn::test_info
###############################################################

import pytest
import textwrap
import yaml

from cloudmesh.burn.ubuntu.networkdata import Networkdata

@pytest.mark.incremental
class Test_Networkdata:
	def test_static_ip(self):
		d = Networkdata()\
				.with_ip(ip="10.1.1.10")\
				.with_gateway(gateway="10.1.1.1")\
				.with_nameservers(nameservers=['8.8.8.8', '8.8.4.4'])\
				.with_defaults()
		
		correct = {'version': 2, 
						'ethernets': {
							'eth0': {
								'addresses': ['10.1.1.10/24'],
								'dhcp4': 'no',
								'gateway4': '10.1.1.1',
								'nameservers': {
									'addresses': ['8.8.8.8', '8.8.4.4']},
									'match': {
										'driver': 'bcmgenet smsc95xx lan78xx'
									},
									'set-name': 'eth0'}
						},
						'wifis': {}
					}

		assert(str(d) == yaml.dump(correct))
