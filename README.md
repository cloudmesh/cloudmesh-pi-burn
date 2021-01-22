# Cloudmesh Pi Burner for SD Cards

**WARNING:** *This program is designed for a Raspberry Pi and must not be
executed on your laptop or desktop. An earlier version that could be run on **Linux, 
macOS, and Windows 10 is no longer supported**. If you want to help us porting them 
on any of these OSes, please contact laszewski@gmail.com*


[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-pi-burn.svg?branch=main)](https://travis-ci.org/TankerHQ/cloudmesn-pi-burn)
[![image](https://img.shields.io/pypi/pyversions/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/v/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn/)
[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-pi-burn.svg)](https://github.com/TankerHQ/python-cloudmesh-pi-burn/blob/main/LICENSE)


<!--TOC-->

- [Cloudmesh Pi Burner for SD Cards](#cloudmesh-pi-burner-for-sd-cards)
  - [cms burn](#cms-burn)
  - [Nomenclature](#nomenclature)
  - [Quickstart for Restricted WiFi Access](#quickstart-for-restricted-wifi-access)
    - [Requirements](#requirements)
    - [Master Pi](#master-pi)
    - [Single Card Burning](#single-card-burning)
    - [Burning Multiple SD Cards with a Single Burner](#burning-multiple-sd-cards-with-a-single-burner)
    - [Connecting Pis to the Internet via Bridge](#connecting-pis-to-the-internet-via-bridge)
  - [Quickstart Guide for Mesh Networks](#quickstart-guide-for-mesh-networks)
  - [Manual burn](#manual-burn)
  - [Manual bridge](#manual-bridge)
  - [STUFF TO BE DELETED OR INTEGRATED IN REST OF DOCUMENT](#stuff-to-be-deleted-or-integrated-in-rest-of-document)
  - [Step 4(alt). Burning Multiple Cards](#step-4alt-burning-multiple-cards)
  - [DEPRECATED. DO NOT GO BEYOND THIS LINE AS THE DOCUMENTATION IS OUT OF DATE](#deprecated-do-not-go-beyond-this-line-as-the-documentation-is-out-of-date)
    - [Installation](#installation)
    - [Information about the SD Cards and Card Writer](#information-about-the-sd-cards-and-card-writer)
    - [Finding Image Versions](#finding-image-versions)
    - [Downloading an Image](#downloading-an-image)
    - [ROOT](#root)
    - [Creating Cluster SD-Cards](#creating-cluster-sd-cards)
    - [Burning SD-Cards](#burning-sd-cards)
    - [Auto Format to FAT32](#auto-format-to-fat32)
    - [Note on using a static IP address](#note-on-using-a-static-ip-address)
    - [From the raspberry FAQ](#from-the-raspberry-faq)

<!--TOC-->

## cms burn

`cms burn` is a program to burn many SD cards for the preparation of
building clusters with Raspberry Pi's. It allows users to
create readily bootable SD cards that have the network configured,
contain a public ssh key from your machine that you used to configure
the cards. Thus not much additional setup is needed for a cluster. Another unique 
feature is that you can burn multiple cards in a row, each with their 
individual setup such as hostnames and ipadresses.


## Nomenclature

* Commands proceeded with `pi@red:$` are to be executed on the Rasperry
  Pi with the name red.

* Commands with `(ENV3) pi@red:$` are to be executed in a virtula ENV
  using Python 3 on the Raspberry Pi with the name red
  
## Quickstart for Restricted WiFi Access

To provide you with a glimpse on what you can do with cms burn, we have 
provided this quickstart guide that will create one master PI and several 
workers.

This setup is intended for those who have restricted access to their home network (ie. cannot access router controls). 
For example, those on campus WiFis or regulated apartment WiFis.

The figure below describes our network configuration. We have 5 Raspberry Pi 4s: 1 master and 4 workers. We have WiFi access, but we do not necessarily have access to the router's controls.

We also have a network switch, where the master and workers can communicate locally, but we will also configure the master to provide internet access to devices on the network switch via a "network bridge".

![](images/network-bridge.png)

### Requirements

For the quickstart we have the following requirements:

* SD Cards and Raspberry Pis
  
* Master Pi: You will need at least **1 Raspberry Pi** SD Card burned 
  using [Raspberry Pi imager](https://www.raspberrypi.org/software/). 
  You can use your normal operating system to burn such a card including Windows, macOS, or Linux. 
  Setting up a Raspberry Pi in this manner should be relatively straightforward 
  as it is nicely documented online (For example, 
  [how to setup SSH](https://www.raspberrypi.org/documentation/remote-access/ssh/)). 
  All you will need for this guide is an internet connection for your Pi. It might also be of use to change the hostname of this Pi.

* You will need an SD card writer (USB tends to work best) to burn new cards
  We recommend that you invest in a USB3 SDCard writer as they are significantly 
  faster and you can resuse them on PI'4s

### Master Pi

**Step 1.** Installing Cloudmesh on the Master Pi

The simple curl command below will generate an ssh-key, update your system, 
and install cloudmesh.

```
pi@masterpi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh
```

This will take a moment...

**Step 2.** Activate Python Virtual Environment

If you have not already, enter the Python virtual environment provided by 
the installation script.

```
pi@masterpi:~ $ source ~/ENV3/bin/activate
```

**Step 3.** Download the latest Raspberry Pi Lite OS

The following command will download the latest images for Raspberry Lite OS.

```
(ENV3) pi@masterpi:~ $ cms burn image get latest
```

We can verify our image's downloaded with the following.

```
(ENV3) pi@masterpi:~ $ cms burn image ls
```

**Step 4**. Setup SD Card Writer

Run the following command to setup your SD Card Writer with cms burn. It will provide a sequence of instructions to follow.

```
(ENV3) pi@masterpi:~ $ cms burn detect

Make sure the USB Reader(s) is removed ...
Is the reader(s) removed? y/n
Now plug in the Reader(s) ...
Is the reader(s) plugged in? y/n

# ----------------------------------------------------------------------
# Detected Card Writers
# ----------------------------------------------------------------------

Bus 001 Device 003: ID 1908:0226 GEMBIRD
```

Now insert one of the worker (orange) SD cards into your writer.

Running the following command will provide us information on our SD card's location on the system. 

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

We can see from the information displayed that our SD card's path is `/dev/sda`. Of course, this may vary. Let us record this path for `cms burn` access.

```
(ENV3) pi@masterpi:~ $ export DEV=/dev/sda
```

`cms burn` is now properly configured and ready to begin burning cards. See the following sections on burning that are in accordance with your setup.

### Single Card Burning

Step 0. Ensure the SD card is inserted.

We can run `cms burn info` again as we did above to verify our 
SD card is connected.

Step 1. Burning the SD Card

Choose a hostname for your card. We will use `red001`.

```
(ENV3) pi@masterpi:~ $ cms burn create --hostname=red001
```

Wait for the card to burn. Once the process is complete, it is safe 
to remove the SD card.


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
(ENV3) pi@masterpi:~ $ cms burn create --hostname=red00[1-2]
```

The user will be prompted to swap the SD cards after each card burn if 
there are still remaining cards to burn.


QUESTION: Do we not also need the ip address? Why burn if we do not have 
network, or is this working with DHCP?

ANSWER: `cms bridge` is what handles ip address assignments. This centralized program allows us to manage the ip addresses of all nodes in the cluster via the master. It runs as a DHCP server so we can automatically handle ip address assignments. `cms bridge` also allows users to assign static IPs to nodes in their cluster. See [cms bridge documentation](https://github.com/cloudmesh/cloudmesh-pi-cluster/blob/main/cloudmesh/bridge/README.md#a-simple-command-to-setup-a-network-bridge-between-raspberry-pis-and-a-manager-pi-utilizing-dnsmasq) for more information. 

If, however, the user wishes to strictly assign a static IP at the time of burning, they may use the `--ipaddr=IP` as noted in the [cms burn manual](https://github.com/cloudmesh/cloudmesh-pi-burn#manual-burn). The behavior of this parameter is very similar to the hostnames parameter. For example, `10.1.1.[1-3]` evaluates to `[10.1.1.1, 10.1.1.2, 10.1.1.3]`

### Connecting Pis to the Internet via Bridge


![](images/network-bridge.png)

Figure: Networking Bridge

Step 0. Recap and Setup

At this point we assume that you have used `cms burn` to create all SD cards for the
Pi's.

We are also continuing to use `masterpi` (which is where we burn the worker SD cards).

We will now use `cms bridge` to connect the worker Pis to the internet. Let us again reference the diagram of our network setup. You should now begin connecting your Pis together via network switch. Ensure that `masterpi` is also connected into the network switch.

Step 1. Verify Local Connection to Workers

Ensure your workers are booted and that your network switch is turned on. Once the Pis are done booting up, we will verify our local connections to them on the network switch via SSH.


> Note: To figure out when a Pi is done completing its initial bootup process, 
> the green light on the Pi will flash periodically until the bootup/setup is complete. 
> Once there is just a red light for a period, the Pi is ready.


Once your setup is configured in this manner, Pi Master should be able to ssh 
into each node via its hostname. For example, if one of our workers is 
`red001`, we may ssh to them as follows:

```
(ENV3) pi@masterpi:~ $ ssh pi@red001.local
```

If this is successful, you are ready to connect your workers to the internet.

Step 2. Configuring our Bridge

At this point, the master pi can talk to the workers via the network switch. However, these
burned Pis do not have internet access. It can be very tedious to connect each Pi individually to our WiFi. So we provide a command to "bridge" internet access between the burner Pi and the burned Pis. This program should already be installed by the cloudmesh installation script.

We can easily create our bridge as follows. 

```
(ENV3) pi@masterpi:~ $ cms bridge create --interface='wlan0'
```

This will take a moment while the dependencies are installed...

> Note the `--interface` option indicates the interface used by the master pi to access the internet. In this case, since we are using WiFi, it is most likely `wlan0`. Other options such as `eth0` and `eth1` exist for ethernet connections.

Once the installations are complete, let us restart the bridge to reflect these changes.

```
(ENV3) pi@masterpi:~ $ cms bridge restart --background
```

> Note the use of `--background` in this case is recommended as the process may potentially break a user's SSH pipeline (due to WiFi). If this is the case, the program will continue in the background without error and the user will be able to SSH shortly after.

Once the process is complete, we can use the following command to list our connected devices.

```
(ENV3) pi@masterpi:~ $ cms bridge info
bridge info

# ----------------------------------------------------------------------
#
# IP range: 10.1.1.2 - 10.1.1.122
# Manager IP: 10.1.1.1
#
# # LEASE HISTORY #
# 2021-01-21 06:04:08 dc:a6:32:e8:01:a3 10.1.1.84 red001 01:dc:a6:32:e8:01:a3
# 2021-01-21 06:04:08 dc:a6:32:e7:f0:fb 10.1.1.12 red003 01:dc:a6:32:e7:f0:fb
# 2021-01-21 06:04:08 dc:a6:32:e8:02:cd 10.1.1.22 red004 01:dc:a6:32:e8:02:cd
# 2021-01-21 06:04:08 dc:a6:32:e8:06:21 10.1.1.39 red002 01:dc:a6:32:e8:06:21
# ----------------------------------------------------------------------
```

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
--- google.com ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 9ms
rtt min/avg/max/mdev = 47.924/48.169/48.511/0.291 ms
```

Note how we are able to omit the pi user and .local extension

The cluster is now complete.

## Quickstart Guide for Mesh Networks 

Gregor does this.

![](images/network-mesh.png)

Figure: Networking with bridge


## Manual burn

<!--MANUAL-BURN-->
```
  burn network list [--ip=IP] [--used]
  burn network
  burn info [DEVICE]
  burn detect
  burn image versions [--refresh]
  burn image ls
  burn image delete [IMAGE]
  burn image get [URL]
  burn create [--image=IMAGE]
                         [--device=DEVICE]
                         [--hostname=HOSTNAME]
                         [--ipaddr=IP]
                         [--sshkey=KEY]
                         [--blocksize=BLOCKSIZE]
                         [--dryrun]
                         [--passwd=PASSWD]
                         [--ssid=SSID]
                         [--wifipassword=PSK]
                         [--format]
  burn burn [IMAGE] [DEVICE] --[dryrun]
  burn mount [DEVICE] [MOUNTPOINT]
  burn set host [HOSTNAME] [MOUNTPOINT]
  burn set ip [IP] [MOUNTPOINT]
  burn set key [KEY] [MOUNTPOINT]
  burn enable ssh [MOUNTPOINT]
  burn unmount [DEVICE]
  burn wifi SSID [PASSWD] [-ni]

Options:
  -h --help              Show this screen.
  --version              Show version.
  --image=IMAGE          The image filename,
                         e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE        The device, e.g. /dev/mmcblk0
  --hostname=HOSTNAME    The hostname
  --ipaddr=IP            The IP address
  --key=KEY              The name of the SSH key file
  --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]

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

Examples: ( \ is not shown)

   > cms burn create --image=2019-09-26-raspbian-buster-lite
   >                 --device=/dev/mmcblk0
   >                 --hostname=red[5-7]
   >                 --ipaddr=192.168.1.[5-7]
   >                 --sshkey=id_rsa

   > cms burn image get latest

   > cms burn image get https://downloads.raspberrypi.org/
   >   raspbian_lite/images/
   >   raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip

   > cms burn image delete 2019-09-26-raspbian-buster-lite


```
<!--MANUAL-BURN-->





## Manual bridge

<!--MANUAL-BRIDGE-->
```
  bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE] [--purge]
  bridge set HOSTS ADDRESSES 
  bridge restart [--nohup] [--background]
  bridge status
  bridge test HOSTS [--rate=RATE]
  bridge list NAMES
  bridge check NAMES [--configuration] [--connection]
  bridge info

Arguments:
    HOSTS        Hostnames of connected devices. 
                 Ex. red002
                 Ex. red[002-003]

    ADDRESSES    IP addresses to assign to HOSTS. Addresses
                 should be in the network range configured.
                 Ex. 10.1.1.2
                 Ex. 10.1.1.[2-3]

    NAMES        A parameterized list of hosts. The first hostname 
                 in the list is the master through which the traffic 
                 is routed. Example:
                 blue,blue[002-003]

Options:
    --interface=INTERFACE  The interface name [default: eth1]
                           You can also specify wlan0 if you wnat
                           to bridge through WIFI on the master
                           eth0 requires a USB to WIFI adapter

    --ip=IPADDRESS         The ip address [default: 10.1.1.1] to assign the master on the
                           interface. Ex. 10.1.1.1

    --range=IPRANGE        The inclusive range of IPs [default: 10.1.1.2-10.1.1.122] that can be assigned 
                           to connecting devices. Value should be a comma
                           separated tuple of the two range bounds. Should
                           not include the ip of the master
                           Ex. 10.1.1.2-10.1.1.20

    --workers=WORKERS      The parametrized hostnames of workers attatched to the bridge.
                           Ex. red002
                           Ex. red[002-003]

    --purge       Include option if a full reinstallation of dnsmasq is desired

    --background    Runs the restart command in the background. stdout to bridge_restart.log

    --nohup      Restarts only the dnsmasq portion of the bridge. This is done to surely prevent SIGHUP if using ssh.

    --rate=RATE            The rate in seconds for repeating the test
                           If ommitted its done just once.

Description:

  Command used to set up a bride so that all nodes route the traffic
  trough the master PI.

  bridge create [--interface=INTERFACE] [--ip=IPADDRESS] [--range=IPRANGE]
      creates the bridge on the current device
      The create command does not restart the network.

  bridge set HOSTS ADDRESSES 
      the set command assigns the given static 
      ip addresses to the given hostnames.

  bridge status
      Returns the status of the bridge and its linked services.

  bridge restart [--nohup]
      restarts the bridge on the master without rebooting. 

  bridge test NAMES
      A test to see if the bridges are configured correctly and one
      hase internet access on teh specified hosts.

  bridge list NAMES
      Lists information about the bridges (may not be needed)

  bridge check NAMES [--config] [--connection]
      provides information about the network configuration
      and netwokrk access. Thisis not a comprehensive speedtest
      for which we use test.

  bridge info
      prints relevant information about the configured bridge


Design Changes:
  We still may need the master to be part of other commands in case
  for example the check is different for master and worker


```
<!--MANUAL-BRIDGE-->






## STUFF TO BE DELETED OR INTEGRATED IN REST OF DOCUMENT


In this example we will set up a network of Raspberry Pi's. In our
example we will set up a cluster with 3 Pi's. We have the following
assumptions:

* We assume you have at at least 3 Raspberry Pi's. This will provide
  you in our example with a master and two worker Pi's. However if you
  have more, you can use more by adding more worker Pi's. Please adapt
  our example accordingly. The minimum number of workers is 1.

* We assume you will use the hostname for the master to be `red`, and
  for the workers you will use `red[001-002]`.

* We assume that you have one more SD Card than you have PI's. If not
  you need to reinstall the burn program on that master. and use that
  reburned SD card.

* We assume that you have an SD card writer. We wecommend that you get
  one that is USB 3 compatible as the new PI's do support USB 3 and
  thus are faster.

* We assume you have the master configured with the (latest Raspberry
  Pi
  OS)[https://www.raspberrypi.org/documentation/installation/installing-images/README.md]

* We assume you use the username `pi` on `red`. Note, that `pi` is
  the default username on Rasperry Pi OS. To rename the hostname which
  is originally `raspberry` please log into it and execute the
  following command:

  TODO: MAYBE WE SHOULD JUST LEAVE THE NAME raspberry and just burn a
  new SD card

  ```
  pi@raspberry:$ sudo echo "127.0.1.1 red" >> /etc/hosts
  pi@raspberry:$ sudo reboot
  ```

  after the reboot the machien will show up as `red`
  
In the first step we will install some useful software on the master
that allows us to easily burn and reburn also the card for master. 
On `red`, perform the following to create an ssh-key, download
cloudmesh for Pi, and download the latest raspbian OS with `cms burn`

```
pi@red:$ ssh-keygen
pi@red:$ curl -Ls http://cloudmesh.github.io/get/pi | sh
pi@red:$ source ~/ENV3/bin/activate

(ENV3) pi@red:$ ssh-add
(ENV3) pi@red:$ cms burn image get latest
(ENV3) pi@red:$ cms burn image ls
```

To prepare for burning check if your SD card writer is detected and
observe the output (note it is a prompted command). We have multiple
programs to do so likely the `info` command will be sufficient.

```
(ENV3) pi@red:$ cms burn detect
(ENV3) pi@red:$ cms burn info

...

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
| Path     | Info                 | Readable | Formatted | Empty | Size             | Aaccess | Removable | Writeable |
+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
| /dev/sdx | Generic Mass-Storage | True     | True      | False | 31.9 GB/29.7 GiB | True    | True      | True      |
+----------+----------------------+----------+-----------+-------+------------------+---------+-----------+-----------+
```

Now set your default SD card device with the following command (your
`/dev/sdx` may be different as reported by the `info` command

```
(ENV3) pi@red:$ export DEV=/dev/sdx
```

and start burning `red[001-002]`.

```
(ENV3) pi@red:$ cms burn create \
--hostname=red[001-002]
```

After you put the SD Cards in the worker Pis and boot them you can log
into them with

```
(ENV3) pi@red:$ ssh pi@red001.local
```

In the future, we will try to remove the `pi` user. 

E.g. use we will integrate `cms host ssh config red[001-003]`


Note that if the Pi's are all connected under (cms
bridge)[https://github.com/cloudmesh/cloudmesh-pi-cluster/tree/main/cloudmesh/bridge],
the `.local` extension is not necessary.


>
> ***Alternative: Specifying --device***
>
> If you would rather not use `export DEV=/dev/sdx`, you can specify
> it using the `--device` option:
>
> ```
> (ENV3) pi@red:$ cms burn create \
> --device=/dev/sdx \
> --hostname=red[001-002] \
> --ipaddr=169.254.10.[1-2]
> ```
>

>
> ***Alternative: Using WiFi:***
>
> If you want to connect your workers directly to the internet via
> WiFi, then you only need to add the following two lines to the end
> of `cms burn`:
>
> ```
> (ENV3) pi@red:$ cms burn create \
> --hostname=red[001-002] \
> --ipaddr=192.168.1.10 \
> --ssid=MyWifiRouterName \
> --wifipassword=MyWifiPassword
> ```
>

>
> ***Alternative: Burning with Multiple SD Card Writers:***
>
> To use multiple card writers you can use
>
> ```
> (ENV3) pi@red:$ cms burn create \
> --device=/dev/sd[a,e] \
> --hostname=red[001-002] \
> --ipaddr=169.254.10.[1-2]
> ```
>



THAT GREGOR DID NOT WANT TO DELETE  AS IT COULD BE USEFUL
AND MAYBE COULD BE INTEGRATED IN THE MAIN DOCUMENTATION

**NOTE**: Notice I have changed the `--ipaddr` option. This is to
remind everyone that the static IP must fall into your network
range. Many home networks have a 192.168.1.x network range, which is
why I have set up the example in this context.

## Step 4(alt). Burning Multiple Cards

The process for burning multiple cards is very straightforward and
analogous to burning a single card. In this example, we assume we want
hostnames `red001, red002, red003` with ip addresses `169.254.10.1,
169.254.10.2, 169.254.10.3' burned on cards located at `/dev/sda,
/dev/sde, /dev/sdf` respectively. Our command is as follows:

```
(ENV3) pi@red:$ cms burn create \
--image=latest \
--device=/dev/sd[a,e,f] \
--hostname=red[001-003] \
--sshkey=default \
--ipaddr=169.254.10.[1-3]
```

This has not yet been tested due to lack of card-readers.

## DEPRECATED. DO NOT GO BEYOND THIS LINE AS THE DOCUMENTATION IS OUT OF DATE


### Installation

First, you must install `cms burn`. In a future version, this will be done
with

```bash
$ pip install cloudmesh-pi-burn
```
   
However, in the meanwhile, you do it as follows:

```bash
$ mkdir cm
$ cd cm $ git clone https://github.com/cloudmesh/cloudmesh-pi-burn.git
$ cd cloudmesh-pi-burn
$ pip install -e .
```    

In the future, we will remove the -e

```bash
$ pip install .
```

### Information about the SD Cards and Card Writer

You need at least one SD Card writer. However, `cms burn` is
supposed to work also with a USB hub in which you can plug in
multiple SD Cards and burn one card at a time. Once done, you can add a
new batch, and you can continue writing. This is done for all specified
hosts so that you can minimize the interaction with the SD cards.

To find out more about the Card writers and the SD Cards, you can use
the command

```bash
$ cms burn detect
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
$ cms burn info
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


### Finding Image Versions

Start using sudo now!

First, you have to find the raspbian image you like to install. For this
purpose, we have developed a command that lists you the available images
in the Raspberry Pi repository. To see the versions, please use the
command

```bash
# cms burn image versions
```

Once in a while, they come out with new versions. You can refresh the
list with

```bash
# cms burn image versions --refresh
```

### Downloading an Image

To download the newest image, use the command

```bash
# cms burn image get latest
```

The image is downloaded into the folder

* `~/.cloudmesh/cmburn/images`

To list the downloaded images, you can use the command

```bash
# cms burn image ls
```

In case you like to use the latest download, you can use the
command.

TODO: MISSING

You can also specify the exact URL with

```bash
# cms burn image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2019-09-30/2019-09-26-raspbian-buster-lite.zip
```

### ROOT

For the burn process, you need to use root privileges. To achieve this,
you need to execute the following commands. The source command
activates the python virtual env that you have created where you
installed the `cms burn` command

```bash
$ sudo su
# source /home/pi/ENV3/bin/activate
```

Please note that for our notation a `#` indicates this command is
executed in root.

### Creating Cluster SD-Cards

Next, we describe how we create a number of SD-Cards to create a cluster.
Each card will have a unique hostname, an IP address and your public key. 
To locate your device, you can use:

```bash
$ cms burn info  
```

You can look at the names of your devices under the device column. Eg
/dev/sda,/dev/sdb,etc

### Burning SD-Cards

To burn one card, we will use `cms burn create` with several
important options:

* `--image` specifies the name of the image to burn
* `--device` is the path to the SD card. If this option is omitted,
  then `cms burn` will use the devices listed under `cms burn info`
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
the network as cms burn will pull information from the network to
configure static IP usage.

For more information on options, see `/cmburn/pi/cmpiburn.py`

Here is an example call of the command `create` using a static IP
address connecting to a home wifi network

TODO: WIFI is not listed here

```bash
# cms burn create \
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
omit the `--device` option, then `cms burn` will refer to the devices
listed using `cms burn info`

If your Pis are going to use ethernet connection, then the command is as
simple as:

```bash
# cms burn create \
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
# cms burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --device=/dev/sd[a-f]
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.[32-37] \
    --format
```

Note the ranges are inclusive. Alternatively, we can omit the --device
option and allow cms burn to detect the devices from `cms burn
info`:

```bash
# cms burn create \
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
# cms burn create \
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

If the only device listed under `cms burn info` is `/dev/sda`, then the
above command is equivalent to:

```bash
# cms burn create \
    --image=2020-02-05-raspbian-buster-lite \
    --hostname=red[2-7] \
    --sshkey=/home/pi/.ssh/id_rsa.pub \
    --blocksize=4M \
    --ipaddr=169.254.10.[32-37] \
    --format
```


### From the raspberry FAQ

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

    see:
    
    cms pi led red off HOSTNAME

SSHFS:
   add master to `.ssh/config` onlocal machine

    ```
   Host master
         HostName xxx.xxx.xxx.xxx
         User pi
         IdentityFile ~/.ssh/id_rsa.pub

   mkdir master
   sshfs master: master -o auto_cache
    ```

    See also: <https://github.com/libfuse/sshfs>

