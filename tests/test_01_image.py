###############################################################
# pytest -v --capture=no tests/test_01_image.py
# pytest -v  tests/test_01_image.py
# pytest -v --capture=no tests/test_01_image.py::Test_01_image.test_TBD
###############################################################

import os
import shutil
import pytest
import sys

from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.console import Console

from cloudmesh.burn.util import os_is_linux


if not os_is_linux():
    Console.error("OS is not Ubuntu, test can not be performed")
    sys.exit(1)

Benchmark.debug()

cloud = "ubuntu"
device = "/dev/sdb"
user = os.environ["USER"]




"""
Here we want to test 

burn image versions [--refresh]
burn image ls
burn image delete [--image=IMAGE]
burn image get [--url=URL]
"""


@pytest.mark.incremental
class Test_burn:

    def test_versions(self):
        HEADING()
        cmd = "cms burn versions --refresh"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "TBD" in str(result)

    def test_get_latest(self):
        HEADING()
        cmd = "cms burn get latest"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "TBD" in str(result)

    def test_get_specific(self):
        HEADING()
        cmd = "cms burn get latest"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "TBD" in str(result)

    def test_ls(self):
        HEADING()
        cmd = "cms burn image ls"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "TBD" in str(result)

    def test_delete_specific(self):
        HEADING()
        cmd = "cms burn info"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "TBD" in result
        # do an ls and see if its deleted or us os.path.exists

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

