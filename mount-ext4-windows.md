# Links

* <https://github.com/cloudmesh-community/hid-sp18-419/blob/master/cluster/headless_setup.md>
* <https://medium.com/@viveks3th/how-to-bootstrap-a-headless-raspberry-pi-with-a-mac-6eba3be20b26>
  * network setup is not good as it requires additional step, we want to preconfigure on sd card and plug in multiple pis at once not a single one.

# Instructions for ext3/4 File Mounting in Windows

Download the Open source ext3/4 file system driver for Windows installer from

* <http://www.ext2fsd.com/>

Download CommandLineDiskImager from the following url

* <https://github.com/davidferguson/CommandLineDiskImager>

Burn the raspbian image to the SD card with the executable

```CommandLineDiskImager.exe C:\Users\John\Downloads\raspbian.img G```

* Open Ext2fsd exe

* The SD card will 2 partition

* FAT32 partition will be assigned with the Drive letter

* Assign Drive Letter for EXT4 (Right click on the EXT4, Assign letter. 
  The drive letter will be used while running cm-burn)

* Setting Automount of this EXT4

* F3 or Tools->Ext2 Volume Managemnt

* Check-> Automatically mount via Ext2Mgr

# Activate SSH

Draft:

Set up ssh key on windows (use and document the ubbuntu on windows thing)

you will have ~/.ssh/id_rsa.pub and ~/.ssh/id_rsa

copy the content of the file ~/.ssh/id_rsa.pub into ???/.ssh/authorized_keys
??? is the location of the admin user i think the username is pi

enable ssh on the other partition while creating the fike to activate ssh

# Activate Network

# Change default password

From the net (wrong method):

Mount the SD card, go into the file system, and edit /etc/passwd. Find the line starting with "pi" that begins like this:

pi:x:1000:1000...
Get rid of the x; leave the colons on either side. This will eliminate the need for a password.

You probably then want to create a new password by using the passwd command after you log in.

The right thing to do is to create a new hash and store it in place of x.
not yet sure how that can be done a previous student from the class may have been aboe to do that 
Bertholt is firstname.
