###############################################################
# pytest -v --capture=no tests/test_linux.py
# pytest -v  tests/test_linux.py
# pytest -v --capture=no tests/test_linux.py::Test_linux.test_pishrink_install
###############################################################

import os
import shutil
import pytest
import sys

from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.console import Console
from cloudmesh.common.util import yn_choice

from cloudmesh.burn.util import os_is_linux

cloud = "ubuntu"
device = "/dev/sdb"
user = os.environ["USER"]

if not os_is_linux():
    Console.error("OS is not Ubuntu, test can not be performed")
    sys.exit(1)


os.system("cms burn info")
print()
if not yn_choice(f"This test will be performed with the user '{user}' on {device}. Continue?"):
    sys.exit(1)

Benchmark.debug()

"""
Tests to be integrated, 

Note image tests are in  test_01_image.py

burn network list [--ip=IP] [--used]
burn network
burn info [--device=DEVICE]
burn detect
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

        sys.stdout.flush()
        sys.stderr.flush()

    def test_install(self):
        HEADING()
        cmd = "cms burn install"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert os.path.exists("/usr/local/bin/pishrink.sh")

        sys.stdout.flush()
        sys.stderr.flush()

    def test_info(self):
        HEADING()
        cmd = "cms burn info"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        assert "Linux Foundation" in result

        sys.stdout.flush()
        sys.stderr.flush()

    def test_burn_format(self):
        HEADING()
        global user
        global device

        os.system(f"cms burn load --device={device}")

        cmd = f"cms burn format --device={device}"
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()

        os.system(f"eject {device}")

        sys.stdout.flush()
        sys.stderr.flush()



    def test_burn_sdcard(self):
        HEADING()

        global user
        global device

        os.system(f"cms burn load --device={device}")

        cmd = f"cms burn sdcard --device={device}"
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()

        sys.stdout.flush()
        sys.stderr.flush()

    def test_mount(self):
        HEADING()
        global user
        global device
        cmd = f"cms burn mount --device={device}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        result = Shell.run(f"ls /media/{user}/boot").splitlines()
        assert len(result) > 0
        result = Shell.run(f"ls /media/{user}/rootfs").splitlines()
        assert len(result) > 0

        sys.stdout.flush()
        sys.stderr.flush()

    def test_unmount(self):
        HEADING()
        global user
        global device
        cmd = f"cms burn unmount --device={device}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        result = Shell.run(f"ls /media/{user}/boot").strip().splitlines()
        assert len(result) == 0
        result = Shell.run(f"ls /media/{user}/rootfs").strip().splitlines()
        assert len(result) == 0

        sys.stdout.flush()
        sys.stderr.flush()

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)

