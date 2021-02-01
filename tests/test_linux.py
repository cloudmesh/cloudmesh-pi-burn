###############################################################
# pip install .; pytest -v --capture=no tests/test_linux.py::Test_linux.test_pishrink_install
# pytest -v --capture=no tests/test_linux.py
# pytest -v  tests/test_linux.py
###############################################################

import os
import shutil

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING

Benchmark.debug()

cloud = "ubuntu"
dev = "/dev/sdb"


@pytest.mark.incremental
class Test_burn:

    def test_pishrink_install(self):
        HEADING()
        cmd = "cloudmesh-installer list pi"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh-pi-burn" in str(result)
        assert "cloudmesh-pi-cluster" in str(result)
        assert "cloudmesh-inventory" in str(result)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, tag=cloud)

