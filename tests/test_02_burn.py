###############################################################
# pytest -v --capture=no tests/test_02_burn.py
# pytest -v  tests/test_02_burn.py
# pytest -v --capture=no tests/test_02_burn.py::Test_burn::test_info
###############################################################

import os
import sys

import pytest
from cloudmesh.burn.sdcard import SDCard
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_pi
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import banner
from cloudmesh.burn.usb import USB

cloud = get_platform()

if os_is_mac():
    device = "/dev/disk2"

    details = USB.get_dev_from_diskutil()

    # checking if string contains list element
    valid = any(entry in device for entry in details)

    if not valid:
        Console.error("this device can not be used for the test")
        sys.exit(1)

    elif len(details) > 1:
        Console.error("For security reasons, please only put one USB writer in")
        sys.exit(1)

else:
    device = "/dev/sdb"

user = os.environ["USER"]

os.system("cms burn info")

banner(f"IS THE DEVICE CORRECTLY SET AS {device}?", c="#")

if not yn_choice(f"Is the device correctly set as {device}"):
    sys.exit(1)

if not (os_is_linux() or os_is_pi() or os_is_mac()):
    Console.error("OS is not Linux or Pi, test can not be performed")
    sys.exit(1)

os.system("cms burn unmount")
os.system("cms burn info")
print()
Console.warning("If you see mount points above, please stop, unmount, and try again.")
print()

if not yn_choice(f"This test will be performed with the user '{user}' on "
                 f"{device}. Select 'n' to input custom devive. Continue with "
                 f"default?"):
    if not yn_choice("Input custom device? i.e /dev/sdX"):
        sys.exit(1)
    else:
        device = input()
        print(f"Using device {device}")

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

        cmd = f"cms burn format --device={device}"
        Benchmark.Start()
        os.system(cmd)
        result = Shell.run(cmd)
        Benchmark.Stop()
        assert f"Disk {device}" in result
        assert "primary" in result
        assert "fat32" in result
        assert "Error" not in result

        sys.stdout.flush()
        sys.stderr.flush()

    def test_burn_sdcard(self):
        HEADING()

        global user
        global device

        cmd = f"cms burn sdcard --device={device}"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        assert "No matching image found." not in result
        assert "Too many images found" not in result
        assert "The image could not be found" not in result

        sys.stdout.flush()
        sys.stderr.flush()

    def test_mount(self):
        HEADING()
        card = SDCard(card_os="raspberry")
        global user
        global device
        cmd = f"cms burn mount --device={device}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        result = Shell.run(f"ls {card.boot_volume}").splitlines()
        assert len(result) > 0
        result = Shell.run(f"ls {card.root_volume}").splitlines()
        assert len(result) > 0

        sys.stdout.flush()
        sys.stderr.flush()

    def test_enable_ssh(self):
        HEADING()
        card = SDCard(card_os="raspberry")

        if os.path.exists(f'{card.boot_volume}/ssh'):
            cmd = f'sudo rm {card.boot_volume}/ssh'
            os.system(cmd)

        cmd = 'cms burn enable ssh'
        Benchmark.Start()
        result = Shell.run(cmd)  # noqa: F841
        Benchmark.Stop()

        assert os.path.exists(f'{card.boot_volume}/ssh')

    def test_wifi(self):
        HEADING()
        card = SDCard(card_os="raspberry")

        if os.path.exists(f"{card.boot_volume}/wpa_supplicant.conf"):
            cmd = f'sudo rm {card.boot_volume}/wpa_supplicant.conf'
            os.system(cmd)

        cmd = 'cms burn wifi --ssid=test_ssid --passwd=test_pass'
        Benchmark.Start()
        result = Shell.run(cmd)  # noqa: F841
        Benchmark.Stop()

        assert os.path.exists(f"{card.boot_volume}/wpa_supplicant.conf")

    def test_set_hostname(self):
        HEADING()
        card = SDCard(card_os="raspberry")

        cmd = 'cms burn set --hostname=test_host'
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()
        cmd = f'sudo cat {card.root_volume}/etc/hostname'
        result = Shell.run(cmd)
        assert 'test_host' in result.split()

    def test_set_ip(self):
        HEADING()
        card = SDCard(card_os="raspberry")

        cmd = 'cms burn set --ip=10.1.1.253'
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()
        cmd = f'sudo cat {card.root_volume}/etc/dhcpcd.conf'
        result = Shell.run(cmd)
        assert 'ip_address=10.1.1.253/24' in result.split()

    def test_set_key(self):
        HEADING()
        card = SDCard(card_os="raspberry")
        test_key = 'ssh-rsa AAAAAAAA test@test'
        f = open("test.pub", "w")
        f.write(test_key)
        f.close()

        cmd = 'cms burn set --key=./test.pub'
        Benchmark.Start()
        os.system(cmd)
        Benchmark.Stop()
        cmd = f'sudo cat {card.root_volume}/home/pi/.ssh/authorized_keys'
        result = Shell.run(cmd)
        os.system('rm ./test.pub')
        assert test_key in result.strip()

    def test_check(self):
        HEADING()
        cmd = "cms burn check"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        print(result)
        expected = ['hostname', 'test_host',
                    'ip', '10.1.1.253/24',
                    'ssh', 'True',
                    'auth_key', 'test@test',
                    'wifi', 'True',
                    'psk', 'test_pass',
                    'ssid', 'test_ssid'
                    ]
        for val in expected:
            assert val in result.split()
        assert result.split().count('True') == 2

    def test_unmount(self):
        HEADING()
        card = SDCard(card_os="raspberry")
        global user
        global device
        cmd = f"cms burn unmount --device={device}"
        Benchmark.Start()
        result = os.system(cmd)
        Benchmark.Stop()
        result = Shell.run(f"ls {card.boot_volume}").strip().splitlines()
        assert "No such file or directory" in result[0]
        result = Shell.run(f"ls {card.root_volume}").strip().splitlines()
        assert "No such file or directory" in result[0]

        sys.stdout.flush()
        sys.stderr.flush()

    def test_network(self):
        HEADING()
        cmd = "cms burn network"
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
        ip_eth0 = Shell.run('ip address | grep eth0| grep -oE'
                            ' "\\b([0-9]{1,3}\\.){3}[0-9]{1,3}\\b" | head '
                            '-1').strip()
        ip_wlan0 = Shell.run('ip address | grep wlan0| grep -oE'
                             ' "\\b([0-9]{1,3}\\.){3}[0-9]{1,3}\\b" | head '
                             '-1').strip()

        for line in result.splitlines():
            if 'eth0' in line:
                cmd_ip = line.split()[3]
                assert line.split()[1] == 'eth0'
                assert cmd_ip == ip_eth0
            elif 'wlan0' in line:
                cmd_ip = line.split()[3]
                assert line.split()[1] == 'wlan0'
                assert cmd_ip == ip_wlan0

    def test_benchmark(self):
        HEADING()
        Benchmark.print(sysinfo=False, csv=True, tag=cloud)
