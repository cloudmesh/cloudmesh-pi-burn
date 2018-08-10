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

a) start the programm with the appropriate parameters
b) the program will ask you to place an SD Card in the SD Card writer. Place it in
c) the specified image will be burned on the SD Card
d) next the SD Card will be mounted by the program and the appropriate 
   modifications will bbe conducted.
e) after the modifications the SD Card will bbe unmounted
f) you will be asked to remove the card
g) if additional cards need to be burned, you will go to step b

## Prerequisits

### OSX 

Unfortunatly, the free versions of writing the ext file system are no longer supported on OSX. This means tah as of writing of this document the best solution we found is to purcahse and install extFS on the MacOS computer you use for burning the SD Cards. If you find an alternative, please let us know. (We tested ext4fuse, which unfortunately only supports read access, see Appendix)

## Windows

???

# Install

```
git clone https://github.com/cloudmesh-community/cm-burn.git
cd cm-burn
pip install .
```
or

```
pip install git+https://github.com/cloudmesh-community/cm-burn
```

ALL UNTESTED!

# Check install

!! NOT IMPLEMENTED YET

The command

```cm-burn check install```

will check if you have installed all prerequisits and are able to run the command as on some OSes you must be in the sudo list to runi it and access the SDcard burner as well as mounting some file systems.


# Instalation via docker

The following instructions will install cm-burn via docker on your platform

TBD


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


# Links

* https://github.com/cloudmesh/cloudmesh.pi/blob/dev/bin/cm-burn
* http://www.microhowto.info/howto/mount_a_partition_located_inside_a_file_or_logical_volume.html
* http://www.janosgyerik.com/mounting-a-raspberry-pi-image-on-osx/
* https://github.com/Hitabis/pibakery
* http://osxdaily.com/2014/03/20/mount-ext-linux-file-system-mac/
* https://linuxconfig.org/how-to-mount-rasberry-pi-filesystem-image
* https://www.jeffgeerling.com/blogs/jeff-geerling/mounting-raspberry-pis-ext4-sd
* https://blog.hypriot.com/post/cloud-init-cloud-on-hypriot-x64/
