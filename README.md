# Cloudmesh Pi Burner for SD Cards

**WARNING:** *This program is designed for a Raspberry Pi and must not
be executed on your laptop or desktop. An earlier version that could
be run on **Linux, macOS, and Windows 10 is no longer supported**. If
you want to help us porting them on any of these OSes, please contact
laszewski@gmail.com*


[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-pi-burn.svg?branch=main)](https://travis-ci.org/TankerHQ/cloudmesn-pi-burn)
[![image](https://img.shields.io/pypi/pyversions/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/v/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


<!--TOC-->

- [Cloudmesh Pi Burner for SD Cards](#cloudmesh-pi-burner-for-sd-cards)
  - [Introduction](#introduction)
  - [Nomenclature](#nomenclature)
  - [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi)
    - [Requirements](#requirements)
    - [Master Pi](#master-pi)
    - [Single Card Burning](#single-card-burning)
    - [Burning Multiple SD Cards with a Single Burner](#burning-multiple-sd-cards-with-a-single-burner)
    - [Connecting Pis to the Internet via Bridge](#connecting-pis-to-the-internet-via-bridge)
  - [Set up of the SSH keys and SSH tunnel](#set-up-of-the-ssh-keys-and-ssh-tunnel)
  - [Manual Pages](#manual-pages)
    - [Manual Page for the `burn` command](#manual-page-for-the-burn-command)
    - [Manual Page for the `bridge` command](#manual-page-for-the-bridge-command)
    - [Manual Page for the `host` command](#manual-page-for-the-host-command)
    - [Manual Page for the `pi` command](#manual-page-for-the-pi-command)
  - [FAQ and Hints](#faq-and-hints)
    - [Can I use the LEDs on the PI Motherboard?](#can-i-use-the-leds-on-the-pi-motherboard)
    - [How can I use pycharm, to edit files or access files in general from my Laptop on the PI?](#how-can-i-use-pycharm-to-edit-files-or-access-files-in-general-from-my-laptop-on-the-pi)
    - [How can I enhance the `get` script?](#how-can-i-enhance-the-get-script)
    - [Can I use a Mesh Network for the setup?](#can-i-use-a-mesh-network-for-the-setup)
    - [Can I use cms burn on Linux?](#can-i-use-cms-burn-on-linux)

<!--TOC-->

## Introduction

`cms burn` is a program to burn many SD cards for the preparation of
building clusters with Raspberry Pi's. It allows users to create
readily bootable SD cards that have the network configured, contain a
public ssh key from your machine that you used to configure the
cards. Thus not much additional setup is needed for a cluster. Another
unique feature is that you can burn multiple cards in a row, each with
their individual setup such as hostnames and ipadresses.


## Nomenclature

* Commands proceeded with `pi@red:$` are to be executed on the
  Rasperry Pi with the name red.

* Commands with `(ENV3) pi@red:$` are to be executed in a virtula ENV
  using Python 3 on the Raspberry Pi with the name red
  
## Quickstart for Bridged WiFi

To provide you with a glimpse on what you can do with cms burn, we
have provided this quickstart guide that will create one master PI and
several workers.

This setup is intended for those who have restricted access to their
home network (ie. cannot access router controls).  For example, those
on campus WiFis or regulated apartment WiFis.

The Figure 1 describes our network configuration. We have 5
Raspberry Pi 4s: 1 master and 4 workers. We have WiFi access, but we
do not necessarily have access to the router's controls.

We also have a network switch, where the master and workers can
communicate locally, but we will also configure the master to provide
internet access to devices on the network switch via a "network
bridge".

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Pi Cluster setup with bridge network

### Requirements

For the quickstart we have the following requirements:

* SD Cards and Raspberry Pis
  
* Master Pi: You will need at least **1 Raspberry Pi** SD Card burned
  using [Raspberry Pi imager](https://www.raspberrypi.org/software/).
  You can use your normal operating system to burn such a card
  including Windows, macOS, or Linux.  Setting up a Raspberry Pi in
  this manner should be relatively straightforward as it is nicely
  documented online (For example,
  [how to setup SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/)).
  All you will need for this guide is an internet connection for your
  Pi. It might also be of use to change the hostname of this Pi.

* You will need an SD card writer (USB tends to work best) to burn new
  cards We recommend that you invest in a USB3 SDCard writer as they
  are significantly faster and you can resuse them on PI'4s

### Master Pi

First we need to configure the Master Pi

**Step 1.** Installing Cloudmesh on the Master Pi

Update pip and the simple curl command below will generate an ssh-key, update your
system, and install cloudmesh.

```
pi@masterpi:~ $ pip install pip -U
pi@masterpi:~ $ curl -Ls https://raw.githubusercontent.com/cloudmesh/get/main/pi/index.html | sh 
# Note: in the future, the command above will be replaced by curl -Ls http://cloudmesh.github.io/get/pi | sh
```

This will take a moment...

**Step 2.** Activate Python Virtual Environment

If you have not already, enter the Python virtual environment provided
by the installation script.

```
pi@masterpi:~ $ source ~/ENV3/bin/activate
```

**Step 3.** Download the latest Raspberry Pi Lite OS

The following command will download the latest images for Raspberry
Lite OS.

```
(ENV3) pi@masterpi:~ $ cms burn image get latest-lite
```

We can verify our image's downloaded with the following.

```
(ENV3) pi@masterpi:~ $ cms burn image ls
```

**Note.** We can use the following command to list the current Raspberry Pi OS versions (full and lite)

```
(ENV3) pi@masterpi:~ $ cms burn image versions --refresh
```

This will list the Tags and Types of each available OS. We can then modify the `image get` command for versions we are interested in. For example,

```
(ENV3) pi@masterpi:~ $ cms burn image get full-2020-05-28
```

**Step 4**. Setup SD Card Writer

Plug your SD Card Writer into the Pi. Ensure you have an SD Card inserted into your writer. Run the following command to find the path to your SD Card.

```
(ENV3) pi@masterpi:~ $ cms burn info
...
# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
| Path     | Info                 | Readable | Formatted | Empty | Size             | Aaccess | Removable | Writeable |
+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
| /dev/sda | Generic Mass-Storage | True     | True      | False | 64.1 GB/59.7 GiB | True    | True      |           |
+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
```

> `cms burn info` has other useful information, but for the purposes of this guide we omit it. 

We can see from the information displayed that our SD card's path is
`/dev/sda`. Of course, this may vary. 

### Single Card Burning

Step 0. Ensure the SD card is inserted.

We can run `cms burn info` again as we did above to verify our 
SD card is connected.

Step 1. Burning the SD Card

Choose a hostname for your card. We will use `red001` with ip `10.1.1.2`. The IP address `10.1.1.1` is reserved for the burner pi (ie. `masterpi`).

> Note we are using the subnet `10.1.1.0/24` in this guide. We currently recommend you do the same, otherwise the WiFi bridge will not configure correctly. We will change this in the future to support other [Private IP Ranges](https://www.arin.net/reference/research/statistics/address_filters/)

```
(ENV3) pi@masterpi:~ $ cms burn create --hostname=red001 --ip=10.1.1.2 --device=/dev/sda --tag=latest-lite
```

Wait for the card to burn. Once the process is complete, it is safe 
to remove the SD card.

We can now proceed to [the bridge setup](#connecting-pis-to-the-internet-via-bridge )

### Burning Multiple SD Cards with a Single Burner

Step 0. Ensure the first SD card is inserted into the burner.

We can run `cms burn info` again as we did above to verify our SD 
card is connected.

Step 2. Burning the Cards

`cms burn` supports logical incremenation of numbers/characters.

For example, `red00[1-2]` is interpreted by cms burn as `[red001, red002]`.
Similarly, `red[a-c]` is interpreted by cms burn as `[reda, redb, redc]`.

We can burn 2 SD cards as follows:

```
(ENV3) pi@masterpi:~ $ cms burn create --hostname=red00[1-2] --ip=10.1.1.[2-3] --device=/dev/sda --tag=latest-lite
```

The user will be prompted to swap the SD cards after each card burn if 
there are still remaining cards to burn.

We can now proceed to the next section where we configure our bridge.

### Connecting Pis to the Internet via Bridge 

Figure 1 depicts how the network is set up with the help of the bridge command.

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Networking Bridge

**Step 0.** Review and Setup

At this point we assume that you have used `cms burn` to create all SD cards for the
Pi's with static IP addresses in the subnet range `10.1.1.0/24` (excluding `10.1.1.1`. See step 1 for details)

We are also continuing to use `masterpi` (which is where we burn the worker SD cards).

We will now use `cms bridge` to connect the worker Pis to the
internet. Let us again reference the diagram of our network setup. You
should now begin connecting your Pis together via network
switch (unmanaged or managed) if you have not done so already. Ensure that `masterpi` is also connected into the network
switch.

**Step 1.** Configuring our Bridge

We can easily create our bridge as follows. 

```
(ENV3) pi@masterpi:~ $ cms bridge create --interface='wlan0'
```

We should now reboot.

```
(ENV3) pi@masterpi:~ $ sudo reboot
```

> Note the `--interface` option indicates the interface 
> used by the master pi to access the internet. 
> In this case, since we are using WiFi, it is 
> likely `wlan0`. Other options such as `eth0` and `eth1` 
> exist for ethernet connections.

**Step 2.** Verifying internet connection 

At this point, our workers should have internet access. Let us SSH into one and ping google.com to verify.

```
(ENV3) pi@masterpi:~ $ ssh red001

pi@red001:~ $ ping google.com
PING google.com (142.250.64.238) 56(84) bytes of data.
64 bytes from mia07s57-in-f14.1e100.net (142.250.64.238): icmp_seq=1 ttl=106 time=48.2 ms
64 bytes from mia07s57-in-f14.1e100.net (142.250.64.238): icmp_seq=2 ttl=106 time=48.3 ms
64 bytes from mia07s57-in-f14.1e100.net (142.250.64.238): icmp_seq=3 ttl=106 time=47.9 ms
64 bytes from mia07s57-in-f14.1e100.net (142.250.64.238): icmp_seq=4 ttl=106 time=47.10 ms
64 bytes from mia07s57-in-f14.1e100.net (142.250.64.238): icmp_seq=5 ttl=106 time=48.5 ms
^C
--- google.com `ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 9ms
rtt min/avg/max/mdev = 47.924/48.169/48.511/0.291 ms
```

Note how we are able to omit the pi user and .local extension. We have successfuly configured our bridge.

## Set up of the SSH keys and SSH tunnel

One important aspect of a cluster is to setup authentication via 
ssh in a convenient way, so we can easily login from the 
laptop to each of the PI 
workers and the PI manager. Furthermore, we like to be able to 
login from the PI manager to each of the workers. In addition, 
we like to be able to login between the workers.

We have chosen a very simple setup while relying on ssh tunnel.

To simplify the setup of this we have developed a command 
`cms host` that gathers and scatters keys onto all machines, 
as well as, sets up the tunnel.

It is essential that that the key on the laptop must 
not be password less. This is also valid for any machine that is directly 
added to the network such as in the mesh notwork. 

To avoid password less keys we recommend you to use `ssh-add` 
or `ssh-keychain` which will ask you for one.

> Note: More information and a concrete example will be documented 
> here shortly.

The manual page for `cms host` is provided in the Manual 
Pages section.

**Step 1.** On the manager create ssh keys for each of the workers.

```
(ENV3) pi@managerpi:~ $ cms host key create red00[1-3]
```

**Step 2.** On the manager gather the worker, manager, 
and your laptop public ssh keys into a file.

```
(ENV3) pi@managerpi:~ $ cms host key gather red00[1-3],you@yourlaptop.local keys.txt
```

**Step 3.** On the manager scatter the public keys to all 
the workers and manager ~/.ssh/authorized_hosts file

```
(ENV3) pi@managerpi:~ $ cms host key scatter red00[1-3],localhost keys.txt
```

**Step 4.** Remove undeeded keys.txt file

```
(ENV3) pi@managerpi:~ $ rm keys.txt
```

**Step 5.** Verify SSH reachability from worker to manager and worker to worker.

```
(ENV3) pi@managerpi:~ $ ssh red001
pi@red001:~ $ ssh masterpi  #bug if manager is still named raspberrypi then the worker might resolve it as 127.0.0.1. Use raspberrypi.local instead.
(ENV3) pi@managerpi:~ $ exit
pi@red001:~ $ ssh red002
pi@red002:~ $ exit
pi@red001:~ $ exit
```

**Step 6.** (For Bridge setup) Create SSH tunnels on the manager 
to enable ssh acces from your laptop to the workers

For now we manually install autossh, to test the new cms host tunnel program. Later we add it to the main master setup script.

```
(ENV3) pi@managerpi:~ $ yes y | sudo apt install autossh
```


```
(ENV3) pi@managerpi:~ $ cms host tunnel create red00[1-3]
```

**Step 7.** (For Bridge setup) Copy the specified command output to 
your `~/.ssh/config` file on your laptop

```
host tunnel create red00[1-3]

Using wlan0 IP = 192.168.1.17
Using cluster hostname = managerpi

Tunnels created.

Please place the following in your remote machine's (i.e. laptop) ~/.ssh/config file to alias simple ssh access (i.e. ssh red001).

# ----------------------------------------------------------------------
# copy to ~/.ssh/config on remote host (i.e laptop)
# ----------------------------------------------------------------------

Host red001
     HostName managerpi.local
     User pi
     Port 8001

Host red002
     HostName managerpi.local
     User pi
     Port 8002

Host red003
     HostName managerpi.local
     User pi
     Port 8003
```

> Note: We will in future provide an addition to the command so you 
> can remove and add
> them directly from the commandline
> 
> ```
> cms host tunnel config create red00[1-3]
> cms host tunnel config delete red00[1-3]
> ```

**Step 8.** (For Bridge setup) Verify SSH reachability from the laptop to workers

```
you@yourlaptop:~ $ ssh red001
```

## Manual Pages

### Manual Page for the `burn` command

Note to execute the command on the commandline you have to type in
`cms burn` and not jsut `burn`.

<!--MANUAL-BURN-->
```
  burn firmware check
  burn install
  burn load --device=DEVICE
  burn format --device=DEVICE
  burn mount [--device=DEVICE] [--os=OS]
  burn unmount [--device=DEVICE] [--os=OS]
  burn network list [--ip=IP] [--used]
  burn network
  burn info [--device=DEVICE]
  burn image versions [--refresh] [--yaml]
  burn image ls
  burn image delete [--image=IMAGE]
  burn image get [--url=URL] [TAG...]
  burn backup [--device=DEVICE] [--to=DESTINATION]
  burn copy [--device=DEVICE] [--from=DESTINATION]
  burn shrink [--image=IMAGE]
  burn create [--image=IMAGE]
              [--device=DEVICE]
              [--hostname=HOSTNAME]
              [--ip=IP]
              [--sshkey=KEY]
              [--blocksize=BLOCKSIZE]
              [--dryrun]
              [--passwd=PASSWD]
              [--ssid=SSID]
              [--wifipassword=PSK]
              [--format]
              [--tag=TAG]
  burn sdcard [TAG...] [--device=DEVICE] [--dryrun]
  burn set [--hostname=HOSTNAME]
           [--ip=IP]
           [--key=KEY]
  burn enable ssh
  burn wifi --ssid=SSID [--passwd=PASSWD] [-ni]
  burn check [--device=DEVICE]

Options:
  -h --help              Show this screen.
  --version              Show version.
  --image=IMAGE          The image filename,
                         e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE        The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME    The hostname
  --ip=IP                The IP address
  --key=KEY              The name of the SSH key file
  --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

Arguments:
    TAG                  Keyword tags to identify an image
                         [default: latest]
Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
    Location where the images will be stored for reuse

Description:
    cms burn create --passwd=PASSWD

         if the passwd flag is added the default password is
         queried from the commandline and added to all SDCards

         if the flag is ommitted login via the password is disabled
         and only login via the sshkey is allowed

  Network

    cms burn network list

        Lists the ip addresses that are on the same network

         +------------+---------------+----------+-----------+
         | Name       | IP            | Status   | Latency   |
         |------------+---------------+----------+-----------|
         | Router     | 192.168.1.1   | up       | 0.0092s   |
         | iPhone     | 192.168.1.4   | up       | 0.061s    |
         | red01      | 192.168.1.46  | up       | 0.0077s   |
         | laptop     | 192.168.1.78  | up       | 0.058s    |
         | unkown     | 192.168.1.126 | up       | 0.14s     |
         | red03      | 192.168.1.158 | up       | 0.0037s   |
         | red02      | 192.168.1.199 | up       | 0.0046s   |
         | red        | 192.168.1.249 | up       | 0.00021s  |
         +------------+----------------+----------+-----------+

    cms burn network list [--used]

        Lists the used ip addresses as a comma separated parameter
        list

           192.168.50.1,192.168.50.4,...

    cms burn network address

        Lists the own network address

         +---------+----------------+----------------+
         | Label   | Local          | Broadcast      |
         |---------+----------------+----------------|
         | wlan0   | 192.168.1.12   | 192.168.1.255  |
         +---------+----------------+----------------+

    cms burn firmware check

        checks if the firmware on the Pi is up to date

    cms burn install

        installs a program to shring img files. THis is useful, after
        you created a backup to make the backup smaller and allow
        faster burning in case of recovery

    cms burn load --device=DEVICE

        loads the sdcard into the USB drive. Thi sis similar to
        loading a cdrom drive. It s the oposite to eject

    cms burn format --device=DEVICE

        formats the SDCard in the specified device. Be careful it is
        the correct device.  cms burn info will help you to identifying it

    cms burn mount [--device=DEVICE] [--os=OS]

        mounts the file systems available on the SDCard

    cms burn unmount [--device=DEVICE] [--os=OS]

        unmounts the mounted file systems from the SDCard

    cms burn info [--device=DEVICE]

        provides useful information about the SDCard

    cms burn image versions [--refresh] [--yaml]

        The images that you like to burn onto your SDCard can be cached locally with the image command.
        The available images for the PI can be found when using the --refresh option. If you do not
        specify it it reads a copy of the image list from our cache

    cms burn image ls

        Lists all downloaded images in our cache. You can download
        them with the cms burn image get command

    cms burn image delete [--image=IMAGE]

        deletes the specified image. The name can be found with the image ls command

    cms burn image get [--url=URL] [TAG...]

        downloads a specific image or the latest image. The tag are a number of words
        separated by a space that must occur in the tag that you find in the versions command

    cms burn backup [--device=DEVICE] [--to=DESTINATION]

        backs up a SDCard to the given location

    cms burn copy [--device=DEVICE] [--from=DESTINATION]

        copies the file form the destination on the SDCard
        this is the same as the SDCard command. we will in future remove one

    cms burn shrink [--image=IMAGE]

        shrinks the size of a backoup or image file that is on
        your local file system. It can only be used for .img files

    cms burn create [--image=IMAGE]
                    [--device=DEVICE]
                    [--hostname=HOSTNAME]
                    [--ip=IP]
                    [--sshkey=KEY]
                    [--blocksize=BLOCKSIZE]
                    [--dryrun]
                    [--passwd=PASSWD]
                    [--ssid=SSID]
                    [--wifipassword=PSK]
                    [--format]

        This is a comprehensif cuntion that not only can format the SDCard, but also
        initializes it with specific falues


    cms burn sdcard [TAG...] [--device=DEVICE] [--dryrun]

        this burns the sd card, see also copy and create

    cms burn set [--hostname=HOSTNAME]
                 [--ip=IP]
                 [--key=KEY]
                 [--mount=MOUNTPOINT]

        this sets specific values on the sdcard after it has ben created
        with the creat, copy or sdcard command

        a --ssh is missing from this command

    cms burn enable ssh [--mount=MOUNTPOINT]

        this enables the ssh server once it is booted

    cms burn wifi --ssid=SSID [--passwd=PASSWD] [-ni]

        this sets the wifi ssid and password afterthe card is created,
        copies, or sdcard is used

    cms burn check [--device=DEVICE]

        this command lists the parameters that were set with the set or create command

Examples: ( \ is not shown)

   > cms burn create --image=2019-09-26-raspbian-buster-lite
   >                 --device=/dev/mmcblk0
   >                 --hostname=red[5-7]
   >                 --ip=192.168.1.[5-7]
   >                 --sshkey=id_rsa

   > cms burn image get latest

   > cms burn image get https://downloads.raspberrypi.org/
   >   raspbian_lite/images/
   >   raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip

   > cms burn image delete 2019-09-26-raspbian-buster-lite


```
<!--MANUAL-BURN-->








### Manual Page for the `bridge` command

Note to execute the command on the commandline you have to type in
`cms bridge` and not jsut `bridge`.

<!--MANUAL-BRIDGE-->
```
Options:
    --interface=INTERFACE  The interface name [default: eth1]
                           You can also specify wlan0 if you wnat
                           to bridge through WIFI on the master
                           eth0 requires a USB to WIFI adapter

Description:

  Command used to set up a bride so that all nodes route the traffic
  trough the master PI.

  bridge create [--interface=INTERFACE]
      creates the bridge on the current device.
      A reboot is required.

```
<!--MANUAL-BRIDGE-->








### Manual Page for the `host` command

Note to execute the command on the commandline you have to type in
`cms host` and not jsut `host`.

<!--MANUAL-HOST-->
```
    host scp NAMES SOURCE DESTINATION [--dryrun]
    host ssh NAMES COMMAND [--dryrun] [--output=FORMAT]
    host config NAMES [IPS] [--user=USER] [--key=PUBLIC]
    host check NAMES [--user=USER] [--key=PUBLIC]
    host key create NAMES [--user=USER] [--dryrun] [--output=FORMAT]
    host key list NAMES [--output=FORMAT]
    host key gather NAMES [--authorized_keys] [FILE]
    host key scatter NAMES FILE

This command does some useful things.

Arguments:
    FILE   a file name

Options:
    --dryrun   shows what would be done but does not execute
    --output=FORMAT  the format of the output

Description:

    host scp NAMES SOURCE DESTINATION

      TBD

    host ssh NAMES COMMAND

      runs the command on all specified hosts
      Example:
           ssh red[01-10] "uname -a"

    host key create NAMES
      create a ~/.ssh/id_rsa and id_rsa.pub on all hosts specified
      Example:
          ssh key create "red[01-10]"

    host key list NAMES

      list all id_rsa.pub keys from all hosts specifed
       Example:
           ssh key list red[01-10]

    host key gather HOSTS FILE

      gathers all keys from file FILE including the one from localhost.

          ssh key gather "red[01-10]" keys.txt

    host key scatter HOSTS FILE

      copies all keys from file FILE to authorized_keys on all hosts,
      but also makes sure that the users ~/.ssh/id_rsa.pub key is in
      the file.

      1) adds ~/.id_rsa.pub to the FILE only if its not already in it
      2) removes all duplicated keys

      Example:
          ssh key scatter "red[01-10]"

    host key scp NAMES FILE

      copies all keys from file FILE to authorized_keys on all hosts
      but also makes sure that the users ~/.ssh/id_rsa.pub key is in
      the file and removes duplicates, e.g. it calls fix before upload

      Example:
          ssh key list red[01-10] > pubkeys.txt
          ssh key scp red[01-10] pubkeys.txt

    host config NAMES IPS [--user=USER] [--key=PUBLIC]

      generates an ssh config file tempalte that can be added to your
      .ssh/config file

      Example:
          cms host config "red,red[01-03]" "198.168.1.[1-4]" --user=pi

    host check NAMES [--user=USER] [--key=PUBLIC]

      This command is used to test if you can login to the specified
      hosts. It executes the hostname command and compares it.
      It provides a table  with a sucess column

      cms host check "red,red[01-03]"

          +-------+---------+--------+
          | host  | success | stdout |
          +-------+---------+--------+
          | red   | True    | red    |
          | red01 | True    | red01  |
          | red02 | True    | red02  |
          | red03 | True    | red03  |
          +-------+---------+--------+


```
<!--MANUAL-HOST-->









### Manual Page for the `pi` command

Note to execute the command on the commandline you have to type in
`cms pi` and not jsut `pi`.


**Note**: Please note that the command `hadoop`, `spark`, and `k3` are
experimental and do not yet work.  In fact the hadoop and spark
deployment are not fullfilling our standard and should not be
used. They will be put into a different command soon so they are not
confusing the used in this README. The command is likely to be called
`pidev`. Once the command is graduated it will be moved into the main
command pi.

There is some very usefull aditional information about how to use the LED and temperature monitoring programs at

* <https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/main/README.md>

<!--MANUAL-PI-->
```
  pi led reset [NAMES]
  pi led (red|green) VALUE
  pi led (red|green) VALUE NAMES [--user=USER]
  pi led list NAMES [--user=USER]
  pi led blink (red|green) NAMES [--user=USER] [--rate=SECONDS]
  pi led sequence (red|green) NAMES [--user=USER] [--rate=SECONDS]
  pi temp NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
  pi free NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
  pi load NAMES [--rate=RATE] [--user=USER] [--output=FORMAT]
  pi hadoop setup [--master=MASTER] [--workers=WORKERS]
  pi hadoop start [--master=MASTER] [--workers=WORKERS]
  pi hadoop stop [--master=MASTER] [--workers=WORKERS]
  pi hadoop test [--master=MASTER] [--workers=WORKERS]
  pi hadoop check [--master=MASTER] [--workers=WORKERS]
  pi spark setup [--master=MASTER] [--workers=WORKERS]
  pi spark start --master=MASTER
  pi spark stop --master=MASTER
  pi spark test --master=MASTER
  pi spark check [--master=MASTER] [--workers=WORKERS]
  pi spark uninstall --master=MASTER [--workers=WORKERS]
  pi k3 install [--master=MASTER] [--workers=WORKERS] [--step=COMMAND]
  pi k3 join --master=MASTER --workers=WORKERS
  pi k3 uninstall [--master=MASTER] [--workers=WORKERS]
  pi k3 delete [--master=MASTER] [--workers=WORKERS]
  pi k3 test [--master=MASTER] [--workers=WORKERS]
  pi k3 view
  pi script list SERVICE [--details]
  pi script list SERVICE NAMES
  pi script list
  pi wifi SSID [PASSWORD] [--dryrun]

This command does some useful things.

Arguments:
    FILE   a file name

Options:
    -f      specify the file


Description:

  This command switches on and off the LEDs of the specified PIs. If
  the hostname is ommitted. IT is assumed that the code is executed on
  a PI and its LED are set. To list the PIs LED status you can use the
  list command

  Examples:

      cms pi led list  "red,red[01-03]"

          lists the LED status of the given hosts

      cms pi led red off  "red,red[01-03]"

          switches off the led of the given PIs

      cms pi led red on  "red,red[01-03]"

          switches on the led of the given PIs

      cms pi led red blink  "red,red[01-03]"

          switches on and off the led of the given PIs

      cms pi led red sequence  "red,red[01-03]"

          goes in sequential order and switches on and off the led of
          the given PIs


```
<!--MANUAL-PI-->











## FAQ and Hints

Here, we provide some usefule FAQs and hints.

### Can I use the LEDs on the PI Motherboard?

> Typically this LED is used to communicate some system related
> information. However `cms pi` can controll it to switch status on
> and off. This is helpful if you like to showcase a particular state
> in the PI. Please look at the manual page. An esample is
> 
> ```bash
> $ cms pi led red off HOSTNAME
> ```
>
> that when executed on the PI (on which you also must have cms
> installed you switch the red LED off. For more options see the
> manual page


### How can I use pycharm, to edit files or access files in general from my Laptop on the PI?

> This is easily possible with the help of SSHFS. To install it we
> refer you to See also: <https://github.com/libfuse/sshfs> SSHFS: add
> master to `.ssh/config` onlocal machine
>
> Let us assume you like to edit fles on a PI that you named `red`
>
> Please craete a `./.ssh/config file that containes the following:
>
> ```
>  Host red
>       HostName xxx.xxx.xxx.xxx
>       User pi
>       IdentityFile ~/.ssh/id_rsa.pub
> ```
> 
> Now let us create a directory in which we mount the remote PI directories
>
> ```
> mkdir master
> sshfs master: master -o auto_cache
> ```

### How can I enhance the `get` script?

Instead of using the link

* <http://cloudmesh.github.io/get/pi>

please use

* <https://raw.githubusercontent.com/cloudmesh/get/main/pi>

This allows us to test also modifications to the get script before we
push them to the official community repository.

You can create a pull request at

* <https://github.com/cloudmesh/get/blob/main/pi/index.html>

### Can I use a Mesh Network for the setup?

This section is still under development.

In case you have a Mesh Network, the setup can typically be even more
simplifies as we can attach the unmanaged router directly to a Mesh
node via a network cable. IN that case the node is directly connected
to the internet and uses the DHCP feature from the Mesh router (see
Figure 2).

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-mesh.png)

Figure 2: Networking with Mesh network

You will not need the bridge command to setup the network.

### Can I use cms burn on Linux?

Nlt everything is supported.

To download the latest Raspberry Pi OS Lite image use

```
cms burn image get latest-lite
```

To see what SDCard writers you have attached, you can use the command

```
cms burn info
```

It will issue a probe of USB devices and see if SDCards can be found.

Identify the `/dev/sdX`, where X is a letter such as b,c,d, ... It
will likely never be a.

sudo apt-get install pv
cms burn sdcard --dev=/dev/sdX
cms burn mount --device=/dev/sdX
cms burn enable ssh
cms burn unmount
```

Take the SDCard into the PI and set it up there. as documented.

### What is the status of the implementation?

| Feature         | PI   | Ubuntu | Mac     | Windows |
| --------------- | ---- | ------ | ------- | ------- |
| image versions  | at + | gt +   | gt +    |         |
| image ls        | at + | gt +   | gt +    |         |
| image delete    | at + | gt +   | gt +    |         |
| image get       | at + | gt +   | gt +    |         |
| info            | a  + | g +    | g +/- 3 |         |
| detect*         |      |        |         |         |
| network         |      | g +?   |         |         |
| backup          | a    | g +    |         |         |
| copy            |      | g +    |         |         |
| shrink install  | a    | gt +   |  -      |         |
| shrink          | a    | g+?    |  -      |         |
| sdcard          |      | gt -   |         |         |
| mount           | a  d | gt +   |         |         |
| unmount         | a  d | gt +   |         |         |
| enable ssh      |      |        |         |         |
| wifi            |   -  |   -    |  -      | -       |
| set             |      |        |         |         |
| create          |      |        |         |         |
| format          | a d  | gt +   |         |         |
| firmware        | a ?  | NA     |  NA     | NA      |

* g = gregor
* r = richie
* a = anthony
* ad = adam
* as = asuri
* ar = arjun

* d = diffrent implementation between Linux and PI (compare)
* 2 = change and add --ssd so its uniform
* ? = needs test
* - = broken
1 = get needs to use the image versions refresh cache
3 = does not report when the USB card is found
t = has a unit test

### What packages do I need to run the info command on macOS

```
brew install libusb
``````

### Are there any unit tests?

As `cms burn` may delete format, delete, and remove files during unit testing users are supposed to first review the 
tests before running them. Please look at the source and see if you can run a test. 

we have the following tests:

* `pytest -v --capture=no tests/test_01_image.py`
  * This test removes files forom ~/.cloudmesh/cmburn/images
  * See also:  [test_01_image.py](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/tests/test_01_image.py)
