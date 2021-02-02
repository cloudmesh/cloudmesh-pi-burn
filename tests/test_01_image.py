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
from cloudmesh.burn.util import os_is_windows

if os_is_windows():
    Console.error("OS is not supported on windows")
    sys.exit(1)

Benchmark.debug()

cloud = sys.platform
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

    def test_erase_images(self):
        HEADING()
        os.system("rm -f ~/.cloudmesh/cmburn/images/2021-01-11-raspios-buster-armhf-lite.*")
        os.system("rm -f ~/.cloudmesh/cmburn/images/2020-12-02-raspios-buster-armhf-lite.*")

    def test_versions(self):
        HEADING()
        cmd = "cms burn image versions --refresh"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "+-" in str(result)
        assert "latest" in str(result)
        assert "raspios_lite_armhf-2021-01-12" in str(result)
        assert "https://downloads.raspberrypi.org/raspios_lite_armhf/images/"\
               "raspios_lite_armhf-2021-01-12/2021-01-11-raspios-buster-armhf-lite.zip" in str(result)

    def test_get_latest(self):
        HEADING()
        Benchmark.Start()
        os.system("cms burn image get --tag=latest")
        Benchmark.Stop()
        result = Shell.run("cms burn image ls")
        assert "2021-01-11-raspios-buster-armhf-lite" in str(result)

    def test_ls(self):
        HEADING()
        cmd = "cms burn image ls"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "2021-01-11-raspios-buster-armhf-lite" in str(result)

    def test_get_specific(self):
        HEADING()
        Benchmark.Start()
        os.system("cms burn image get --tag=lite-2020-12-04")
        Benchmark.Stop()
        result = Shell.run("cms burn image ls")
        assert "2020-12-02-raspios-buster-armhf-lite" in str(result)

    def test_delete_specific(self):
        HEADING()
        cmd = "cms burn image delete --image=2020-12-02-raspios-buster-armhf-lite"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        result = Shell.run("cms burn image ls")
        assert "2020-12-02-raspios-buster-armhf-lite" not in str(result)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=True, csv=True, tag=cloud)

