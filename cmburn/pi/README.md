# cm-pi-burn

WARNING: This program is designed for a Raspberry Pi and must not be
executed on your laptop

## Setup a Master Raspberry Pi

We recommend that you install first on one Raspberry pi. The process is
documented at

* <https://www.raspberrypi.org/downloads/>

The first thing you need to do is install a regular image burning
program. We recommend you use Raspberry PI Imager, but you can also
choose Etcher.

As for the image, we want to use Raspbian and not Noobs, as Raspbian is
the official supported OS. We use this OS on the master.

Please follow the instructions carefully.

Download the latest Raspbian Desktop image from

* <https://www.raspberrypi.org/downloads/raspbian/> 

and unzip it to get a `.img` file. Insert an SD card into your computer
and burn it with this image using a program like Etcher.

Once you have downloded imager and installed in your OS, and started it will look like:

![Imager](images/imager.png)
 
You can now chose the image and the SD Crad where you want to burn it.
Make sure you select the card correctly as to avoid destroying the OS on the 
computer that starts imager.
 
## Starting the Pi


Once you have achieved that and configured the OS (do not forget to use
a strong password), you need to update it after the customary reboot. 

Make sure your time is set up properly, which you can do with 

```bash
$ sudo date -s "Jan 2, 2020 14:03 EST"
```

and put in the appropriate time string corresponding to your date and
time and time zone.

Now, open a terminal and execute 

```bash
$ sudo apt-get update
$ sudo apt-get full-upgrade
```

Now you have to create an ssh key with the command.

```bash
$ ssh-keygen
```

Keep the default location and use a strong passphrase but do not use the
same as you have used for your login. Using no passphrase is not
recommended. You can use `ssh-add` in a terminal, so you do not have to
all the time type in your passphrase. Please consult with the manual on
`ssh-keygen` and `ssh-add`.

## Activate python 3

Next, configure python 3 with the help of a virtual env

```bash
$ python3 -m venv ~/ENV3
$ source ~/ENV3/bin/activate
```

Place at the end of your `.bashrc` file the line

```
$ source ~/ENV3/bin/activate
```
 
Now open a new terminal and see if it has the `(ENV3)` as a prefix to
your command prompt.

If this is the case close all the other windows and use the terminal you
just started.


## Installation

First, you must install cm-pi-burn. In a future version, this will be done
with

```bash
$ pip install cloudmesh-cmburn
```
   
However, in the meanwhile, you do it as follows:

```bash
$ mkdir cm
$ cd cm
$ git clone https://github.com/cloudmesh/cloudmesh_pi_burn.git
$ cd cloudmesh_pi_burn
$ pip install -e .
```    

In the future, we will remove the -e

```bash
$ pip install .
```

## Information about the SD Cards and Card Writer

You need at least one SD Card writer. However, cm-pi-burn is
supposed to work also with a USB hub in which you can plug in
multiple SD Cards and burn one card at a time. Once done, you can add a
new batch, and you can continue writing. This is done for all specified
hosts so that you can minimize the interaction with the SD cards.

To find out more about the Card writers and the SD Cards, you can use
the command

```bash
$ cm-pi-burn detect
```

It will first ask you to not plug in the SDCard writer to probe the
system in empty status. Then you need to plug in the SD Card writer
and with the cards in it. After you have said yes once you plugged
them in, you will see an output similar to: 

```
# ----------------------------------------------------------------------
# Detecting USB Card Reader
# ----------------------------------------------------------------------

Make sure the USB Reader is removed ...
Is the reader removed? (Y/n) 
Now plug in the Reader ...
Is the reader pluged in? (Y/n) 

# ----------------------------------------------------------------------
# Detected Card Writer
# ----------------------------------------------------------------------

Bus 002 Device 020: ID 045b:0210 Hitachi, Ltd 
Bus 002 Device 024: ID 05e3:0749 Genesys Logic, Inc. 
Bus 001 Device 014: ID 045b:0209 Hitachi, Ltd 
Bus 001 Device 015: ID 045b:0209 Hitachi, Ltd 
Bus 001 Device 016: ID 05e3:0749 Genesys Logic, Inc. 
Bus 002 Device 023: ID 05e3:0749 Genesys Logic, Inc. 
Bus 002 Device 019: ID 045b:0210 Hitachi, Ltd 
Bus 002 Device 021: ID 05e3:0749 Genesys Logic, Inc. 
Bus 002 Device 022: ID 05e3:0749 Genesys Logic, Inc. 
```

Note that in this case, we will see two devices, one for the USB hub in
which the card is plugged in, and one for the SD Card itself.

Next, we like to show you a bit more useful information while probing
the operating system when the SD Card  Writers are plugged in. Please
call the command:

```bash
$ cm-pi-burn info
```

You will see an output similar to 

```
# ----------------------------------------------------------------------
# Operating System
# ----------------------------------------------------------------------

Disk /dev/mmcblk0: 29.7 GiB, 31914983424 bytes, 62333952 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x5e3da3da

Device         Boot  Start      End  Sectors  Size Id Type
/dev/mmcblk0p1        8192   532479   524288  256M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      532480 62333951 61801472 29.5G 83 Linux

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+------+----------+--------+----------+-------+-------------------+-----------+-----------+
| Name | Device   | Reader | Formated | Empty | Size              | Removable | Protected |
+------+----------+--------+----------+-------+-------------------+-----------+-----------+
| sde  | /dev/sde | True   | True     | True  |  31.9 GB/29.7 GiB | True      | False     |
| sdd  | /dev/sdd | True   | True     | False |  31.9 GB/29.7 GiB | True      | False     |
| sdc  | /dev/sdc | True   | True     | True  |  31.9 GB/29.7 GiB | True      | False     |
| sdb  | /dev/sdb | True   | True     | False |  31.9 GB/29.7 GiB | True      | False     |
| sda  | /dev/sda | True   | True     | False |  31.9 GB/29.7 GiB | True      | False     |
+------+----------+--------+----------+-------+-------------------+-----------+-----------+
```

Under `Operating System` you will see the block device you will see
information about your operating system. This is the card plugged into
the back of your PI.

Under SDCards found you will see the list of SD Cards and some
information about the cards that are plugged into the writers.

Make sure that you only include cards that you truly want to overwrite.
We have given an example where this is not the case while indicating it
in the Empty column. We recommend that you only use formatted cards, so
you are sure you do not by accident delete information.

## ROOT

For the burn process, you need to use root privileges. To achieve this,
you need to execute the following commands. The source command
activates the python virtual env that you have created where you
installed the cm-pi-burn command

```bash
$ sudo su
# source /home/pi/ENV3/bin/activate
```

Please note that for our notation a `#` indicates this command is
executed in root.

## Finding Image Versions

First, you have to find the raspbian image you like to install. For this
purpose, we have developed a command that lists you the available images
in the Raspberry Pi repository. To see the versions, please use the
command

```bash
# cm-pi-burn image versions
```

Once in a while, they come out with new versions. You can refresh the
list with

```bash
# cm-pi-burn image versions --refresh
```

## Downloading an Image

To download the newest image, use the command

```bash
# cm-pi-burn image get latest
```

The image is downloaded into the folder

* `~/.cloudmesh/cmburn/images`

To list the downloaded images, you can use the command

```bash
# cm-pi-burn image ls
```

In case you like to use the latest download, you can use the
command. You can also specify the exact URL with 

```bash
# cm-pi-burn image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip
```

## Creating Cluster SD-Cards

Next, we describe how we create a number of SD-Cards to create a cluster.
Each card will have a unique hostname, an IP address and your public key. 
To locate your device, you can use:

```bash
$ sudo fdisk -l

```
or the more convenient option would be to use the

```bash
$ cm-pi-burn info  
```

You can look at the names of your devices under the device column. Eg
/dev/sda,/dev/sdb,etc

## Burning SD-Cards

To burn one card, we will use ` cm-pi-burn create ` with several
important options:

* `--image` specifies the name of the image to burn
* `--device` is the path to the SD card. If this option is omitted,
  then `cm-pi-burn` will use the devices listed under `cm-pi-burn info`
* `--hostname` is the name for the pi
* `--sshkey` is the path to your SSH PUBLIC key
* `--blocksize` specified to 4M for our purposes

If you want to specify a password for desktop login (for debugging
purposes), you can use the option

* `--passwd=PASSWD` 

to set a password. In the future, you should not use this option as we
do not want to login through the terminal. We only want to SSH from the
master Pi.

### Auto Format to FAT32

The `--format` is an option that can be used to automatically format
your SD card to FAT32. The current implementation is quite unstable as
it makes several assumptions. If this option is used, it will most
likely work.

Do not worry if you see the message `No partition is defined yet!`

### Note on using a static IP address

You can use the `--ipaddr=IP` option to set a static IP address for your
Pis. To make sure this works, ensure that your master Pi is connected to
the network as cm-pi-burn will pull information from the network to
configure static IP usage.

For more information on options, see `/cmburn/pi/cmpiburn.py`

Here is an example call of the command `create` using a static IP
address connecting to a home wifi network

```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --device=/dev/sda \
    --hostname=red2 \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.30 \
    --format
```

Here we are assuming that your device name is sda, but its very important
to verify it once before executing the above command. Note that if we
omit the `--device` option, then `cm-pi-burn` will refer to the devices
listed using `cm-pi-burn info`

If your Pis are going to use ethernet connection, then the command is as
simple as:

```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --device=/dev/sda \
    --hostname=red2 \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.32 \
    --format
```

To burn many cards, you can specify them conveniently in parameter
notation in  the `--hostname` and `--ipaddr` arguments:

```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --device=/dev/sd[a-f]
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub 
    --blocksize=4M
    --ipaddr=169.254.10.[32-37] \
    --format
```

Note the ranges are inclusive. Alternatively, we can omit the --device
option and allow cm-pi-burn to detect the devices from `cm-pi-burn
info`:

```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.[32-37] \
    --format
```


You may see the program output some unmount errors during the burn
process - this is normal.

After the process is completed, a message will appear on your terminal
stating the number of cards you have burnt.

You can verify if the burn process is completed or not by plugging in
one of the SD cards to a Raspberry Pi and starting it. Raspberry Pi
terminal appears asking your login and password. After the successful
authentication, now you can use your raspberry pi just like any other.


Here is an alternative version to the command above with a different
`--device` option.


```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --device=/dev/sda \
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.[32-37] \
    --format
```

Notice here how we have only listed one port in the `--device` option.
This would be in the case that we only have one SD card writer, but we
don't want to rerun the command each time. That would be quite tedious.
Instead, the command will burn to `/dev/sda` with hostname red2, then a
prompt will come up asking the user if we want to reuse `/dev/sda`.

```
Slot /dev/sda needs to be reused. Do you wish to continue? [y/n] 
# y
Insert next card and press enter...
# [enter]
Burning next card...
```

In this way, we avoid having to rerun the command while providing enough
safeguards so we don't accidentally overwrite the last SD card. This
prompt will also appear if the number of hosts (in this example there
are 4 hosts) exceeds the number of available devices (1 in this
example).

If the only device listed under `cm-pi-burn info` is `/dev/sda`, then the
above command is equivalent to:

```bash
# cm-pi-burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.[32-37] \
    --format
```


## From the raspberry FAQ

Quote:
    There is no on/off switch! To switch on, just plug it in. To switch
    off, if you are in the graphical environment, you can either log out
    from the main menu, exit to the Bash prompt, or open the terminal.
    From the Bash prompt or terminal, you can shut down the Raspberry Pi
    by entering sudo halt `-h`. Wait until all the LEDs except the power
    LED are off, then wait an additional second to make sure the SD card
    can finish its wear-leveling tasks and write actions. You can now
    safely unplug the Raspberry Pi. Failure to shut the Raspberry Pi
    down properly may corrupt your SD card, which would mean you would
    have to re-image it.
    
LED control:
    See Gregor's pi book there is a section describing how to do it
    
    See also: <https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi>
    
    There may be more resources. We can use this to test which node is
    which. E.g develop a class that sets the LEDs on one or more from
    the master with ssh
    
    See also:
    <https://www.raspberrypi.org/forums/viewtopic.php?t=12530>

SSHFS:
   add master to `.ssh/config` onlocal machine

    ```
   Host master
         HostName xxx.xxx.xxx.xxx
         User pi
         IdentityFile ~/.ssh/id_rsa.pub

   mkdir master
   sshfs master: master
    ```

    See also: <https://github.com/libfuse/sshfs>
