###############################################################
# pip install .; pytest -v --capture=no tests/test_linux.py::Test_linux.test_pishrink_install
# pytest -v --capture=no tests/test_linux.py
# pytest -v  tests/test_linux.py
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
burn network list [--ip=IP] [--used]
              burn network
              burn info [--device=DEVICE]
              burn detect
              burn image versions [--refresh]
              burn image ls
              burn image delete [--image=IMAGE]
              burn image get [--url=URL]
              burn backup [--device=DEVICE] [--to=DESTINATION]
              burn copy [--device=DEVICE] [--from=DESTINATION]
              burn shrink [--image=IMAGE]
              burn create [--image=IMAGE]
                          [--device=DEVICE]
                          [--hostname=HOSTNAME]
                          [--ip=IP]
                          [--sshkey=KEY]
                          [--blocksize=BLOCKSIZE]
                          [--dryrun]
                          [--passwd=PASSWD]
                          [--ssid=SSID]
                          [--wifipassword=PSK]
                          [--format]
              burn sdcard [--image=IMAGE] [--device=DEVICE] [--dryrun]
              burn set [--hostname=HOSTNAME]
                       [--ip=IP]
                       [--key=KEY]
                       [--mount=MOUNTPOINT]
              burn enable ssh [--mount=MOUNTPOINT]
              burn wifi SSID [--passwd=PASSWD] [-ni]
"""

@pytest.mark.incremental
class Test_burn:

    def test_installer(self):
        HEADING()
        cmd = "cloudmesh-installer list pi"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "cloudmesh-pi-burn" in str(result)
        assert "cloudmesh-pi-cluster" in str(result)
        assert "cloudmesh-inventory" in str(result)

    def test_pishrink_install(self):
        HEADING()
        cmd = "cms burn shrink install"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.exists("/usr/local/bin/pishrink.sh")

    def test_info(self):
        HEADING()
        cmd = "cms burn info"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "Linux Foundation" in result

    def test_burn_sdcard(self):
        HEADING()
        global user
        global device
        cmd = f"cms burn sdcard mount --device={device}"
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()


    def test_mount(self):
        HEADING()
        global user
        global device
        cmd = f"cms burn mount --device={device}"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        result = Shell.run(f"ls /media/{user}/boot").splitlines()
        assert len(result) > 0
        result = Shell.run(f"ls /media/{user}/rootfs").splitlines()
        assert len(result) > 0

    def test_unmount(self):
        HEADING()
        global user
        global device
        cmd = f"cms burn unmount --device={device}"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        result = Shell.run(f"ls /media/{user}/boot").splitlines()
        assert len(result) == 0
        result = Shell.run(f"ls /media/{user}/rootfs").splitlines()
        assert len(result) == 0

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

