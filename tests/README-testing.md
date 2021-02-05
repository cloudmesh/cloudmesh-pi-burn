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
    - Prequsite: A copy of the latest-lite image is saved in ~/.
      cloudmesh/cmburn/images
    - Purpose: Test most cms burn functions, excluding sdcard cloning 
      functions.
    - Output: An sd card imaged with latest-lite accessible at pi@ 10.1.1.
      253 with the default raspi os password
3. **test_03_clone.py**
    - Prequisite: A functional burned card, enough storage space to store an 
      block copy of the SD card. You cannot run this on the pi with an sd 
      card the same size as your pi's OS sd card. This is why the tests were 
      separate. That and an entire bit-by-it copy of 64 GB can take some time.
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
1. **test_configure_wifi:** underlaying function not yet implemented.
