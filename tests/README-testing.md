## How to Test cloudmesh-pi-burn

This directory includes three test files that are meant to be tested 
sequentially in order, in totality.

Due to the nature of burning and testing SD cards, these unit tests are not 
independent and build on top of each other.

Do not expect an individual test from a test file to work without 
understanding and verifying the required pre-conditions. 

### Test Files

1. **rest_01_image.py**
    - Prequisite: None
    - Purpose: Listing, downloading, and deleting images.
    - Residual Output: A copy of the latest-lite image is saved in ~/.
      cloudmesh/cmburn/images
2. **test_02_burn.py**
    - Prequsite: A copy of the latest-lite image is saved in ~/., pv program
      cloudmesh/cmburn/images
    - Purpose: Test most cms burn functions, excluding sdcard cloning 
      functions.
    - Output: An sd card imaged with latest-lite accessible at pi@ 10.1.1.
      253 with the default raspi os password
3. **test_03_clone.py**
    - Prequisite: A functional burned card, enough storage space to store an 
      block copy of the SD card. You cannot run this on the pi with an sd 
      card the same size as your pi's OS sd card. This is why the tests were 
      separate. That and an entire bit-by-it copy of 64 GB can take some time. pv program.
    - Purpose: Test cloning an sd card.
    - Output: An bootable cloned sd card. 

### Running the Tests

**These tests have been tested on Raspi OS and Ubuntu 18.04.**

**These tests require that the SD card is not mounted. The test files will 
unmount on launch, do not remount during test configuration.** 

A mounted sd card will fail to format. Ubuntu will automatically mount on 
detection. Raspi OS does not.

**Tests use /dev/sdb/ as the default device. Follow the after starting the test 
to change the device if required.**

```
This test will be performed with the user 'pi' on /dev/sdb. Select 'n' to input custom devive. Continue with default? (Y/n)
n
Input custom device? i.e /dev/sdX (Y/n)
y
/dev/sda
```
**You need the pv program if it is not already installed**

```
sudo apt install pv
```

#### Steps

1. Move to the pi-burn directory.

```
cd ~/cm/cloudmesh-pi-burn/
```

2. Run the images tests and verify all pass. This only needs to be done once 
   before burn tests. 
   
```
pytest -v --capture=no tests/test_01_image.py
```

3. Run the burn tests and verify all pass.

```
pytest -v --capture=no tests/test_02_burn.py
```

4. Verify the sd card from is bootable by booting a Pi with it. It is 
   assigned a static ip of 10.1.1.253. You can access it with the default 
   raspi os password:
   
```
ssh pi@10.1.1.253
```

5. Move the sd card back to the burning device. On the Pi it is important to 
   unplug and replug in your sd card reader. It is best to verify you can mount 
   and unmount your sd card before proceeding.
   
```
(ENV3) pi@raspberrypi:~/cm/cloudmesh-pi-burn $ cms burn mount
burn mount
/dev/sdb
mounting /dev/sdb1 /media/pi/boot
mounting /dev/sdb2 /media/pi/rootfs
Timer: 0.6463s Load: 0.1716s (line_strip)
(ENV3) pi@raspberrypi:~/cm/cloudmesh-pi-burn $ ls /media/pi/rootfs/
bin   dev  home  lost+found  mnt  proc  run   srv  tmp  var
boot  etc  lib   media       opt  root  sbin  sys  usr
(ENV3) pi@raspberrypi:~/cm/cloudmesh-pi-burn $ cms burn unmount
burn unmount
unmounting /media/pi/boot
unmounting  /media/pi/rootfs
Timer: 7.1469s Load: 0.1706s (line_strip)
```

   
6. Run the clone tests. This will copy the image off of the sd card, shrink 
   it, and copy it back onto the sd card. Verify all tests pass.
   
```
pytest -v -x --capture=no tests/test_03_clone.py
```

7. Verify the sd card from is bootable by booting a Pi with it. It is 
   assigned a static ip of 10.1.1.253. You can access it with the default 
   raspi os password:
   
```
ssh pi@10.1.1.253
```

### Tests Expected to Fail
None as of 2/6/21

### Testing Notes

The test file test_02_burn.py creates a bootable sd card using the cms burn 
commands. This should be a good template to follow for the create command. 

I struggled alot with the sd cards and when they should be loaded or mounted or not mounted, and that effect on formatting and writing the cards.

The big takeaway was:

1.    ensure a card doesn't have a mounted FS while trying to format.
2.    always format a card before buring or copying.
3.    **sudo eject -t /dev/sdb** or its equivalent **cms burn load 
      --device=/dev/sdb** will automatically mount the FS on ubuntu if the 
      device was previously ejected, but not if it is detected but not 
      mounted (i.e. after a **cms burn unmount** ). No automatic mounting on Pi.
4.    However, the **sudo eject -t /dev/sdb** in the burn_format command, 
      ends up 
      not mounting in either case. I think the script moves fast enough, that it prevents this from happening. Although if we have format reliability issues on ubuntu. this might be what to look at. 
