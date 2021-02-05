## Test Results on Pi

### What is the status of the implementation?

| Feature         | PI    | Ubuntu | Mac     | Windows |
| --------------- | ----- | ------ | ------- | ------- |
| image versions  | at +  | gt +   | gt +    |         |
| image ls        | at +  | gt +   | gt +    |         |
| image delete    | at +  | gt +   | gt +    |         |
| image get       | at +  | gt +   | gt +    |         |
| info            | at +  | g +    | g +/- 3 |         |
| detect*         |       |        |         |         |
| network         | at +  | g +?   |         |         |
| backup          | at +  | g +    |         |         |
| copy            | at +  | g +    |         |         |
| shrink install  | at +  | gt +   |  -      |         |
| shrink          | at +  | g+?    |  -      |         |
| sdcard          | at +  | gt -   |         |         |
| mount           | at +  | gt +   |         |         |
| unmount         | at +  | gt +   |         |         |
| enable ssh      | at +  |        |         |         |
| wifi            | at -  |   -    |  -      | -       |
| set             | at +  |        |         |         |
| create          |       |        |         |         |
| format          | at +  | gt +   |         |         |
| firmware        | a     | NA     |  NA     | NA      |

* g = gregor
* r = richie
* a = anthony
* ad = adam
* as = asuri
* ar = arjun

* d = diffrent implementation between Linux and PI (compare)
* 2 = change and add --ssd so its uniform
* ? = needs test
* - = broken
1 = get needs to use the image versions refresh cache
3 = does not report when the USB card is found
t = has a unit test

### test_pi.py
Most cms burn functions are tested in test_pi.py.

Successful completion of tests will create a bootable sd card with latest-lite.

Make sure to pay attention to command prompt at the start of test to verify 
the device. You can put in a custom device if you do not want the default.

### 15 pass and 1 fail

1 fail because test_wifi_configure not yet implemented for pi.

```
(ENV3) pi@raspberrypi:~/cm/cloudmesh-pi-burn $ pytest -v --capture=no tests/test_pi.py
=========================================================================================== test session starts ============================================================================================
platform linux -- Python 3.7.3, pytest-6.2.1, py-1.10.0, pluggy-0.13.1 -- /home/pi/ENV3/bin/python3
cachedir: .pytest_cache
rootdir: /home/pi/cm/cloudmesh-pi-burn, configfile: pytest.ini
plugins: cov-2.11.1
collecting ... burn info
dryrun:     False

# ----------------------------------------------------------------------
# This is  Raspberry PI
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Operating System SD Card
# ----------------------------------------------------------------------

Disk /dev/mmcblk0: 59.7 GiB, 64088965120 bytes, 125173760 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x71ebc03b

Device         Boot  Start       End   Sectors  Size Id Type
/dev/mmcblk0p1        8192    532479    524288  256M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      532480 125173759 124641280 59.4G 83 Linux

# ----------------------------------------------------------------------
# USB Device Probe
# ----------------------------------------------------------------------

+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+
|   Adr. |   bus |   Vendor |   Prod. | H Vendor   |   H Prod. |   Man. |   Ser.Num. |   USB Ver. | Comment                       |
|--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------|
|      2 |     1 |     8457 |   13361 | 02109      |     03431 |      0 |          0 |        2.1 | VIA Labs, Inc. Hub            |
|      1 |     1 |     7531 |       2 | 01d6b      |        02 |      3 |          1 |        2   | Linux Foundation 2.0 root hub |
|      4 |     2 |     3034 |     774 | 0bda       |      0306 |      1 |          3 |        3   | Realtek Semiconductor Corp.   |
|      1 |     2 |     7531 |       3 | 01d6b      |        03 |      3 |          1 |        3   | Linux Foundation 3.0 root hub |
+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
| Path     | Plugged-in   | Info                                         | Readable   | Formatted   | Empty   | Size             | Access   | Removable   | Writeable   |
|----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------|
| /dev/sda | True         | Generic- USB3.0 CRW-SD                       | True       | True        | False   | 3.97 GB/3.70 GiB | True     | True        | True        |
| /dev/sdb | True         | Generic- USB3.0 CRW-SD/MS 1.00 PQ: 0 ANSI: 6 | True       | True        | False   | 64.1 GB/59.7 GiB | True     | True        | True        |
+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
Timer: 0.9065s Load: 0.1717s (line_strip)

This test will be performed with the user 'pi' on /dev/sdb. Continue? (Y/n) n
Input custom device? (/dev/sdX) (Y/n) Y
/dev/sda
Using device /dev/sda
collected 16 items                                                                                                                                                                                         

tests/test_pi.py::Test_burn::test_installer 

# ######################################################################
# test_installer /tests/test_pi.py 79
# ######################################################################


pi:
    cloudmesh-common cloudmesh-cmd5 cloudmesh-sys cloudmesh-configuration
    cloudmesh-test cloudmesh-gui cloudmesh-abstract cloudmesh-admin
    cloudmesh-inventory cloudmesh-cloud cloudmesh-pi-cluster
    cloudmesh-pi-burn


PASSED
tests/test_pi.py::Test_burn::test_install 

# ######################################################################
# test_install /tests/test_pi.py 93
# ######################################################################

burn install

# ----------------------------------------------------------------------
# Installing pishrink.sh into /usr/local/bin
# ----------------------------------------------------------------------

--2021-02-04 20:12:54--  https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 151.101.184.133
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|151.101.184.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 10729 (10K) [text/plain]
Saving to: ‘pishrink.sh’

     0K ..........                                            100% 4.34M=0.002s

2021-02-04 20:12:54 (4.34 MB/s) - ‘pishrink.sh’ saved [10729/10729]


WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

+--------+----------------------------------------------------------------------------+----------+----------+--------------+
|   name | command                                                                    | status   | stdout   |   returncode |
|--------+----------------------------------------------------------------------------+----------+----------+--------------|
|      2 | wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh | done     |          |            0 |
|      3 | chmod +x pishrink.sh                                                       | done     |          |            0 |
|      4 | sudo mv pishrink.sh /usr/local/bin                                         | done     |          |            0 |
|      5 | sudo apt install parted -y > $HOME/tmp.log                                 | done     |          |            0 |
+--------+----------------------------------------------------------------------------+----------+----------+--------------+
Timer: 2.7690s Load: 0.1721s (line_strip)

PASSED
tests/test_pi.py::Test_burn::test_info 

# ######################################################################
# test_info /tests/test_pi.py 105
# ######################################################################

burn info
dryrun:     False

# ----------------------------------------------------------------------
# This is  Raspberry PI
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Operating System SD Card
# ----------------------------------------------------------------------

Disk /dev/mmcblk0: 59.7 GiB, 64088965120 bytes, 125173760 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x71ebc03b

Device         Boot  Start       End   Sectors  Size Id Type
/dev/mmcblk0p1        8192    532479    524288  256M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      532480 125173759 124641280 59.4G 83 Linux

# ----------------------------------------------------------------------
# USB Device Probe
# ----------------------------------------------------------------------

+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+
|   Adr. |   bus |   Vendor |   Prod. | H Vendor   |   H Prod. |   Man. |   Ser.Num. |   USB Ver. | Comment                       |
|--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------|
|      2 |     1 |     8457 |   13361 | 02109      |     03431 |      0 |          0 |        2.1 | VIA Labs, Inc. Hub            |
|      1 |     1 |     7531 |       2 | 01d6b      |        02 |      3 |          1 |        2   | Linux Foundation 2.0 root hub |
|      4 |     2 |     3034 |     774 | 0bda       |      0306 |      1 |          3 |        3   | Realtek Semiconductor Corp.   |
|      1 |     2 |     7531 |       3 | 01d6b      |        03 |      3 |          1 |        3   | Linux Foundation 3.0 root hub |
+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
| Path     | Plugged-in   | Info                                         | Readable   | Formatted   | Empty   | Size             | Access   | Removable   | Writeable   |
|----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------|
| /dev/sda | True         | Generic- USB3.0 CRW-SD                       | True       | True        | False   | 3.97 GB/3.70 GiB | True     | True        | True        |
| /dev/sdb | True         | Generic- USB3.0 CRW-SD/MS 1.00 PQ: 0 ANSI: 6 | True       | True        | False   | 64.1 GB/59.7 GiB | True     | True        | True        |
+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
Timer: 0.8152s Load: 0.1707s (line_strip)

PASSED
tests/test_pi.py::Test_burn::test_burn_format 

# ######################################################################
# test_burn_format /tests/test_pi.py 117
# ######################################################################

burn load --device=/dev/sda

# ----------------------------------------------------------------------
# load /dev/sda
# ----------------------------------------------------------------------

Timer: 0.0596s Load: 0.0000s (line_strip)
burn format --device=/dev/sda

# ----------------------------------------------------------------------
# format {device}
# ----------------------------------------------------------------------

sudo eject -t /dev/sda
                sudo parted /dev/sda --script -- mklabel msdos
                sudo parted /dev/sda --script -- mkpart primary fat32 1MiB 100%
                sudo mkfs.vfat -n UNTITLED -F32 /dev/sda1
mkfs.fat 4.1 (2017-01-24)
                sudo parted /dev/sda --script print
Model: Generic- USB3.0 CRW-SD (scsi)
Disk /dev/sda: 3974MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags: 

Number  Start   End     Size    Type     File system  Flags
 1      1049kB  3974MB  3973MB  primary  fat32        lba

Formatted SD Card
Timer: 5.3072s Load: 0.1724s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_burn_sdcard 

# ######################################################################
# test_burn_sdcard /tests/test_pi.py 140
# ######################################################################

burn load --device=/dev/sda

# ----------------------------------------------------------------------
# load /dev/sda
# ----------------------------------------------------------------------

Timer: 1.0631s Load: 0.0001s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_mount 

# ######################################################################
# test_mount /tests/test_pi.py 159
# ######################################################################

burn mount --device=/dev/sda
/dev/sda
mounting /dev/sda1 /media/pi/boot
mounting /dev/sda2 /media/pi/rootfs
/dev/sda
mounting /dev/sda1 /media/pi/boot
mounting /dev/sda2 /media/pi/rootfs
Timer: 2.3304s Load: 0.1958s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_enable_ssh 

# ######################################################################
# test_enable_ssh /tests/test_pi.py 176
# ######################################################################

PASSED
tests/test_pi.py::Test_burn::test_configure_wifi 

# ######################################################################
# test_configure_wifi /tests/test_pi.py 191
# ######################################################################

FAILED
tests/test_pi.py::Test_burn::test_set_hostname 

# ######################################################################
# test_set_hostname /tests/test_pi.py 206
# ######################################################################

burn set --hostname=test
Timer: 0.1618s Load: 0.1722s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_set_ip 

# ######################################################################
# test_set_ip /tests/test_pi.py 218
# ######################################################################

burn set --ip=10.10.10.10
Timer: 0.0965s Load: 0.1717s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_set_key 

# ######################################################################
# test_set_key /tests/test_pi.py 230
# ######################################################################

burn set --key=./test.pub
Timer: 0.0818s Load: 0.1709s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_unmount 

# ######################################################################
# test_unmount /tests/test_pi.py 247
# ######################################################################

burn unmount --device=/dev/sda
unmounting /media/pi/boot
unmounting  /media/pi/rootfs
Timer: 6.5633s Load: 0.1716s (line_strip)
PASSED
tests/test_pi.py::Test_burn::test_network 

# ######################################################################
# test_network /tests/test_pi.py 264
# ######################################################################

PASSED
tests/test_pi.py::Test_burn::test_backup PASSED
tests/test_pi.py::Test_burn::test_shrink PASSED
tests/test_pi.py::Test_burn::test_benchmark 

# ######################################################################
# test_benchmark /tests/test_pi.py 293
# ######################################################################



+-----------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------+
| Name                        | Status   |    Time |     Sum | Start               | tag       | Node        | User   | OS    | Version                                |
|-----------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------|
| test_pi/test_installer      | ok       |   0.904 |   0.904 | 2021-02-04 20:12:52 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_install        | ok       |   4.135 |   4.135 | 2021-02-04 20:12:52 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_info           | ok       |   2.207 |   2.207 | 2021-02-04 20:12:57 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_burn_format    | ok       |  12.783 |  12.783 | 2021-02-04 20:13:00 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_burn_sdcard    | ok       | 264.273 | 264.273 | 2021-02-04 20:13:16 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_mount          | ok       |   4.096 |   4.096 | 2021-02-04 20:17:40 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_enable_ssh     | ok       |   1.457 |   1.457 | 2021-02-04 20:17:44 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_configure_wifi | ok       |   1.385 |   1.385 | 2021-02-04 20:17:46 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_set_hostname   | ok       |   1.526 |   1.526 | 2021-02-04 20:17:47 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_set_ip         | ok       |   1.46  |   1.46  | 2021-02-04 20:17:49 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_set_key        | ok       |   1.445 |   1.445 | 2021-02-04 20:17:50 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_unmount        | ok       |   7.925 |   7.925 | 2021-02-04 20:17:52 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_pi/test_network        | ok       |   1.425 |   1.425 | 2021-02-04 20:18:00 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
+-----------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------+

# csv,timer,status,time,sum,start,tag,uname.node,user,uname.system,platform.version
# csv,test_pi/test_installer,ok,0.904,0.904,2021-02-04 20:12:52,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_install,ok,4.135,4.135,2021-02-04 20:12:52,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_info,ok,2.207,2.207,2021-02-04 20:12:57,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_burn_format,ok,12.783,12.783,2021-02-04 20:13:00,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_burn_sdcard,ok,264.273,264.273,2021-02-04 20:13:16,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_mount,ok,4.096,4.096,2021-02-04 20:17:40,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_enable_ssh,ok,1.457,1.457,2021-02-04 20:17:44,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_configure_wifi,ok,1.385,1.385,2021-02-04 20:17:46,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_set_hostname,ok,1.526,1.526,2021-02-04 20:17:47,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_set_ip,ok,1.46,1.46,2021-02-04 20:17:49,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_set_key,ok,1.445,1.445,2021-02-04 20:17:50,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_unmount,ok,7.925,7.925,2021-02-04 20:17:52,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_pi/test_network,ok,1.425,1.425,2021-02-04 20:18:00,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020

PASSED

================================================================================================= FAILURES =================================================================================================
______________________________________________________________________________________ Test_burn.test_configure_wifi _______________________________________________________________________________________

self = <test_pi.Test_burn object at 0xb5344f10>

    def test_configure_wifi(self):
        HEADING()
        card = SDCard(card_os="raspberry", host="raspberry")
    
        if os.path.exists(f"{card.boot_volume}/wpa_supplicant.conf"):
            cmd = f'sudo rm {card.boot_volume}/wpa_supplicant.conf'
            os.system(cmd)
    
        cmd = f'cms burn wifi --ssid=test'
        Benchmark.Start()
        result = Shell.run(cmd)
        Benchmark.Stop()
    
>       assert os.path.exists(f"{card.boot_volume}/wpa_supplicant.conf")
E       AssertionError: assert False
E        +  where False = <function exists at 0xb66c5618>('/media/pi/boot/wpa_supplicant.conf')
E        +    where <function exists at 0xb66c5618> = <module 'posixpath' from '/usr/lib/python3.7/posixpath.py'>.exists
E        +      where <module 'posixpath' from '/usr/lib/python3.7/posixpath.py'> = os.path

tests/test_pi.py:204: AssertionError
========================================================================================= short test summary info ==========================================================================================
FAILED tests/test_pi.py::Test_burn::test_configure_wifi - AssertionError: assert False
================================================================================= 1 failed, 15 passed in 322.20s (0:05:22) =================================================================================
```

At this point I was able to boot and sd card and ssh into it with the static 
ip assigned by the test.

```
$ ssh pi@10.10.10.10
```

### test_clone.py

Next I test cloning that same SD card.

SD card cloning can take a long time to run, so I put it in a second test 
file test_clone.py

I was using a 4GB card so the test would not take too long. This test can not 
be run with an SD card of the equal size to the current OS SD card becuase 
dd first copies the entire drive bit by bit.

### 3/3 pass


```
(ENV3) pi@raspberrypi:~/cm/cloudmesh-pi-burn $ pytest -v -x --capture=no tests/test_clone.py
=========================================================================================== test session starts ============================================================================================
platform linux -- Python 3.7.3, pytest-6.2.1, py-1.10.0, pluggy-0.13.1 -- /home/pi/ENV3/bin/python3
cachedir: .pytest_cache
rootdir: /home/pi/cm/cloudmesh-pi-burn, configfile: pytest.ini
plugins: cov-2.11.1
collecting ... burn info
dryrun:     False

# ----------------------------------------------------------------------
# This is  Raspberry PI
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Operating System SD Card
# ----------------------------------------------------------------------

Disk /dev/mmcblk0: 59.7 GiB, 64088965120 bytes, 125173760 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x71ebc03b

Device         Boot  Start       End   Sectors  Size Id Type
/dev/mmcblk0p1        8192    532479    524288  256M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      532480 125173759 124641280 59.4G 83 Linux

# ----------------------------------------------------------------------
# USB Device Probe
# ----------------------------------------------------------------------

+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+
|   Adr. |   bus |   Vendor |   Prod. | H Vendor   |   H Prod. |   Man. |   Ser.Num. |   USB Ver. | Comment                       |
|--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------|
|      2 |     1 |     8457 |   13361 | 02109      |     03431 |      0 |          0 |        2.1 | VIA Labs, Inc. Hub            |
|      1 |     1 |     7531 |       2 | 01d6b      |        02 |      3 |          1 |        2   | Linux Foundation 2.0 root hub |
|      4 |     2 |     3034 |     774 | 0bda       |      0306 |      1 |          3 |        3   | Realtek Semiconductor Corp.   |
|      1 |     2 |     7531 |       3 | 01d6b      |        03 |      3 |          1 |        3   | Linux Foundation 3.0 root hub |
+--------+-------+----------+---------+------------+-----------+--------+------------+------------+-------------------------------+

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
| Path     | Plugged-in   | Info                                         | Readable   | Formatted   | Empty   | Size             | Access   | Removable   | Writeable   |
|----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------|
| /dev/sda | True         | Generic- USB3.0 CRW-SD                       | True       | True        | False   | 3.97 GB/3.70 GiB | True     | True        | True        |
| /dev/sdb | True         | Generic- USB3.0 CRW-SD/MS 1.00 PQ: 0 ANSI: 6 | True       | True        | False   | 64.1 GB/59.7 GiB | True     | True        | True        |
+----------+--------------+----------------------------------------------+------------+-------------+---------+------------------+----------+-------------+-------------+
Timer: 1.9522s Load: 0.1708s (line_strip)

This test will be performed with the user 'pi' on /dev/sdb. Continue? (Y/n) n
Input custom device? i.e /dev/sdX (Y/n) Y       
/dev/sda
Using device /dev/sda
collected 4 items                                                                                                                                                                                          

tests/test_clone.py::Test_clone::test_backup 

# ######################################################################
# test_backup /tests/test_clone.py 46
# ######################################################################

burn load --device=/dev/sda

# ----------------------------------------------------------------------
# load /dev/sda
# ----------------------------------------------------------------------

Timer: 0.0594s Load: 0.0000s (line_strip)
['Disk', '/dev/sda:', '3.7', 'GiB,', '3974103040', 'bytes,', '7761920', 'sectors', '/dev/sda1', '8192', '532479', '524288', '256M', 'c', 'W95', 'FAT32', '(LBA)', '/dev/sda2', '532480', '7761919', '7229440', '3.5G', '83', 'Linux']
3974103040
['-rw-r--r--', '1', 'pi', 'pi', '3974103040', 'Feb', '4', '20:46', './test.img']
3974103040
PASSED
tests/test_clone.py::Test_clone::test_shrink 

# ######################################################################
# test_shrink /tests/test_clone.py 73
# ######################################################################

Before size: 3974103040
After size: 2223137280
PASSED
tests/test_clone.py::Test_clone::test_copy 

# ######################################################################
# test_copy /tests/test_clone.py 94
# ######################################################################

burn load --device=/dev/sda

# ----------------------------------------------------------------------
# load /dev/sda
# ----------------------------------------------------------------------

Timer: 0.0677s Load: 0.0000s (line_strip)
burn mount --device=/dev/sda
/dev/sda
mounting /dev/sda1 /media/pi/boot
mounting /dev/sda2 /media/pi/rootfs
/dev/sda
mounting /dev/sda1 /media/pi/boot
mounting /dev/sda2 /media/pi/rootfs
Timer: 2.3295s Load: 0.1954s (line_strip)
burn unmount
unmounting /media/pi/boot
unmounting  /media/pi/rootfs
Timer: 6.4984s Load: 0.1706s (line_strip)
PASSED
tests/test_clone.py::Test_clone::test_benchmark 

# ######################################################################
# test_benchmark /tests/test_clone.py 116
# ######################################################################



+------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------+
| Name                   | Status   |    Time |     Sum | Start               | tag       | Node        | User   | OS    | Version                                |
|------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------|
| test_clone/test_backup | ok       | 211.158 | 211.158 | 2021-02-04 20:42:49 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_clone/test_shrink | ok       |   7.723 |   7.723 | 2021-02-04 20:46:21 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
| test_clone/test_copy   | ok       | 311.721 | 311.721 | 2021-02-04 20:46:30 | raspberry | raspberrypi | pi     | Linux | #1379 SMP Mon Dec 14 13:11:54 GMT 2020 |
+------------------------+----------+---------+---------+---------------------+-----------+-------------+--------+-------+----------------------------------------+

# csv,timer,status,time,sum,start,tag,uname.node,user,uname.system,platform.version
# csv,test_clone/test_backup,ok,211.158,211.158,2021-02-04 20:42:49,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_clone/test_shrink,ok,7.723,7.723,2021-02-04 20:46:21,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020
# csv,test_clone/test_copy,ok,311.721,311.721,2021-02-04 20:46:30,raspberry,raspberrypi,pi,Linux,#1379 SMP Mon Dec 14 13:11:54 GMT 2020

PASSED

====================================================================================== 4 passed in 562.39s (0:09:22) =======================================================================================
```

Again at this point I verified the re-burned card with the new shrunken 
image by booting with that card and connecting to it.

```
ssh pi@10.10.10.10
```

## Test results on linux (ubuntu 18.04)

### test_pi.py

Originally burn_sdcard failed becuase: pv was missing on my ubuntu.
1. I did not have the latest-lite image in ~/.cloudmesh...
2. My ubuntu did not have pv installed. This must be a missing requirement 
   for cloudmesh get pi.

```
anthony@anthony-ubuntu:~/cm/cloudmesh-pi-burn$ cms burn sdcard --device=/dev/sda
burn sdcard --device=/dev/sda
INFO: Burning...
/home/anthony/.cloudmesh/cmburn/images/2021-01-11-raspios-buster-armhf-lite.img
/dev/sda
4M
dd if=/home/anthony/.cloudmesh/cmburn/images/2021-01-11-raspios-buster-armhf-lite.img | pv -w 80 | sudo dd of=/dev/sda bs=4M conv=fsync status=progress
sh: 1: pv: not found
dd: writing to 'standard output': Broken pipe
1+0 records in
0+0 records out
0 bytes copied, 0.000145562 s, 0.0 kB/s
0+0 records in
0+0 records out
0 bytes copied, 5.0097e-05 s, 0.0 kB/s
```

Running the following image tests leaves a copy of latest-lite in ~/.cloudmesh.

```
pytest -v --capture=no tests/test_01_image.py
```

The following installs pv

```
sudo apt install pv
```

Now the following passed

```
pytest -v --capture=no tests/test_pi.py::Test_burn::test_burn_sdcard
```

Lets try the whole test again.



### test_clone.py
