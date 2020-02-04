# cm-pi-burn

This is the location of the new manual page for cm-pi-burn

Please add content here

:o2: address also the issue of the default password, that should be changed or disabled via an option, or a readline. the way how to do this is included in general/cmburn.py see disable password ... it woudl be enough to disable it. i think

# Addressing Issue ... Disabling Default Password


## Quicksatrt

```bash
$ cm-pi-burn.py image get latest
$ cm-pi-burn.py image ls
$ cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                       --device=/dev/mmcblk0
                       --hostname=red[2-6] 
                       --ipaddr=192.168.1.[2-6]
                       --sshkey=id_rsa
```

## Manual Page

:o2: an option is missing to disable or set the default password in the create command

```bash
Cloudmesh Raspberry Pi Image Burner.

Usage:
  cm-pi-burn [-v] info [DEVICE]
  cm-pi-burn [-v] detect
  cm-pi-burn [-v] image versions [--refresh]
  cm-pi-burn [-v] image ls
  cm-pi-burn [-v] image delete [IMAGE]
  cm-pi-burn [-v] image get [URL]
  cm-pi-burn [-v] create [--image=IMAGE]
                         [--device=DEVICE]
                         [--hostname=HOSTNAME]
                         [--ipaddr=IP]
                         [--sshkey=KEY]
                         [--blocksize=BLOCKSIZE]
                         [--dryrun]
  cm-pi-burn [-v] burn [IMAGE] [DEVICE] --[dryrun]
  cm-pi-burn [-v] mount [DEVICE] [MOUNTPOINT]
  cm-pi-burn [-v] set hostname [HOSTNAME] [MOUNTPOINT]
  cm-pi-burn [-v] set ip [IP] [MOUNTPOINT]
  cm-pi-burn [-v] set key [KEY] [MOUNTPOINT]
  cm-pi-burn [-v] enable ssh [MOUNTPOINT]
  cm-pi-burn [-v] unmount [DEVICE]
  cm-pi-burn [-v] wifi SSID [PASSWD] [-ni]
  cm-pi-burn (-h | --help)
  cm-pi-burn --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --image=IMAGE          The image filename, e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE        The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME    The hostname
  --ipaddr=IP            The IP address
  --key=KEY              The name of the SSH key file [default: id_rsa]
  --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
    Location where the images will be stored for reuse

Description:
  cm-pi-burn

Example:
  cm-pi-burn create --image=2019-09-26-raspbian-buster-lite --device=/dev/mmcblk0
                    --hostname=red[5-7] --ipaddr=192.168.1.[5-7] --sshkey=id_rsa
  cm-pi-burn.py image get latest
  cm-pi-burn.py image delete 2019-09-26-raspbian-buster-lite
  cm-pi-burn.py image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip

```
