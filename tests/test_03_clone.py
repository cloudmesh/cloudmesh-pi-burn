###############################################################
# pytest -v -x --capture=no tests/test_03_clone.py
# pytest -v -x tests/test_03_clone.py
# pytest -v --capture=no tests/test_03_clone.py::Test_clone::test_backup
###############################################################

import os
import sys

import pytest
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_pi
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import yn_choice

cloud = get_platform()
device = "/dev/sdb"
user = os.environ["USER"]

if not (os_is_linux() or os_is_pi()):
    Console.error("OS is not Linux or Pi, test can not be performed")
    sys.exit(1)

os.system("cms burn unmount")
os.system("cms burn info")
print()
Console.warning("If you see mount points above, please stop, unmount, and try again.")
print()

if not yn_choice(f"This test will be performed with the user '{user}' on "
                 f"{device}. Select 'n' to input custom devive. Continue with "
                 "default?"):
    if not yn_choice("Input custom device? i.e /dev/sdX"):
        sys.exit(1)
    else:
        device = input()
        print(f"Using device {device}")

Benchmark.debug()


@pytest.mark.incremental
class Test_clone:
    def test_backup(self):
        HEADING()
        global device

        os.system(f"cms burn load --device={device}")
        Console.ok("Backing up card image to ./test/img")

        cmd = f'cms burn backup --device={device} --to=./test.img'
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        assert 'error' not in result.split()

        cmd = f'sudo fdisk -l | grep {device}'
        result = Shell.run(cmd)
        print(result.split())
        dev_size = result.split()[4]
        print(dev_size)

        cmd = 'ls -al ./test.img'
        result = Shell.run(cmd)
        print(result.split())
        test_bak_size = result.split()[4]
        print(test_bak_size)

        assert dev_size == test_bak_size

    def test_shrink(self):
        # requires test_backup to run first
        HEADING()

        cmd = 'ls -al ./test.img'
        result = Shell.run(cmd)
        before_size = result.split()[4]
        print(f'Before size: {before_size}')

        cmd = 'cms burn shrink --image=./test.img'
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()

        cmd = 'ls -al ./test.img'
        result = Shell.run(cmd)
        after_size = result.split()[4]
        print(f'After size: {after_size}')

        assert float(before_size) > float(after_size)

    def test_copy(self):
        # requires test_backup to run first
        HEADING()

        os.system("cms burn unmount")  # card can not be mounted before format
        os.system(f"cms burn format --device={device}")
        Console.ok("Copying image to sdcard")

        cmd = f'cms burn copy --device={device} --from=./test.img'
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()

        card = SDCard(card_os="raspberry")
        cmd = f"cms burn mount --device={device}"
        os.system(cmd)
        result = Shell.run(f"ls {card.boot_volume}").splitlines()
        assert len(result) > 0
        result = Shell.run(f"ls {card.root_volume}").splitlines()
        assert len(result) > 0

        cmd = "cms burn unmount"
        os.system(cmd)
        os.remove('./test.img')

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
