# cm-pi-burn

THIS NEEDS TO BE MOVED ELSEWHERE

Find the device the SD card appears as when plugged in (likely `/dev/mmcblk0`).


## Setup a Master Raspberry Pi

We recommend that you install first on one Raspberry pi the full
operating system. Please consult with the manuals on how to burn your SD
card.

Download the latest Raspbian Desktop image from
<https://www.raspberrypi.org/downloads/raspbian/> and unzip it to get a
`.img` file. Insert a SD card into your computer and burn it with this
image using a program like Etcher.

Once you have achieved that and configured the OS (dont forget to use a
strong password) you need to update it after the customary reboot.

Make sure your time is set up properly, which you can do with 

```bash
$ sudo date -s "Dec 2, 2019 14:03 EST"
```

and put in the appropriate time string corresponding to your date and
time and time zone.

Now, open a terminal and execute 

```bash
    $sudo apt-get update
    $sudo apt-get full-upgrade
```

Now you have to create an ssh key with the command

```bash
    ssh-keygen
```

Keep the default location and use a strong passphrase. Using no
passphrase is not recommended. You can use `ssh-add` in a terminal so
you do not have to all the time type in your passphrase. Please consult
with the manual aon `ssh-keygen` and `ssh-add`.

## Activate python 3

Next configure python 3 with the help of a virtual env

```bash
    $python3 -venv ~/ENV3
    $ source ~/ENV3/bin/activate
```

Place at the end of your `.bashrc` file the line

```
source ~/ENV3/bin/activate
```
 
Now open a new terminal and see if it has the `(ENV3)` as a prefix to
your command prompt.

If this is the case close all the other windows and use the terminal you
just started.


## Instalation

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

## Finding Image Versions

First you have to find the raspbian image you like to install. For this
purpose we have developed a command that lists you the available images
in the Raspberry Pi repository. To see the versions, please use the command


```bash
$ cm-pi-burn versions
```

Once in a while they come out with new versions. You can refersh the list with

```bash
$ cm-pi-burn versions --refresh
```

## Downloading an Image

To download the newest image, use the command

```bash
$ cm-pi-burn get latest
```

The image is downloaded into the folder

* `~/.cloudmesh/cmburn/images`

To list the downloaded images you can use the command

```bash
$ ./cm-pi-burn.py image ls
```


In case you need other images, you can downloead them while using the label:

NOT YET IMPLEMENTED


```bash
$ cm-pi-burn get raspbian_lite-2019-04-09
```

where the label, is the label that you will get from the versions
command. In case you like to use the latest download, you can use the
command. You can also specify the exact URL with 

NOT YET IMPLEMENTED

```bash
$ cm-pi-burn get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip
```


## Creating Cluster SD-Cards

Next we describe how we create a number of SD-Cards to create a cluster.
Each card will have a unique hostname, an ipaddress and you public key.

To burn one card use:

```
$ sudo cm-pi-burn create --image=2019-09-26-raspbian-buster-lite \
                         --device=/dev/mmcblk0 \
                         --hostname=red2 --ipaddr=192.168.1.2 \
                         --sshkey=~/.ssh/id_rsa.pub
```

To burn many cards you can specify them conveniently in parameter
notation in  the `--hostname` and `--ipaddr` arguments:

```
$ sudo cm-pi-burn create --image=2019-09-26-raspbian-buster-lite \
                         --device=/dev/mmcblk0 \
                         --hostname=red[2-6] --ipaddr=192.168.1.[2-6]\
                         --sshkey=~/.ssh/id_rsa.pub 
```

TODO: clarify this .... we can do this without errors and try except
then and only report the erros that are relevant.


You may see the program output some unmount errors during the burn process -
this is normal.

The program will ring the terminal bell when one card is done and the next
needs to be inserted (this probably means you can work on other stuff and your
terminal emulator will notify you when cards need to be swapped).
