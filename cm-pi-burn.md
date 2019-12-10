# cm-pi-burn

# Setup on 'normal' computer

Make sure you have git and Python 3 installed. Use pip to install the following
packages:

- docopt
- pprint
- python_hostlist
- wget

Find the device the SD card appears as when plugged in (likely `/dev/mmcblk0`).

Additionally, find the name for you SSH public key:

| If your key is located at | its name is |
|---------------------------|-------------|
| ~/.ssh/id_ed25519.pub     | id_ed25519  |
| ~/.ssh/id_rsa.pub         | id_rsa      |

Skip to the 'Usage' section below to run cm-pi-burn.

# Setup on Raspberry Pi

Download the latest Raspbian Desktop image from <https://www.raspberrypi.org/downloads/raspbian/> and unzip it to get a `.img` file. Insert a SD card into your computer and burn it with this image using a program like `cat` or Etcher:

```bash
$ cat raspbian-image-filename.img >/dev/mmcblk0
```

Insert the card into a Raspberry Pi and boot it up. Connect to WiFi via the GUI.

All work should be done as root.

Set the time so that SSL works properly:

```bash
$ timedatectl set-time '2019-12-21 23:59:00'
```

Install the cm-pi-burn python dependencies via pip:

```bash
$ pip3 install docopt pprint python_hostlist wget requests
```

Clone the cm-pi-burn git respository and enter it:

```bash
$ git clone https://github.com/cloudmesh/cm-burn.git
$ cd cm-burn
```

Follow the instructions in the 'Usage' section below.

When you insert a second SD card to the Raspberry Pi, you can use the command
`sudo fdisk -l` to list storage devices and find the name of the second SD card
(it may or may not be `/dev/mmcblk0`, which is used as an example in the
'Usage' section below).

# Usage

First you must install cm-pi-burn. In a future version this will be done with 

```bash
$ pip install cloudmesh-cmburn
```
   
However in the meanwhile you do it as follows:

```bash
$ mkdir cm
$ cd cm
$ git clone git@github.com:cloudmesh/cm-burn.git
$ cd cm-burn
$ pip install -e .
```    

In future we will remove the -e

    $ pip install .


You must create an empty `/media/pi` directory if it does not already exist:

```bash
$ mkdir -p /media/pi
```

Download the latest Raspbian image:

```bash
$ ./cm-pi-burn.py image get latest
```

Note that the download command is run as root, since images are by default
saved inside the user's home folder and the burn process must be done as root -
thus, the download must also be done as root to put the downloaded image into
root's home folder.

Find the name of the downloaded image:

```bash
$ ./cm-pi-burn.py image ls
```

Alternatively you can download an older image by first listing the available
images and then providing a download URL:

```bash
$ ./cm-pi-burn.py image versions
$ ./cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
```

To burn one card:

```
$ ./cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                         --device=/dev/mmcblk0
                         --hostname=red2 --ipaddr=192.168.1.2
                         --sshkey=id_ed25519
```

To burn many cards (only change is in hostname/ipaddr args):

```
$ ./cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                         --device=/dev/mmcblk0
                         --hostname=red[2-6] --ipaddr=192.168.1.[2-6]
                         --sshkey=id_ed25519
```

You may see the program output some unmount errors during the burn process -
this is normal.

The program will ring the terminal bell when one card is done and the next
needs to be inserted (this probably means you can work on other stuff and your
terminal emulator will notify you when cards need to be swapped).
