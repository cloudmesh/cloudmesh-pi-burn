# Cloudmesh Pi Burner for SD Cards

**WARNING:** *This program is designed for a **Raspberry Pi**. Instructions 
to use **Linux** are included in the FAQ. We are working on support for **macOS 
and Windows 10**. If you want to help us port to any of these OSes, please 
contact laszewski@gmail.com*

[![image](https://travis-ci.com/cloudmesh/cloudmesh-pi-burn.svg?branch=main)](https://travis-ci.com/github/cloudmesh/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/pyversions/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/v/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


<!--TOC-->

- [Cloudmesh Pi Burner for SD Cards](#cloudmesh-pi-burner-for-sd-cards)
  - [Introduction](#introduction)
  - [Nomenclature](#nomenclature)
  - [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi)
    - [Requirements](#requirements)
    - [Manager Pi](#manager-pi)
    - [Burning Multiple SD Cards with a Single Burner](#burning-multiple-sd-cards-with-a-single-burner)
    - [Connecting Pis to the Internet via Bridge](#connecting-pis-to-the-internet-via-bridge)
  - [Quickstart for Bridged Wifi with Inventory](#quickstart-for-bridged-wifi-with-inventory)
    - [Initial Manager Setup](#initial-manager-setup)
    - [Creating our inventory](#creating-our-inventory)
    - [Burning SD Cards using Inventory](#burning-sd-cards-using-inventory)
    - [Booting Up Workers and Verifying Connection](#booting-up-workers-and-verifying-connection)
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
    - [What packages do I need to run the info command on macOS](#what-packages-do-i-need-to-run-the-info-command-on-macos)
    - [Are there any unit tests?](#are-there-any-unit-tests)
    - [Using Pi Imager to setup a Manager Pi with headless access](#using-pi-imager-to-setup-a-manager-pi-with-headless-access)
    - [Single Card Burning](#single-card-burning)
    - [How to update firmware?](#how-to-update-firmware)
    - [How to burn a cluster using Linux](#how-to-burn-a-cluster-using-linux)
  - [Alternatives](#alternatives)
    - [What is the status of the implementation?](#what-is-the-status-of-the-implementation)
  - [How can I contribute Contributing](#how-can-i-contribute-contributing)

<!--TOC-->

## Introduction

`cms burn` is a program to burn many SD cards for the preparation of
building clusters with Raspberry Pi's. It allows users to create
readily bootable SD cards that have the network configured and contain a
public ssh key from your machine that you then use to login into the
PIs after boot. Thus, little setup is needed for a cluster after boot. Another
unique feature is that you can burn multiple cards in a row, each with
their individual setup such as hostnames and ipadresses.


## Nomenclature

* Commands proceeded with `pi@managerpi:$` are to be executed on the
  Raspberry Pi with the name `managerpi`.

* Commands with `(ENV3) pi@managerpi:$` are to be executed in a virtual ENV
  using Python 3 on the Raspberry Pi with the name managerpi
  
## Quickstart for Bridged WiFi

To provide you with a glimpse of what you can do with cms burn, we
have provided this quickstart guide that will create one manager PI and
several workers.

This setup is intended for those who have restricted access to their
network (ie. cannot access router controls).  For example, those
on campus WiFis or regulated apartment WiFis.

The Figure 1 describes our network configuration. We have 5
Raspberry Pi 4s: 1 manager and 4 workers. We have WiFi access, but we
do not necessarily have wired access or access to the router's controls.

We also have a network switch, where the manager and workers can
communicate locally, but we will configure the manager to provide
internet access to devices on the network switch via a "network
bridge".

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Pi Cluster setup with bridge network

### Requirements

For the quickstart we have the following hardware requirements:

* SD Cards and Raspberry Pis

* You will need an SD card writer (USB-A) to burn new cards We
  recommend that you invest in a USB 3.0 SDCard writer as they are
  significantly faster and you can reuse them on PI'4s. Make sure to
  get an adapter if your normal computer only supports USB-C
  
* You will need a Raspberry Pi cluster. Detailed information about
  parts are provided at our
  [Web page](https://cloudmesh.github.io/pi/docs/hardware/parts/).

### Manager Pi

First we need to configure the Manager Pi

**Step 0.** Burn Manager Pi SD Card

Using [Raspberry Pi imager](https://www.raspberrypi.org/software/),
  burn an SD card with *Raspberry Pi OS (32-bit) with desktop and
  recommended applications*. You may use your normal system to burn
  such a card including Windows, macOS, or Linux.

You will then want a method of accessing this manager Pi. You may
either use SSH (recommended) from the command line or a monitor to use the desktop environment (easiest)
to access it. We highly recommend
[changing the password](https://www.raspberrypi.org/documentation/linux/usage/users.md)
on the Pi as soon as you have access. This is because the pi is
initialized with default user `pi` and default password
`raspberry`. This is critical if you are on a shared network where
anyone can attempt to access your pi.

> Monitor Desktop Environment: You will need a monitor, keyboard, and
> mouse. This is the easiest approach as Raspberry Pi OS provides a
> very nice user interface with an easy-to-follow setup process for
> connecting to WiFi and other such tasks.

> SSH Environment: You may consider enabling SSH access to your Pi so
> that you may access the file system from your preferred machine.

> Headless Configuration: See section 3 of
> [enabling ssh](https://www.raspberrypi.org/documentation/remote-access/ssh/)
> for instructions on how to enable SSH headlessly. Similarly,
> [how to enable WiFi headlessly](https://raspberrypi.stackexchange.com/questions/10251/prepare-sd-card-for-wifi-on-headless-pi).
> Additionally you can check out the FAQ for step-by-step
> instructions.
> [Using Pi Imager to setup a Manager Pi with headless access](#using-pi-imager-to-setup-a-manager-pi-with-headless-access).

> Update the firmware: See the FAQ [How to update firmware?]>
> (#how-to-update-firmware)

**Step 1.** Installing Cloudmesh on the Manager Pi

Open a new terminal screen on the Manager Pi. Here we assume the
hostname is `managerpi`. However, this is of no importance in relation
to the topics of this guide.

Update pip. The simple curl command below will generate an ssh-key,
update your system, and install cloudmesh.

```
pi@managerpi:~ $ pip install pip -U
pi@managerpi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -                
```

This will take a moment...

**Step 2.** Reboot

The installation script updates your system. Reboot for effect.

```
pi@managerpi:~ $ sudo reboot
```

**Step 3.** Download the latest Raspberry Pi Lite OS

The following command will download the latest images for Raspberry
Lite OS.

```
(ENV3) pi@managerpi:~ $ cms burn image get latest-lite
```

We can verify our image's downloaded with the following.

```
(ENV3) pi@managerpi:~ $ cms burn image ls
```

> **Note.** For our cluster we use light, but if you like 
> to use other versions please see this note.
> We can use the following command to list the current
> Raspberry Pi OS versions (full and lite)
>
> ```
> (ENV3) pi@managerpi:~ $ cms burn image versions --refresh
> ```
>
> This will list the Tags and Types of each available OS. We can then
> modify the `image get` command for versions we are interested in. For
> example,
>
> ```
> (ENV3) pi@managerpi:~ $ cms burn image get full-2020-05-28
> ```


**Step 4**. Setup SD Card Writer

Plug your SD Card Writer into the Pi. Ensure you have an SD Card
inserted into your writer. Run the following command to find the path
to your SD Card.

```
(ENV3) pi@managerpi:~ $ cms burn info
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

> `cms burn info` has other useful information, but for the purposes
> of this guide we omit it.

We can see from the information displayed that our SD card's path is
`/dev/sda`. Of course, this may vary. 

### Burning Multiple SD Cards with a Single Burner

**Step 0.** Ensure the first SD card is inserted into the burner.

We can run `cms burn info` again as we did above to verify our SD 
Card is connected.

**Step 1.** Burning the Cards

`cms burn` supports parameterized hostnames that allow automatic incrementation of numbers.

For example, `red00[1-2]` is interpreted by cms burn as `[red001, red002]`.
Similarly, `red[a-c]` is interpreted by cms burn as `[reda, redb, redc]`.

We can burn 2 SD cards as follows:

**!! WARNING VERIFY THE DEVICE IS CORRECT. REFER TO CMS BURN !!**

```
(ENV3) pi@managerpi:~ $ cms burn create --hostname=red00[1-4] --ip=10.1.1.[2-5] --device=/dev/sda --tag=latest-lite
```

The user will be prompted to swap the SD cards after each card burn if 
there are still remaining cards to burn.

**Step 2.** Boot the cluster

After all cards are burned. Turn off the cluster, insert the cards, and turn 
the cluster back on.

We can now proceed to the next section where we configure our bridge.

### Connecting Pis to the Internet via Bridge 

Figure 1 depicts how the network is set up with the help of the bridge
command.

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Networking Bridge

**Step 0.** Review and Setup

At this point, we assume that you have used `cms burn` to create all SD
cards for the Pi's with static IP addresses in the subnet range
`10.1.1.0/24` (excluding `10.1.1.1`. See step 1 for details)

We are also continuing to use `managerpi` (which is where we burn the
worker SD cards).

We will now use `cms bridge` to connect the worker Pis to the
internet. Let us again reference the diagram of our network setup. You
should now begin connecting your Pis via the network switch
(unmanaged or managed) if you have not done so already. Ensure that
`managerpi` is also connected to the network switch.

We assign the eth0 interface of the `managerpi` to be 10.1.1.1, and it 
acts as the default gateway for the workers. The workers' IPs were set 
during the create command.

**Step 1.** Configuring our Bridge

We can easily create our bridge as follows. 

```
(ENV3) pi@managerpi:~ $ cms bridge create --interface='wlan0'
```

We should now reboot.

```
(ENV3) pi@managerpi:~ $ sudo reboot
```

> Note the `--interface` option indicates the interface used by the
> manager pi to access the internet.  In this case, since we are using
> WiFi, it is likely `wlan0`. Other options such as `eth0` and `eth1`
> exist for ethernet connections.

**Step 2.** Verifying internet connection 

We should now be able to see our workers. 

```
arp -a
```

Note it may take a few minutes for them to populate in the neighbor table. If 
you want to speed this up try to ping them individually.

```
ping red002
```

At this point, our workers should have internet access. Let us SSH
into one and ping google.com to verify. Ensure you have booted your
workers and connected them to the same network switch as the manager.

```
(ENV3) pi@managerpi:~ $ ssh red002

pi@red002:~ $ ping google.com
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

Note how we are able to omit the pi user and .local extension. We have
successfully configured our bridge. Our pis are now ready to cluster.

## Quickstart for Bridged Wifi with Inventory

In this guide, we will show how you can configure a Cloudmesh Inventory to easily burn a cluster of SD cards as well as configure the current Pi as the manager if desired. 

We will follow the same network setup as the Bridged Wifi above:

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

The requirements for this guide are the same as the [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi).

### Initial Manager Setup

First, we need to setup our manager with cloudmesh. Follow Steps 0-4 of the [Manager-pi setup](#manager-pi) in the Bridged Wifi Guide. For this guide, we will rename our Pi hostname to `managerpi`. 

### Creating our inventory

For this guide, we will create two workers for `managerpi`. We can do this as follows:

```
(ENV3) pi@managerpi:~ $ cms inventory create --manager=managerpi --workers=red00[2-3] --ip=10.1.1.1,10.1.1.[2-3]  --inventory="cluster.yaml" --keyfile=~/.ssh/id_rsa.pub latest-lite
```

We can then use the following to list the entries of our inventory.

```
(ENV3) pi@managerpi:~ $ cms inventory list --inventory=cluster.yaml
inventory list --inventory=cluster.yaml
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| host      | name      | type | tag         | cluster | label | service | services | ip       | dns | project | owners | comment | description | keyfile           | status   |
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| managerpi | managerpi |      | latest-lite | cluster |       | manager |          | 10.1.1.1 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red002 | red002 |      | latest-lite | cluster |       | worker  |          | 10.1.1.2 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red003 | red003 |      | latest-lite | cluster |       | worker  |          | 10.1.1.3 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
```

### Burning SD Cards using Inventory

First, verify that you have plugged in your SD card writer with an SD card into the `managerpi`. For this guide, we will simply use one SD card burner to burn both SD cards.

Verify your SD card is detected with the following:

```
(ENV3) pi@managerpi:~ $ cms burn info
# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+
| Path     | Info                   | Formatted   | Size             | Plugged-in   | Readable   | Empty   | Access   | Removable   | Writeable   |
|----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------|
| /dev/sdb | Generic STORAGE DEVICE | True        | 64.1 GB/59.7 GiB | True         | True       | False   | True     | True        | True        |
+----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+
```
> Some information has been ommitted from cms burn info for simplicity

Note your device. In our case, it is `/dev/sdb`. Of course, on your machine it may vary. 

We can now burn our cards as follows:

```
(ENV3) pi@managerpi:~ $ cms burn create --inventory=cluster.yaml --name=managerpi,red00[2-3] --device=/dev/sdb

Manager hostname is the same as this system's hostname. Is this intended? (Y/n) Y
Do you wish to configure this system as a WiFi bridge? A restart is required after this command terminates (Y/n) Y

# Cut out output of burn command for simplicity

INFO: Burned card 1

INFO: Please remove the card

Slot /dev/sdb needs to be reused. Do you wish to continue? [y/n] y
Insert next card and press enter...

# Cut out output of burn command for simplicity

INFO: Burned card 2

INFO: Please remove the card

INFO: You burned 2 SD Cards
Done :)
```

Note that in this example, the hostname of the manager passed into `cms burn create` is the same as the current system's hostname. This is intentnional (as indicated by our `Y` choice) and we are also configuring the `managerpi` as a bridge (as indicated by our `)

We must now reboot the manager.

```
(ENV3) pi@managerpi:~ $ sudo reboot
```

### Booting Up Workers and Verifying Connection

Insert the burned worker cards into 

Refer to Step 2 in [Connecting Pis to the Internet via Bridge](#connecting-pis-to-the-internet-via-bridge) for instructions

## Set up of the SSH keys and SSH tunnel

One important aspect of a cluster is to setup authentication via ssh
in a convenient way, so we can easily login from the laptop to each of
the PI workers and the PI manager. Furthermore, we like to be able to
login from the PI manager to each of the workers. In addition, we like
to be able to login between the workers.

We have chosen a very simple setup while relying on ssh tunnel.

To simplify the setup of this we have developed a command `cms host`
that gathers and scatters keys onto all machines, as well as sets up
the tunnels.

It is essential that the key on the laptop must not be password
less. This is also valid for any machine that is directly added to the
network such as in the mesh network.

To avoid password less keys we recommend you to use `ssh-add` 
or `ssh-keychain` which will ask you for one.

The manual page for `cms host` is provided in the Manual Pages
section.

**Step 1.** On the manager create ssh keys for each of the workers.

```
(ENV3) pi@managerpi:~ $ cms host key create red00[1-3]
```

**Step 2.** On the manager gather the worker, manager, and your laptop
public ssh keys into a file.

```
(ENV3) pi@managerpi:~ $ cms host key gather red00[1-3],you@yourlaptop.local keys.txt
```

**Step 3.** On the manager scatter the public keys to all the workers
and manager ~/.ssh/authorized_hosts file

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
pi@red001:~ $ ssh managerpi.local
```

TODO: BUG: The workers still currently still need to use .local after names. This 
will be resolved by the inventory create update.

```
(ENV3) pi@managerpi:~ $ exit
pi@red001:~ $ ssh red002.local
pi@red002:~ $ exit
pi@red001:~ $ exit
```

**Step 6.** (For Bridge setup) Create SSH tunnels on the manager 
to enable ssh access from your laptop to the workers

For now, we manually install autossh, to test the new cms host tunnel
program. Later we add it to the main manager setup script.

```
(ENV3) pi@managerpi:~ $ yes y | sudo apt install autossh
(ENV3) pi@managerpi:~ $ cms host tunnel create red00[1-3]
```

**Step 7.** (For Bridge setup) Copy the specified command output to 
your `~/.ssh/config` file on your laptop

```
host tunnel create red00[1-3]

Using wlan0 IP = 192.168.1.17
Using cluster hostname = managerpi

Tunnels created.

Please place the following in your remote machine's (i.e. laptop)
`~/.ssh/config` file to alias simple ssh access (i.e. `ssh red001`).

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

> Note: We will in the future provide an addition to the command so you 
> can remove and add
> them directly from the command line
> 
> ```
> cms host tunnel config create red00[1-3]
> cms host tunnel config delete red00[1-3]
> ```

**Step 8.** (For Bridge setup) Verify SSH reachability from the laptop
  to workers

```
you@yourlaptop:~ $ ssh red001
```

## Manual Pages

### Manual Page for the `burn` command

Note to execute the command on the command line you have to type in
`cms burn` and not just `burn`.

<!--MANUAL-BURN-->
```
  burn firmware check
  burn firmware update
  burn install
  burn load --device=DEVICE
  burn format --device=DEVICE
  burn imager [TAG...]
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
              [--inventory=INVENTORY]
              [--name=NAME]
  burn sdcard [TAG...] [--device=DEVICE] [--dryrun]
  burn set [--hostname=HOSTNAME]
           [--ip=IP]
           [--key=KEY]
  burn enable ssh
  burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]
  burn check [--device=DEVICE]
  burn mac --hostname=HOSTNAME

Options:
  -h --help              Show this screen.
  --version              Show version.
  --image=IMAGE          The image filename,
                         e.g. 2019-09-26-raspbian-buster.img
  --device=DEVICE        The device, e.g. /dev/sdX
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
    cms burn create --inventory=INVENTORY --device=DEVICE --name=NAME

        Will refer to a specified cloudmesh inventory file (see cms help inventory).
        Will search the configurations for NAME inside of INVENTORY and will burn
        to DEVICE. Supports parameter expansion.

    cms burn create --passwd=PASSWD

         if the passwd flag is added the default password is
         queried from the commandline and added to all SDCards

         if the flag is omitted login via the password is
         disabled and only login via the sshkey is allowed

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

    cms burn firmware update

        checks and updates the firmware on the Pi

    cms burn install

        installs a program to shrink img files. THis is
        useful, after you created a backup to make the
        backup smaller and allow faster burning in case of
        recovery

    cms burn load --device=DEVICE

        loads the sdcard into the USB drive. Thi sis similar to
        loading a cdrom drive. It s the opposite to eject

    cms burn format --device=DEVICE

        formats the SDCard in the specified device. Be
        careful it is the correct device.  cms burn info
        will help you to identifying it

    cms burn mount [--device=DEVICE] [--os=OS]

        mounts the file systems available on the SDCard

    cms burn unmount [--device=DEVICE] [--os=OS]

        unmounts the mounted file systems from the SDCard

    cms burn info [--device=DEVICE]

        provides useful information about the SDCard

    cms burn image versions [--refresh] [--yaml]

        The images that you like to burn onto your SDCard
        can be cached locally with the image command.  The
        available images for the PI can be found when
        using the --refresh option. If you do not specify
        it it reads a copy of the image list from our
        cache

    cms burn image ls

        Lists all downloaded images in our cache. You can
        download them with the cms burn image get command

    cms burn image delete [--image=IMAGE]

        deletes the specified image. The name can be found
        with the image ls command

    cms burn image get [--url=URL] [TAG...]

        downloads a specific image or the latest
        image. The tag are a number of words separated by
        a space that must occur in the tag that you find
        in the versions command

    cms burn backup [--device=DEVICE] [--to=DESTINATION]

        backs up a SDCard to the given location

    cms burn copy [--device=DEVICE] [--from=DESTINATION]

        copies the file form the destination on the SDCard
        this is the same as the SDCard command. we will in
        future remove one

    cms burn shrink [--image=IMAGE]

        shrinks the size of a backup or image file that
        is on your local file system. It can only be used
        for .img files

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

        This command  not only can format the SDCard, but
        also initializes it with specific values

    cms burn sdcard [TAG...] [--device=DEVICE] [--dryrun]

        this burns the sd card, see also copy and create

    cms burn set [--hostname=HOSTNAME]
                 [--ip=IP]
                 [--key=KEY]
                 [--mount=MOUNTPOINT]

        this sets specific values on the sdcard after it
        has ben created with the create, copy or sdcard
        command

        a --ssh is missing from this command

    cms burn enable ssh [--mount=MOUNTPOINT]

        this enables the ssh server once it is booted

    cms burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]

        this sets the wifi ssid and password after the card
        is created, copied, or the sdcard is used.

        The option country option expects an ISO 3166-1
        two digit country code. The default is "US" and
        the option not required if suitable. See
        https://en.wikipedia.org/wiki/ISO_3166-1 for other
        countries.

    cms burn check [--device=DEVICE]

        this command lists the parameters that were set
        with the set or create command

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
`cms bridge` and not just `bridge`.

<!--MANUAL-BRIDGE-->
```

Options:
    --interface=INTERFACE  The interface name [default: eth1]
                           You can also specify wlan0 if you want
                           to bridge through WIFI on the manager
                           eth0 requires a USB to WIFI adapter

   --ip=IP  The ip address to assign on the eth0 interface,
            ie. the listening interface [default: 10.1.1.1]

  --dns=NAMESERVER  The ip address of a nameserver to set statically
           For example, --dns=8.8.8.8,8.8.4.4 will use google
           nameservers

Description:

  Command used to set up a bride so that all nodes route the traffic
  trough the manager PI.

  bridge create [--interface=INTERFACE] [--ip=IP] [--dns=NAMESERVER]
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
    host tunnel create NAMES [--port=PORT]
    host mac NAMES [--eth] [--wlan] [--output=FORMAT]

This command does some useful things.

Arguments:
    FILE   a file name

Options:
    --dryrun   shows what would be done but does not execute
    --output=FORMAT  the format of the output
    --port=PORT starting local port for tunnel assignment

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

    host tunnel create NAMES [--port=PORT]

      This command is used to create a persistent local port
      forward on the host to permit ssh tunnelling from the wlan to
      the physical network (eth). This registers an autossh service in
      systemd with the defualt port starting at 8001.

      Example:
          cms host tunnel create red00[1-3]

    host mac NAMES

      returns the list of mac addresses of the named pis.

```
<!--MANUAL-HOST-->




### Manual Page for the `pi` command

Note to execute the command on the command line you have to type in
`cms pi` and not just `pi`.

There is some very usefull aditional information about how to use the
LED and temperature monitoring programs at

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

  This command switches on and off the LEDs of the specified
  PIs. If the hostname is omitted. It is assumed that the
  code is executed on a PI and its LED is set. To list the
  PIs LED status you can use the list command

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

          goes in sequential order and switches on and off
          the led of the given PIs


```
<!--MANUAL-PI-->





## FAQ and Hints

Here, we provide some useful FAQs and hints.

### Can I use the LEDs on the PI Motherboard?

Typically this LED is used to communicate some system-related
information. However `cms pi` can control it to switch status on
and off. This is helpful if you like to showcase a particular state
in the PI. Please look at the manual page. An example is
 
```bash
$ cms pi led red off HOSTNAME
```

that when executed on the PI (on which you also must have cms
installed you switch the red LED off. For more options see the
manual page


### How can I use pycharm, to edit files or access files in general from my Laptop on the PI?

This is easily possible with the help of SSHFS. To install it we
refer you to See also: <https://github.com/libfuse/sshfs> SSHFS: add
the manager to `.ssh/config` on the local machine

Let us assume you like to edit files on a PI that you named `red`

Please create a `./.ssh/config file that contains the following:

```
 Host red
      HostName xxx.xxx.xxx.xxx
      User pi
      IdentityFile ~/.ssh/id_rsa.pub
```

Now let us create a directory in which we mount the remote PI directories

```
mkdir manager
sshfs manager: manager -o auto_cache
```

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
simple as we can attach the unmanaged router directly to a Mesh
node via a network cable. In that case, the node is directly connected
to the internet and uses the DHCP feature from the Mesh router (see
Figure 2).

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-mesh.png)

Figure 2: Networking with Mesh network

You will not need the bridge command to setup the network.

### Can I use cms burn on Linux?

Not everything is supported.

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
will likely never be sda.

To test it use

```
sudo apt-get install pv
cms burn info
cms burn sdcard --dev=/dev/sdX
cms burn mount --device=/dev/sdX
cms burn enable ssh
cms burn unmount
```

Take the SDCard into the PI and set it up there as documented.

For the full features, please use `cms burn create` instead of
`cms burn sdcard`


### What packages do I need to run the info command on macOS

```
brew install libusb
brew install pv
```

**Access to ext4**: For the more advanced features of `burn` you will
need full write access to the ext4 partition on your SDCard that is
created when you burn it. Unfortunately, the tools that used to be
freely available seem no longer to work properly, so you could use
[extFS for Mac by Paragon Software](https://www.paragon-software.com/us/home/extfs-mac/)
which does cost $40 for a license.

For this reason, we recommend that you first set up the manager PI and
do all burning on the manager PI.

### Are there any unit tests?

As `cms burn` may delete and format files and disks/SD Cards during unit
testing users are supposed to first review the tests before running
them. Please look at the source and see if you can run a test.

We have the following tests:

* `pytest -v --capture=no tests/test_01_image.py`

  * This test removes files from ~/.cloudmesh/cmburn/images
  * See also:
  [test_01_image.py](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/tests/test_01_image.py)

* TODO: add the other tests

### Using Pi Imager to setup a Manager Pi with headless access

This FAQ will provide step-by-step instructions for burning and accessing a 
headless manager pi. We include instructions for either wifi access to 
the pi or local ethernet connection.

If you have restricted WIFI that requires you to register you 
devices MAC address via a web browser (such as a campus or
hotel wifi access page), you might not be able to continue
with a headless setup. In this case, we recommend that you use your
Laptop as a "hotspot" and connect the PI to it.

This FAQ references instructions from
<https://www.raspberrypi.org/documentation/remote-access/ssh/> and
<https://www.raspberrypi.org/documentation/configuration/wireless/headless.md>

**Step 1.**

Download and install the Pi Imager software from raspberrypi.org <https://www.
raspberrypi.org/software/>.

**Step 2.**

Launch the Pi Imager software, insert a SD card reader and SD card into 
your laptop.

**Step 3.**

Choose the OS in the Pi Imager interface. We will use **Raspberry Pi OS 
(32-BIT) with the Raspberry Pi desktop.

**Step 4.**

Choose the SD card in the Pi Imager interface. If you do not see an SD card 
and a reader is plugged into your laptop, remove and re-insert the sd card 
reader.

**Step 5.**

Push the 'Write' button and confirm the settings to burn the OS to your SD card.
You may need to put in the SUDO password to burn the card. This will take 
some time. USB 3.0 devices are faster than USB 2.0. Make sure your cable is 
USB 3.0 as well. 

**Step 6.**

Mount the SD card. This can be accomplished easily in Linux by unplugging 
and replugging in the device. On Pi and Linux you should see the boot 
partition at **/media/$USER/boot** (where user is you username) and on 
MacOS at **/Volumes/boot**. I will use Linux for the example. Substitute as 
required for MacOS.

**Step 7.**

Enable SSH access to the SD card. At the command prompt

```
you@yourlaptop:~ $ cd /media/$USER/boot
you@yourlaptop:~ $ touch /media/$USER/boot/ssh
```

This creates an empty file named ssh in the boot partition. On the first boot, 
this enables the SSH service, and then an empty ssh file will be 
automatically deleted.

**Step 8.**

If you only have wireless access to your Pi. You need to setup the wireless 
configuration. 

If you have restricted WIFI that requires you to register you 
devices MAC address via a web browser (think hotel wifi access page), you 
might not be able to continue with a headless setup.

Otherwise, you can continue without this step if you have ethernet
access between your laptop and pi (either via switch or direct
cable). After plugging into a shared switch with the Pi, or directly
to it, you will need to make sure you see a link local address on your
ethernet port on your laptop. It should look something
like 169.254.X.X. If you do not see this investigate how to setup a
link local ip on your OS.

```
you@yourlaptop:/media/$USER/boot $ nano /media/$USER/boot/wpa_supplicant.conf

#Insert this into the file and save (CTRL-X, Y, Enter).

ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=<Insert 2 letter ISO 3166-1 country code here e.g. US>

network={
 ssid="<Name of your wireless LAN>"
 psk="<Password for your wireless LAN>"
}
```

**Step 9.**

Unmount and eject the SD card. 

```
you@yourlaptop:~ $ sudo umount /media/$USER/boot
you@yourlaptop:~ $ sudo umount /media/$USER/rootfs
```

**Step 10.**

Boot a pi with the SD card. Wait a few minutes and try to access it via SSH. 
Use the Raspi OS default username "pi" and "raspberry".

```
you@yourlaptop:~ $ ssh pi@raspberrypi.local
```

**Step 11.**

Change the password.

```
pi@raspberrypi:~ $ passwd
```

**Step 12.**

Change the hostname on the pi.

```
pi@raspberrypi:~ $ sudo raspi-config
<1. System Options>
<S4 Hostname>
enter
managerpi
<Finish>
Would you like to reboot?
<Yes>
```

**Step 13.**

Wait a minute or two and reconnect. Now using the new hostname.

```
you@yourlaptop:~ $ ssh pi@managerpi.local
```

**Step 14.**

You are all done. You are ready to proceed with [Quickstart for Bridged 
WiFi](#quickstart-for-bridged-wifi). You will now witness the magic of how 
cms burn automates this process for you. 

```
pi@managerpi:~ $ 
```

### Single Card Burning

Step 0. Ensure the SD card is inserted.

We can run `cms burn info` again as we did above to verify our 
SD card is connected.

Step 1. Burning the SD Card

Choose a hostname for your card. We will use `red001` with ip
`10.1.1.2`. The IP address `10.1.1.1` is reserved for the burner pi
(ie. `managerpi`).

> Note we are using the subnet `10.1.1.0/24` in this guide. We
> currently recommend you do the same, otherwise the WiFi bridge will
> not configure correctly. We will change this in the future to
> support other
> [Private IP Ranges](https://www.arin.net/reference/research/statistics/address_filters/)

**!! WARNING VERIFY THE DEVICE IS CORRECT. REFER TO CMS BURN !!**

```
(ENV3) pi@managerpi:~ $ cms burn create --hostname=red001 --ip=10.1.1.2 --device=/dev/sda --tag=latest-lite
```

Wait for the card to burn. Once the process is complete, it is safe 
to remove the SD card.

We can now proceed to [the bridge setup](#connecting-pis-to-the-internet-via-bridge )

### How to update firmware?

To update the firmware reference the [raspi documentation](#https://www.raspberrypi.org/documentation/hardware/raspberrypi/booteeprom.md) 

Or follow the simple instructions below.

```
pi@managerpi:~ $ sudo apt update
pi@managerpi:~ $ sudo apt full-upgrade
pi@managerpi:~ $ sudo reboot
pi@managerpi:~ $ sudo rpi-eeprom-update -a
pi@managerpi:~ $ sudo reboot
```

### How to burn a cluster using Linux

This will setup the same cluster seen in [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi)
using only a Linux machine. Pi imager and a manual manager pi setup process is 
not required using this method. 

#### Prerequisites

* We recommend Python 3.8.2 Python or newer.
* We recommend pip version 21.0.0 or newer
* You have a private and public ssh key named ~/.ssh/id_rsa and ~/.
  ssh/id_rsa.pub

#### Install Cloudmesh

Create a Python virtual environment `ENV3` in which to install cloudmesh. 
This will keep cloudmesh and its dependencies separate from your default 
environment. 

Always make sure to `source` this environment when working with cloudmesh.

```
you@yourlaptop:~ $ python -m venv ~/ENV3
you@yourlaptop:~ $ source ~/ENV3/bin/activate 
you@yourlaptop:~ $ mkdir cm
you@yourlaptop:~ $ cd cm
you@yourlaptop:~ $ pip install cloudmesh-installer
you@yourlaptop:~ $ cloudmesh-installer get pi 
```

#### Create a Manager Pi

**Step 1.** Get the latest RaspiOS-full image

```
you@yourlaptop:~ $ cms burn image get latest-full
```

**Step 1.** Insert and SD Card to your laptop and identify the sd card device 
name using:

```
you@yourlaptop:~ $ cms burn info
```

**Step 2.** Burn the manager pi.

> **!! WARNING VERIFY THE DEVICE IS CORRECT. REFER TO CMS BURN !!**

```
you@yourlaptop:~ $ cms burn create --hostname=managerpi --tag=latest-full--device=/dev/sdX --ssid=your_wifi --wifipassword=your_password
```
#### Create the workers

**Step 1.** Download the latest RaspiOS-lite image

```
cms burn image get latest-lite
```

**Step 2.** Burn the workers

> **!! WARNING VERIFY THE DEVICE IS CORRECT. REFER TO CMS BURN !!**

```
cms burn create --hostname=red00[1-4] --ip=10.1.1.[2-5] --device=/dev/sdX --tag=latest-lite
```

**Step 3.** Turn off the cluster, insert sd cards, turn on the cluster, and 
connect to the manager pi.

```
you@yourlaptop:~ $ ssh pi@mangerpi.local
```

**Step 4.** Update and install cloudmesh on your manager pi

Update pip. The simple curl command below will generate an ssh-key,
update your system, and install cloudmesh.

```
pi@managerpi:~ $ pip install pip -U
pi@managerpi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -                
pi@managerpi:~ $ sudo reboot
```

**Step 4.** Enable the bridge on the mangerpi.

See section [Connecting Pis to the Internet via Bridge](#connecting-pis-to-the-internet-via-bridge)

**Step 5.** Generate and distribute SSH keys

See section [Set up of the SSH keys and SSH tunnel](#set-up-of-the-ssh-keys-and-ssh-tunnel)

**Step 6.** Enjoy your Pi cluster :)

## Alternatives

There are several alternatives to make the setup easier:

* Using Ansible after you have created the SDCards via PIImager. This however 
  requires still the discovery of the hosts on the network and additional steps.
* PiBakery can burn cards while allowing startup scripts and naming hosts. 
  Although the GUI is nice it is also a limiting factor as each card should have 
  a different hostname
* Using DHCP to get IP addresses automatically. This is a solution we also used but
  do not present here
* PXE or network booting which allows you to boot from the network. For larger PI 
  clusters this requires multiple Servers so that the network is not overwhelmed. 
  Starting the cluster takes much longer.


### What is the status of the implementation?

| Feature         | PI    | Ubuntu | Mac   | Windows |
| --------------- | ----- | ------ | ----- | ------- |
| image versions  |    +  |    +   |    +  |         |
| image ls        |    +  |    +   |    +  |         |
| image delete    |    +  |    +   |    +  |         |
| image get       |    +  |    +   |    +  |         |
| info            |    +  |    +   |    +  |         |
| network         |    +  |    +   |       |         |
| backup          |    +  |    +   |    -  |         |
| copy            |    +  |    +   |    -  |         |
| shrink install  |    +  |    +   |       |         |
| shrink          |    +  |    +   |       |         |
| sdcard          |    +  |    +   |    +  |         |
| mount           |    +  |    +   |    +  |         |
| unmount         |    +  |    +   |    +  |         |
| enable ssh      |    +  |    +   |    +  |         |
| wifi            |    +  |    +   |    +  |         |
| set             |    +  |    +   | TODO1 |         |
| create          |  TODO |  TODO  | TODO  |         |
| check           |    +  |    +   |    +  |         |
| format          |    +  |    +   |    +  |         |
| firmware        |    +  | NA     |  NA   | NA      |

* for macOS, only the image commands have unit tests
* firmware does not have a unit test
  

* empty = not yet implemented
* + = verified throug unit test either by ANthony or Gregor
* - broken

* TODO1 = todo for boot fs, rootfs not supported


## How can I contribute Contributing

The code uses a variety of cloudmesh components. This mainly includes

  * [GitHub cloudmesh-pi-burn](https://github.com/cloudmesh/cloudmesh-pi-burn)
  * [GitHub cloudmesh-pi-cluster](https://github.com/cloudmesh/cloudmesh-pi-cluster)
    
Additional cloudmesh components are used. For example:
  * [GitHub cloudmesh-pi-cluster](https://github.com/cloudmesh/cloudmesh-common)
  * [GitHub cloudmesh-pi-cluster](https://github.com/cloudmesh/cloudmesh-cmd5)
  * [GitHub cloudmesh-pi-cluster](https://github.com/cloudmesh/cloudmesh-inventory)

