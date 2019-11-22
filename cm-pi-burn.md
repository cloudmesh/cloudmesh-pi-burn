# cm-pi-burn

# Setup on 'normal' computer

Make sure you have git and Python 3 installed. Use pip to install the following
packages:

- docopt
- pprint
- hostlist
- wget

Find the device the SD card appears as when plugged in (likely `/dev/mmcblk0`).

# Setup on Raspberry Pi

TODO

# Usage

Download the latest Raspbian image:

```
# ./cm-pi-burn.py image get latest
```

Note that the download command is run as root, since images are by default
saved inside the user's home folder and the burn process must be done as root -
thus, the download must also be done as root to put the downloaded image into
root's home folder.

Find the name of the downloaded image:

```
# ./cm-pi-burn.py image ls
```

Alternatively you can download an older image by first listing the available
images and then providing a download URL:

```
# ./cm-pi-burn.py image versions
# ./cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
```

To burn one card:

```
# ./cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                         --device=/dev/mmcblk0
                         --hostname=red2 --ipaddr=192.168.1.2
                         --sshkey=id_ed25519
```

To burn many cards (only change is in hostname/ipaddr args):

```
# ./cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                         --device=/dev/mmcblk0
                         --hostname=red[2-6] --ipaddr=192.168.1.[2-6]
                         --sshkey=id_ed25519
```
