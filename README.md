# cm-burn

:warning: this page is a draft and under development cm-burn is not yet working

`cm-burn` is a program to burn many SD cards for the preparation of building clusters with Raspbberry Pi's. The program is developed in Python and is portable on Linux, Windows, and OSX. It allows users to create readily bootable SD cards that have the 
network configured, contain a public ssh key from your machine that you used to configure the cards. The unique feature is that you can bburn multiple cards in a row.

A sample command invocation looks like:

```
cm-burn —name  red[5,7] \
        -key ~/.ssh/id_rsa.pub \
        —ips 192.168.1.[5,7] \
        —image 2018-06-27-raspbian-stretch
        -password
```
This command creates 3 SD cards where the hostnames red5, red,6, red 7 with the network addresses 192.168.1.5, 192.168.1.6, and 192.168.1.7. The public key is added to the authorized_keys file of the pi user. Via the password flag, a password is interacively asked and set on all cards.

## Process

The process of the burn is as follows.

1. start the programm with the appropriate parameters
   the program will ask you to place an SD Card in the SD Card writer. Place it in
2. the specified image will be burned on the SD Card
3. next the SD Card will be mounted by the program and the appropriate 
   modifications will bbe conducted.
4. after the modifications the SD Card will be unmounted
5. you will be asked to remove the card
6. if additional cards need to be burned, you will go to step 2.

In case a SD Card of a PI in the cluster goes bad, you can simply reburn it by providing the appropriate parameters, and just print the subset that are broken.

## Prerequisits

### Raspberry Pi

We assume that you have set up a raspberry pi with the newest rasbian OS. We assume that you have changed the default password and can log into the pi.

We assume you have not done anything else to the OS.

The easiest way to duplicate the SD card is simply to clone it with the buidl in SD Card copier. This program can be found in the menu under Accessories.

![SD Card Copier](images/sdcc.png) 

Figure: SD Card Copier

This program will copy the contents of the card plugged into the PI onto another one. The only thing you need is an USB SD Card writer. You cn accept the devaults when the cards are plugged in whic allow you to copy the Internal SD Card onto the other one. Just be carefull that you do not overwrite your internal one. This feature can also be used to create backups of images that you have worked on and want to preserve.

Thus as you can see there is not much you need to do to prepare a PI to be used for burning the SD Card.

TODO: Python3

### OSX 

Unfortunatly, the free versions of writing the ext file system are no longer supported on OSX. This means tah as of writing of this document the best solution we found is to purcahse and install extFS on the MacOS computer you use for burning the SD Cards. If you find an alternative, please let us know. (We tested ext4fuse, which unfortunately only supports read access, see Appendix)

To easily read and write ext file systems, please install extFS which can be downloaded from 

* <https://www.paragon-software.com/home/extfs-mac/>

The purchase price of the software is $39.95.

If you like to not spend any money we recommend that you conduct the burning on a raspberry pi.

TODO: PYTHON3 use pyenv

## Windows

TODO: This section has to be written by *Anand*. The following description is incomplete and not yet accurate.

First you need to elevate permissions Python.exe in Windows

* Create a shortcut for python.exe
* Change the shortcut target into something like C:\xxx\...\python.exe your_script.py
* Click "advance..." in the property panel of the shortcut, and click the option "run as administrator"

Download the Open source ext3/4 file system driver for Windows installer from

* <http://www.ext2fsd.com/>

Download CommandLineDiskImager from the following url

* <https://github.com/davidferguson/CommandLineDiskImager>

Burn the raspbian image to the SD card with the executable

```CommandLineDiskImager.exe C:\Users\John\Downloads\raspbian.img G```

* Open Ext2fsd exe
* The SD card will have 2 partition
* FAT32 partition will be assigned with the Drive letter
* Assign Drive Letter for EXT4 (Right click on the EXT4, 
  Assign letter. 
  The drive letter will be used while running cm-burn)
* Setting Automount of this EXT4
* F3 or Tools->Ext2 Volume Managemnt
* Check-> Automatically mount via Ext2Mgr


## Instalation 

### Install on your OS

Once you have decided which Computer system (MacOS, Linux, or Windows) you like to use for using the cm-burn program you need to install it. The program is written in python3 which we assume you have installed and is your default python in your terminal.

To install cm-burn, please execute 
```
git clone https://github.com/cloudmesh-community/cm-burn.git
cd cm-burn
pip install .
```

In future it will also be hosted on pypi and you will be able to install it with 

```
pip install git+https://github.com/cloudmesh-community/cm-burn
```
To check if the program works please issue the command

```cm-burn check install```

It will check if you have installed all prerequisits and are able to run the command as on some OSes you must be in the sudo list to runi it and access the SDcard burner as well as mounting some file systems.


### Instalation on Windows via docker

The following instructions will install cm-burn via docker on your platform

TODO: *Anand* will provide the instructions for Windows. It will use the Linux backend and access the devices from within the docker image in order to execute the program. as such it is very similar to the version provided for the Raspberry PI or a Linux OS based system, but the code runs in a container.

### Usage

TODO: This section has to be updated with the newest cm-burn -h 

The manual page is as follows:

```
cm-burn -h
Cloudmesh Raspberry Pi Mass Image Burner.

Usage:
  cm-burn create --group GROUP --names HOSTS --image IMAGE [--key=KEY]  [--ips=IPS]
  cm-burn gregor --group GROUP --names HOSTS --image IMAGE [--key=KEY]  [--ips=IPS]
  cm-burn ls
  cm-burn rm IMAGE
  cm-burn get [URL]
  cm-burn update
  cm-burn check install
  cm-burn (-h | --help)
  cm-burn --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --key=KEY     the path of the public key [default: ~/.ssh/id_rsa.pub].
  --ips=IPS     th ips in hostlist format

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
  ~/.cloudmesh/inventory
  Location where the images will be stored for reuse

Description:
  cm-burn create --names HOSTS [--key KEY] --image IMAGE --bootdrive BOOTDRIVE --rootdrive ROOTDRIVE --ssid SSID --psk PSK
  cm-burn update
        updates the downloaded images if new once are available
  cm-burn ls
        lists the downloaded images
  cm-burn rm IMAGE
        remove the image
  cm-burn get URL
        downloads the image at the given URL
  cm-burn get jessie
        abbreviation to download a specific version of an image.
        Identify what would be useful.

Example:
  cm-burn create --names red[000-010] ips --image rasbian_latest
```

## Appendix

### OSX ext4fuse

Unfortunately ext4fuse only supports read access. To install it please use the following steps. HOwever it will not allow you to use the cm-burn program. iT may bbe usefule for inspection of SD Cards

On OSX you will need brew and install osxfuse and ext4fuse

```
brew cask install osxfuse
brew install ext4fuse
```

To run it, your account must be in the sudoers list. Than you can do the following

```
mkdir linux
mkdir boot
cp  ../*.img 00.img
brew cask install osxfuse
brew install ext4fuse
hdiutil mount 00.img 
```

This will return 
```
/dev/disk3          	FDisk_partition_scheme         	
/dev/disk3s1        	Windows_FAT_32                 	/Volumes/boot
/dev/disk3s2        	Linux          
```

We can now access the boot partition with 

```
ls /Volumes/boot/
```

This partition is writable as it is not in ext format.

However to access the Linux partition in read only form we need to mount it with fuse

```
sudo mkdir /Volumes/Linux
sudo ext4fuse /dev/disk2s2 /Volumes/Linux -o allow_other
ext4fuse /dev/disk2s2 linux
less linux/etc/hosts
sudo umount /Volumes/Linux 
```

### Activate SSH

see method 3 in <https://www.raspberrypi.org/documentation/remote-access/ssh/>

Draft:

Set up ssh key on windows (use and document the ubbuntu on windows thing)

you will have ~/.ssh/id_rsa.pub and ~/.ssh/id_rsa

copy the content of the file ~/.ssh/id_rsa.pub into ???/.ssh/authorized_keys
??? is the location of the admin user i think the username is pi

enable ssh on the other partition while creating the fike to activate ssh

### Hostname

change /etc/hostname

### Activate Network

see <https://www.raspberrypi.org/learning/networking-lessons/rpi-static-ip-address/>

### Change default password

From the net (wrong method):

Mount the SD card, go into the file system, and edit /etc/passwd. Find the line starting with "pi" that begins like this:

```pi:x:1000:1000...```

Get rid of the x; leave the colons on either side. This will eliminate the need for a password.

You probably then want to create a new password by using the passwd command after you log in.

The right thing to do is to create a new hash and store it in place of x.
not yet sure how that can be done a previous student from the class may have been aboe to do that 
Bertholt is firstname.

could this wokr? <https://unix.stackexchange.com/questions/81240/manually-generate-password-for-etc-shadow>

```python3 -c "from getpass import getpass; from crypt import *; p=getpass(); print('\n'+crypt(p, METHOD_SHA512)) if p==getpass('Please repeat: ') else print('\nFailed repeating.')"```

## Unmount Drives on Windows

RemoveDrive.exe needs to be downloaded to c:\Tools from the following path and to have the Administrator rights (Right Click on the exe -> Properties -> Compatibility Tab -> Run this program as an Administrator

* <https://www.uwe-sieber.de/drivetools_e.html>

See also 

* <https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-psdrive?view=powershell-6>

# Links

* <https://github.com/cloudmesh-community/hid-sp18-419/blob/master/cluster/headless_setup.md>
* <https://medium.com/@viveks3th/how-to-bootstrap-a-headless-raspberry-pi-with-a-mac-6eba3be20b26>
  * network setup is not good as it requires additional step, we want to preconfigure on sd card and plug in multiple pis at once not a single one.
* https://github.com/cloudmesh/cloudmesh.pi/blob/dev/bin/cm-burn
* http://www.microhowto.info/howto/mount_a_partition_located_inside_a_file_or_logical_volume.html
* http://www.janosgyerik.com/mounting-a-raspberry-pi-image-on-osx/
* https://github.com/Hitabis/pibakery
* http://osxdaily.com/2014/03/20/mount-ext-linux-file-system-mac/
* https://linuxconfig.org/how-to-mount-rasberry-pi-filesystem-image
* https://www.jeffgeerling.com/blogs/jeff-geerling/mounting-raspberry-pis-ext4-sd
* https://blog.hypriot.com/post/cloud-init-cloud-on-hypriot-x64/
* https://www.paragon-software.com/home/extfs-mac/
