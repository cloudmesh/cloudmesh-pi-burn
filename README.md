# Cloudmesh Pi Burner for SD Cards

[![image](https://travis-ci.com/cloudmesh/cloudmesh-pi-burn.svg?branch=main)](https://travis-ci.com/github/cloudmesh/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/pyversions/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn)
[![image](https://img.shields.io/pypi/v/cloudmesh-pi-burn.svg)](https://pypi.org/project/cloudmesh-pi-burn/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


<!--TOC-->

- [Cloudmesh Pi Burner for SD Cards](#cloudmesh-pi-burner-for-sd-cards)
  - [1. Burning Tutorials](#1-introduction)
  - [2. Manual Pages](#6-manual-pages)
    - [6.1 Manual Page for the `burn` command](#61-manual-page-for-the-burn-command)
    - [6.2 Manual Page for the `bridge` command](#62-manual-page-for-the-bridge-command)
    - [6.3 Manual Page for the `host` command](#63-manual-page-for-the-host-command)
    - [6.4 Manual Page for the `pi` command](#64-manual-page-for-the-pi-command)
    - [6.4 Manual Page for the `ssh` command](#64-manual-page-for-the-ssh-command)
  - [3. FAQ and Hints](#7-faq-and-hints)
    - [3.1 Quickstart for a Setup of a cluster from macOS or Linux with no burning on a PI.](#71-quickstart-for-a-setup-of-a-cluster-from-macos-or-linux-with-no-burning-on-a-pi)
    - [3.2 Quickstart for Using a Pi to Burn a Cluster Using Inventory](#72-quickstart-for-using-a-pi-to-burn-a-cluster-using-inventory)
    - [3.3 Can I use the LEDs on the PI Motherboard?](#73-can-i-use-the-leds-on-the-pi-motherboard)
    - [3.4 How can I use pycharm, to edit files or access files in general from my Laptop on the PI?](#74-how-can-i-use-pycharm-to-edit-files-or-access-files-in-general-from-my-laptop-on-the-pi)
    - [3.5 How can I enhance the `get` script?](#75-how-can-i-enhance-the-get-script)
    - [3.6 Can I use a Mesh Network for the setup?](#76-can-i-use-a-mesh-network-for-the-setup)
    - [3.7 Can I use cms burn on Linux?](#77-can-i-use-cms-burn-on-linux)
    - [3.8 What packages do I need to run the info command on macOS](#78-what-packages-do-i-need-to-run-the-info-command-on-macos)
    - [3.9 Are there any unit tests?](#79-are-there-any-unit-tests)
    - [3.10 Using Pi Imager to setup a Manager Pi with headless access](#710-using-pi-imager-to-setup-a-manager-pi-with-headless-access)
    - [3.11 Single Card Burning](#711-single-card-burning)
    - [3.12 How to update firmware?](#712-how-to-update-firmware)
    - [3.13 Alternatives](#713-alternatives)
    - [3.14 How do I scann for WIFI networks?](#714-how-do-i-scann-for-wifi-networks)
    - [3.15 What is the status of the implementation?](#715-what-is-the-status-of-the-implementation)
    - [3.16 I run into a Kernal Panic on my burned Pi. What do I do?](#716-i-run-into-a-kernal-panic-on-my-burned-pi-what-do-i-do)
    - [3.17 How do I enable password login?](#717-how-do-i-enable-password-login)
    - [3.18 How do I use SDCard externers with different voltage?](#718-how-do-i-use-sdcard-externers-with-different-voltage)
    - [3.19 How do I get the latest image if a new image was released?](#719-how-do-i-get-the-latest-image-if-a-new-image-was-released)
  - [4. How can I contribute Contributing](#8-how-can-i-contribute-contributing)

<!--TOC-->

## 1. Burning Tutorials

The latest and most up-to-date burning tutorials are hosted on piplanet.org.

Please see: 
- https://cloudmesh.github.io/pi/tutorial/raspberry-burn/ (burn a raspberry cluster from linux or mac)
- https://cloudmesh.github.io/pi/tutorial/ubuntu-burn/ (burn an ubuntu cluster from linux or mac)
- https://cloudmesh.github.io/pi/tutorial/raspberry-burn-windows/ (burn a raspberry cluster from windows)

## 2. Manual Pages

### 2.1 Manual Page for the `burn` command

Note to execute the command on the command line you have to type in
`cms burn` and not just `burn`.

<!--MANUAL-BURN-->
```
  burn gui [--hostname=HOSTNAME]
           [--ip=IP]
           [--ssid=SSID]
           [--wifipassword=PSK]
           [--bs=BLOCKSIZE]
           [--dryrun]
           [--no_diagram]
  burn ubuntu NAMES [--inventory=INVENTORY] [--ssid=SSID] [-f]
  [--wifipassword=PSK] [-v] --device=DEVICE [--country=COUNTRY]
  [--upgrade]
  burn raspberry NAMES --device=DEVICE
                      [--inventory=INVENTORY]
                      [--ssid=SSID]
                      [--wifipassword=PSK]
                      [--country=COUNTRY]
                      [--password=PASSWORD]
                      [-v]
                      [-f]
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
  burn image versions [--details] [--refresh] [--yaml]
  burn image ls
  burn image delete [--image=IMAGE]
  burn image get [--url=URL] [TAG...]
  burn backup [--device=DEVICE] [--to=DESTINATION]
  burn copy [--device=DEVICE] [--from=DESTINATION]
  burn shrink [--image=IMAGE]
  burn cluster --device=DEVICE --hostname=HOSTNAME
               [--burning=BURNING]
               [--ip=IP]
               [--ssid=SSID]
               [--wifipassword=PSK]
               [--bs=BLOCKSIZE]
               [--os=OS]
               [-y]
               [--imaged]
               [--set_passwd]
  burn create [--image=IMAGE]
              [--device=DEVICE]
              [--burning=BURNING]
              [--hostname=HOSTNAME]
              [--ip=IP]
              [--sshkey=KEY]
              [--blocksize=BLOCKSIZE]
              [--passwd=PASSWD]
              [--ssid=SSID]
              [--wifipassword=PSK]
              [--format]
              [--tag=TAG]
              [--inventory=INVENTORY]
              [--name=NAME]
              [-y]
  burn sdcard [TAG...] [--device=DEVICE] [-y]
  burn set [--hostname=HOSTNAME]
           [--ip=IP]
           [--key=KEY]
           [--keyboard=COUNTRY]
           [--cmdline=CMDLINE]
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
  --hostname=HOSTNAME    The hostnames of the cluster
  --ip=IP                The IP addresses of the cluster
  --key=KEY              The name of the SSH key file
  --blocksize=BLOCKSIZE  The blocksise to burn [default: 4M]
  --burning=BURNING      The hosts to be burned

Arguments:
   TAG                   Keyword tags to identify an image

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

        Checks if the firmware on the Pi is up to date

    cms burn firmware update

        Checks and updates the firmware on the Pi

    cms burn install

        Installs a program to shrink img files. THis is
        useful, after you created a backup to make the
        backup smaller and allow faster burning in case of
        recovery

        This command is not supported on MacOS

    cms burn load --device=DEVICE

        Loads the sdcard into the USB drive. Thi sis similar to
        loading a cdrom drive. It s the opposite to eject

    cms burn format --device=DEVICE

        Formats the SDCard in the specified device. Be
        careful it is the correct device.  cms burn info
        will help you to identifying it

    cms burn mount [--device=DEVICE] [--os=OS]

        Mounts the file systems available on the SDCard

    cms burn unmount [--device=DEVICE] [--os=OS]

        Unmounts the mounted file systems from the SDCard

    cms burn info [--device=DEVICE]

        Provides useful information about the SDCard

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

        Deletes the specified image. The name can be found
        with the image ls command

    cms burn image get [--url=URL] [TAG...]

        Downloads a specific image or the latest
        image. The tag are a number of words separated by
        a space that must occur in the tag that you find
        in the versions command

    cms burn backup [--device=DEVICE] [--to=DESTINATION]

        This command requires you to install pishrink previously with

            cms burn install

        Backs up a SDCard to the given location.

    cms burn copy [--device=DEVICE] [--from=DESTINATION]

        Copies the file form the destination on the SDCard
        this is the same as the SDCard command. we will in
        future remove one

    cms burn shrink [--image=IMAGE]

        Shrinks the size of a backup or image file that
        is on your local file system. It can only be used
        for .img files

       This command is not supported on MacOS.

    cms burn create [--image=IMAGE]
                    [--device=DEVICE]
                    [--hostname=HOSTNAME]
                    [--ip=IP]
                    [--sshkey=KEY]
                    [--blocksize=BLOCKSIZE]
                    [--passwd=PASSWD]
                    [--ssid=SSID]
                    [--wifipassword=PSK]
                    [--format]

        This command  not only can format the SDCard, but
        also initializes it with specific values

    cms burn sdcard [TAG...] [--device=DEVICE]

        this burns the sd card, see also copy and create

    cms burn set [--hostname=HOSTNAME]
                 [--ip=IP]
                 [--key=KEY]
                 [--mount=MOUNTPOINT]
                 [--keyboard=COUNTRY]
                 [--cmdline=CMDLINE]

        Sets specific values on the sdcard after it
        has ben created with the create, copy or sdcard
        command

        a --ssh is missing from this command

    cms burn enable ssh [--mount=MOUNTPOINT]

        Enables the ssh server once it is booted

    cms burn wifi --ssid=SSID [--passwd=PASSWD] [--country=COUNTRY]

        Sets the wifi ssid and password after the card
        is created, copied, or the sdcard is used.

        The option country option expects an ISO 3166-1
        two digit country code. The default is "US" and
        the option not required if suitable. See
        https://en.wikipedia.org/wiki/ISO_3166-1 for other
        countries.

    cms burn check [--device=DEVICE]

        Lists the parameters that were set
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















### 2.2 Manual Page for the `bridge` command

Note to execute the command on the commandline you have to type in
`cms bridge` and not just `bridge`.

<!--MANUAL-BRIDGE-->
```
  bridge create [--interface=INTERFACE] [--ip=IP] [--dns=NAMESERVER]

Options:
  --interface=INTERFACE  The interface name [default: eth1]
                         You can also specify wlan0 if you want
                         to bridge through WIFI on the manager
                         eth0 requires a USB to WIFI adapter

  --ip=IP  The ip address to assign on the eth0 interface,
           ie. the listening interface [default: 10.1.1.1]

  --dns=NAMESERVER  The ip address of a nameserver to set
                    statically. For example, --dns=8.8.8.8,8.8.4.4
                    will use the google nameservers

Description:

  Command used to set up a bride so that all nodes route the traffic
  trough the manager PI.

  bridge create [--interface=INTERFACE] [--ip=IP] [--dns=NAMESERVER]
      creates the bridge on the current device.
      A reboot is required.
```
<!--MANUAL-BRIDGE-->





### 2.3 Manual Page for the `host` command

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
    host key scatter NAMES FILE [--user=USER]
    host key add NAMES FILE
    host key delete NAMES FILE
    host tunnel create NAMES [--port=PORT]
    host mac NAMES [--eth] [--wlan] [--output=FORMAT]
    host setup WORKERS [LAPTOP]
    host shutdown NAMES
    host reboot NAMES
    host adduser NAMES USER
    host passwd NAMES USER
    host addsudo NAMES USER
    host deluser NAMES USER
    host config proxy PROXY NAMES [--append]


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

    host key scatter HOSTS FILE [--user=USER]

      copies all keys from file FILE to authorized_keys on all hosts,
      but also makes sure that the users ~/.ssh/id_rsa.pub key is in
      the file. If provided the optional user, it will add the keys to
      that user's .ssh directory. This is often required when
      adding a new user in which case HOSTS should still a sudo
      user with ssh currently enabled.

      1) adds ~/.id_rsa.pub to the FILE only if its not already in it
      2) removes all duplicated keys

      Example:
          ssh key scatter "red[01-10]"
          ssh key scatter pi@red[01-10] keys.txt --user=alice

    host key add NAMES FILE

      Adds all keys in FILE into the authorized_keys of NAMES.

      Example:
          cms host key add worker001 ~/.ssh/id_rsa.pub

    host key delete NAMES FILE

      Deletes all keys in fILE from authorized_keys of NAMES if they exist.

      Example
          cms host key delete worker001 ~/.ssh/id_rsa.pub

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

    host setup WORKERS [LAPTOP]

      Executes the following steps

          cms bridge create --interface='wlan0'
          cms host key create red00[1-3]
          cms host key gather red00[1-3],you@yourlaptop.local keys.txt
          cms host key scatter red00[1-3],localhost keys.txt
          rm keys.txt
          cms host tunnel create red00[1-3]

    host shutdown NAMES

      Shutsdown NAMES with `sudo shutdown -h now`. If localhost in
      names, it is shutdown last.

    host reboot NAMES

      Reboots NAMES with `sudo reboot`. If localhost in names,
      it is rebooted last.

    host adduser NAMES USER

      Adds a user with user name USER to the hosts identified by
      NAMES. Password is disabled, see host passwd to enable.

    host addsudo NAMES USER

      Adds sudo rights to USER at NAMES

    host passwd NAMES USER

      Changes the password for USER at NAMES

    host deluser NAMES USER

      Deleted USER from NAMES. Home directory will be removed.

    host config proxy PROXY NAMES

      This adds to your ~/.ssh/config file a ProxyJump
      configuration to reach NAMES via PROXY. This is useful when
      the PROXY is acting as a network bridge for NAMES to your
      current device.

      Example:
          cms host config proxy pi@red.lcaol red00[1-2]
```
<!--MANUAL-HOST-->















### 2.4 Manual Page for the `pi` command

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
  pi temp NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
  pi free NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
  pi load NAMES [--rate=SECONDS] [--user=USER] [--output=FORMAT]
  pi wifi SSID [PASSWORD] [--dryrun]
  pi script list SERVICE [--details]
  pi script list SERVICE NAMES
  pi script list

Arguments:
    NAMES       The hostnames in parameterized form
    VALUE       The Values are on, off, 0, 1
    USER        The user name for a login
    SSID        The ssid of your WIfi
    PASSWORD    The assword for the WIFI

  Options:
     -v               verbose mode
     --output=OUTPUT  the format in which this list is given
                      formats includes cat, table, json, yaml,
                      dict. If cat is used, it is just print
     --user=USER      the user name
     --rate=SECONDS   repeats the quere given by the rate in seconds

Description:

      This command allows to set the leds on the PI board and return
      information about the PIs such as temperature, memory space and
      load. It also allows to set the wifi for the PI.

      The most important part of this command is that it executes it not
      only on ome pi but multiple. The hostnames are defined by a parameterized
      notation. red0[1-2] results in red01 and red02.

      The script command are not yet completed and is under development

      The script commands can be used as an alternative to shell scripts.
      They are predefined scripts that can be run easily vai the command
      The script commands are listing details. This is useful as they are
      distributed with the cloudmesh shell. Thus no additional files are
      needed.

      At this time we do not define any predefined scripts.


  Examples:

      This command switches on and off the LEDs of the specified
      PIs. If the hostname is omitted. It is assumed that the
      code is executed on a PI and its LED are set. To list the
      PIs LED status you can use the list command

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

      To showcase information about temperature free space an load
      you can ues

          pi temp "red,red[01-03]"
          pi free "red,red[01-03]"
          pi load "red,red[01-03]"

      To set the WIFI use (where SSID is your ssid). The command
      requires a reboot to activate the WIfi.

          pi wifi SSID

      The script commands are not yet implemented

          pi script list SERVICE [--details]
          pi script list SERVICE NAMES
          pi script list

```
<!--MANUAL-PI-->






### 2.5 Manual Page for the `ssh` command

Note to execute the command on the command line you have to type in
`cms ssh` and not just `ssh`.

THis command is used to easily add and remove entries to the `~/.ssh/config`
file via the commandline

<!--MANUAL-SSH-->
```
    ssh config list [--output=OUTPUT]
    ssh config add NAME IP [USER] [KEY]
    ssh config delete NAME

Arguments:
  NAME        Name or ip of the machine to log in
  list        Lists the machines that are registered and
              the commands to login to them
  PARAMETERS  Register te resource and add the given
              parameters to the ssh config file.  if the
              resource exists, it will be overwritten. The
              information will be written in /.ssh/config
  USER        The username for the ssh resource
  KEY         The location of the public keye used for
              authentication to the host

Options:
   --output=OUTPUT   the format in which this list is given
                     formats includes cat, table, json, yaml,
                     dict. If cat is used, it is just printed as
                     is. [default: table]

Description:
    ssh config list
        lists the hostsnames that are present in the ~/.ssh/config file

    ssh config add NAME IP [USER] [KEY]
        registers a host i ~/.ssh/config file
        Parameters are attribute=value pairs

    ssh config delete NAME
        deletes the named host from the ssh config file

Examples:

     ssh config add blue 192.168.1.245 gregor

         Adds the following to the !/.ssh/config file

         Host blue
              HostName 192.168.1.245
              User gergor
              IdentityFile ~/.ssh/id_rsa.pub

```
<!--MANUAL-SSH-->









## 3. FAQ and Hints

Here, we provide some useful FAQs and hints.

> Note: many of these are out of date or no longer required, but are kept for posterity.

### 3.1 Quickstart for a Setup of a cluster from macOS or Linux with no burning on a PI.

This will setup the same cluster seen in [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi). Pi imager and a manual manager pi setup 
is not required using this method. It will use the latest Pi OS 
images, full for master, and lite for workers.

#### 3.1.1 Prerequisites

* We recommend Python 3.8.2 Python or newer.
* We recommend pip version 21.0.0 or newer
* You have a private and public ssh key named ~/.ssh/id_rsa and ~/.
  ssh/id_rsa.pub
* macOS dependencies [What packages do I need to run the info command on macOS](#what-packages-do-i-need-to-run-the-info-command-on-macos)  

#### 3.1.2 Install Cloudmesh

Create a Python virtual environment `ENV3` in which to install cloudmesh. 
This will keep cloudmesh and its dependencies separate from your default 
environment. 

Always make sure to `source` this environment when working with cloudmesh.

```
you@laptop:~ $ python -m venv ~/ENV3
you@laptop:~ $ source ~/ENV3/bin/activate 
(ENV3) you@laptop:~ $ mkdir cm
(ENV3) you@laptop:~ $ cd cm
(ENV3) you@laptop:~/cm $ pip install cloudmesh-installer
(ENV3) you@laptop:~/cm $ cloudmesh-installer get pi 
```

#### 3.1.3 Create a Cluster

Here, we demonstarte how to burn 1 manager and 2 worker SD Cards. The 
manager is called red, the workers are red001 and red002.

**Step 1.** Identify the SD card device

Plug in a sd card reader with sd card to the laptop and identify the device.
In Linux it is /dev/sdX in macOS it is /dev/diskX.

```
(ENV3) you@laptop:~ $ cms burn info 
```

```
# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+----------------------------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+
| Path     | Info                                         | Formatted   | Size             | Plugged-in   | Readable   | Empty   | Access   | Removable   | Writeable   |
|----------+----------------------------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------|
| /dev/diskX | Generic- USB3.0 CRW-SD/MS 1.00 PQ: 0 ANSI: 6 | True        | 
64.1 GB/59.7 GiB | True         | True       | False   | True     | True        | True        |
+----------+----------------------------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+

```

**Step 2.** Burn the SD cards 

You will be prompted to input your wifi password for your SSID when runing the 
command below.

```
(ENV3) you@laptop:~ $ cms burn cluster --device=/dev/diskX --hostname="red,red00[1-2]" --ssid=SSID
```

**Step 3.** Boot the cluster and complete setup of cloudmesh and all ssh 
access

Plug in the SD Cards in the PI's and start them up. It will take at least 60 
seconds for them to boot for the first time.

Now login to the manager with 

```
(ENV3) you@laptop:~ $ ssh pi@red.local
```

On the manager you call the follwoing commands

```
pi@red:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -
pi@red:~ $ sudo reboot
(ENV3) pi@red:~ $ cms host setup red00[1-2] you@laptop.local 
```

Copy the specified command output to your ~/.ssh/config file on your laptop. 
W weill soon have a command that will add them for you without using an editor.

```
# ----------------------------------------------------------------------
# copy to ~/.ssh/config on remote host (i.e laptop)
# ----------------------------------------------------------------------

Host red
     HostName red.local
     User pi

Host red001
     HostName red.local
     User pi
     Port 8001

Host red002
     HostName red.local
     User pi
     Port 8002

```

Let us test by running a command from the laptop to get the Pis' 
temperatures.

```
(ENV3) you@laptop:~ $ cms pi temp red,red00[1-2]              
pi temp red,red00[1-2]
+--------+--------+-------+----------------------------+
| host   |    cpu |   gpu | date                       |
|--------+--------+-------+----------------------------|
| red    | 50.147 |  50.1 | 2021-02-18 21:10:05.942494 |
| red001 | 51.608 |  51.6 | 2021-02-18 21:10:06.153189 |
| red002 | 45.764 |  45.7 | 2021-02-18 21:10:06.163067 |
+--------+--------+-------+----------------------------+

```

<a name="clustermac"></a>

### 3.2 Quickstart for Using a Pi to Burn a Cluster Using Inventory

In this guide, we will show how you can configure a Cloudmesh Inventory to
easily burn a cluster of SD cards as well as configure the current Pi as the
manager if desired.

We will follow the same network setup as the Bridged Wifi explained in a
previous section (see Figure 1).

The requirements for this guide are the same as the [Quickstart for Bridged WiFi](#quickstart-for-bridged-wifi).

#### 3.2.1 Initial Manager Setup

Ensure you have burned an SD card from your laptop using [Raspberry Pi
Imager](#https://www.raspberrypi.org/software/). Ensure you burn the card with
**Raspberry Pi OS 32-bit with desktop and recommended applications**. This will
serve as our manager.

Once you have burned your manager card, plug this into a Raspberry Pi. Connect
this Pi to a keyboard, mouse, and monitor and boot. Walk through the initial
setup prompt to rename your Pi's hostname to `managerpi` as well as connect to
Wifi. You should also change your password in doing so.

If you are logged in via SSH, you may accomplish the above with `sudo
raspi-config`. For more information on setups, see [Manager Pi
Setup](#32-manager-pi)

From here, we assume your Pi hostname is `managerpi`.

Once you have gone through this, you may install cloudmesh and configure your
system with the following:

```
pi@managerpi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -
```

Reboot after this script

```
pi@managerpi:~ $ sudo reboot
```

#### 3.2.2 Creating our inventory

For this guide, we will create two workers for `managerpi`. We can do this as
follows:

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

#### 3.2.3 Burning SD Cards using Inventory

First, verify that you have plugged in your SD card writer with an SD card into
the `managerpi`. For this guide, we will simply use one SD card burner to burn
both SD cards.

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

Note that in this example, the hostname of the manager passed into `cms burn
create` is the same as the current system's hostname. This is intentnional (as
indicated by our `Y` choice) and we are also configuring the `managerpi` as a
bridge (as indicated by our `)

We must now reboot the manager.

```
(ENV3) pi@managerpi:~ $ sudo reboot
```

#### 3.2.4 Booting Up Workers and Verifying Connection

Insert the burned worker cards into the worker Pis and boot.

With the following command, you can verify connection to your workers:

```
(ENV3) pi@managerpi:~ $ cms pi temp red002
pi temp red002
+--------+--------+-------+----------------------------+
| host   |    cpu |   gpu | date                       |
|--------+--------+-------+----------------------------|
| red002 | 37.485 |  37.4 | 2021-02-20 00:47:19.212921 |
+--------+--------+-------+----------------------------+
```

### 3.3 Can I use the LEDs on the PI Motherboard?

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


### 3.4 How can I use pycharm, to edit files or access files in general from my Laptop on the PI?

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

Now let us create a directory in which we mount the remote PI directories in our 
case we mount the directory cm

```
mkdir redcm
sshfs red:/home/pi/cm  redcm -o auto_cache
```

To unmount the filesystem use on LInux

```
$ fusermount -u redcm
```

and on macOS

```
umount redcm
```

If you need other directories, pleas apply  our strategy accordingly

### 3.5 How can I enhance the `get` script?

Instead of using the link

* <http://cloudmesh.github.io/get/pi>

please use

* <https://raw.githubusercontent.com/cloudmesh/get/main/pi>

This allows us to test also modifications to the get script before we
push them to the official community repository.

You can create a pull request at

* <https://github.com/cloudmesh/get/blob/main/pi/index.html>

### 3.6 Can I use a Mesh Network for the setup?

This section is still under development.

In case you have a Mesh Network, the setup can typically be even more
simple as we can attach the unmanaged router directly to a Mesh
node via a network cable. In that case, the node is directly connected
to the internet and uses the DHCP feature from the Mesh router (see
Figure 2).

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-mesh.png)

Figure 2: Networking with Mesh network

You will not need the bridge command to setup the network.

### 3.7 Can I use cms burn on Linux?

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


### 3.8 What packages do I need to run the info command on macOS

```
brew install libusb
```

**Access to ext4**: For the more advanced features of `burn` you will
need full write access to the ext4 partition on your SDCard that is
created when you burn it. Unfortunately, the tools that used to be
freely available seem no longer to work properly, so you could use
[extFS for Mac by Paragon Software](https://www.paragon-software.com/us/home/extfs-mac/)
which does cost $40 for a license.

For this reason, we recommend that you first set up the manager PI and
do all burning on the manager PI.

### 3.9 Are there any unit tests?

As `cms burn` may delete and format files and disks/SD Cards during unit
testing users are supposed to first review the tests before running
them. Please look at the source and see if you can run a test.

We have the following tests:

* `pytest -v --capture=no tests/test_01_image.py`

  * This test removes files from ~/.cloudmesh/cmburn/images
  * See also:
  [test_01_image.py](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/tests/test_01_image.py)

* TODO: add the other tests

### 3.10 Using Pi Imager to setup a Manager Pi with headless access

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

### 3.11 Single Card Burning

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

### 3.12 How to update firmware?

To update the firmware reference the [raspi documentation](#https://www.raspberrypi.org/documentation/hardware/raspberrypi/booteeprom.md) 

Or follow the simple instructions below.

```
pi@managerpi:~ $ sudo apt update
pi@managerpi:~ $ sudo apt full-upgrade
pi@managerpi:~ $ sudo reboot
pi@managerpi:~ $ sudo rpi-eeprom-update -a
pi@managerpi:~ $ sudo reboot
```

### 3.13 Alternatives

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

### 3.14 How do I scann for WIFI networks?

```
sudo iwlist wlan0 scan
```


### 7.15 What is the status of the implementation?

| Feature         | PI    | Ubuntu | Mac   | Windows |
| --------------- | ----- | ------ | ----- | ------- |
| image versions  |    +  |    +   |    +  |         |
| image ls        |    +  |    +   |    +  |         |
| image delete    |    +  |    +   |    +  |         |
| image get       |    +  |    +   |    +  |         |
| info            |    +  |    +   |    +  |         |
| network         |    +  |    +   |       |         |
| backup          |    +  |    +   |    +  |         |
| copy            |    +  |    +   |       |         |
| shrink install  |    +  |    +   |       |         |
| shrink          |    +  |    +   |       |         |
| sdcard          |    +  |    +   |    +  |         |
| mount           |    +  |    +   |    +  |         |
| unmount         |    +  |    +   |    +  |         |
| enable ssh      |    +  |    +   |    +  |         |
| wifi            |    +  |    +   |    +  |         |
| set             |    +  |    +   |    +  |         |
| create          |  TODO |   (1)  |   (1) |         |
| cluster         |    NA |    +   |    +  |         |
| check           |    +  |    +   |    +  |         |
| format          |    +  |    +   |    +  |         |
| cluster         |   NA  |    +   |    +  |         | 
| firmware        |    +  |   NA   |   NA  | NA      |
| inventory       |       |        |       |         |

* (1)  use the `cluster` command instead 
* for macOS, only the image commands have unit tests
* firmware does not have a unit test
* empty = not yet implemented or teste, an implementation could be provided by 
  the community
* - = broken
* NA = Not applicable for this OS

* TODO1 = todo for boot fs, rootfs not supported

### 3.16 I run into a Kernal Panic on my burned Pi. What do I do?

Occassionally, one may run into an error similar to the following:

```
Kernel panic-not syncing: VFS: unable to mount root fs on unknown-block(179,2)
```

See [here](https://raspberrypi.stackexchange.com/questions/40854/kernel-panic-not-syncing-vfs-unable-to-mount-root-fs-on-unknown-block179-6) for more information on this bug.

This error has been reported in the past. A simple reburn using `cms burn`
tends to resolve the issue.

### 3.17 How do I enable password login?

The option `--set_passwd` in `cms burn cluster` enables you to securely enter a
password to prevent the password disable.

The option `[--passwd=PASSWD]` is used with `cms burn create` todo the same
thing. Note entering the passwd in the command is optional.If empty you will be
prompted.

### 3.18 How do I use SDCard externers with different voltage?


Becauase I am using and sd card extender, I need to set a cmdline argument to
force 3.3V SD card operation.

You can set an arbitray command line argument with

```
cms burn set --cmdline=CMDLINE
```

To force 3.3V operation to enable the use of an SD card extender use

```
cms burn set--cmdline=sdhci.quirks2=4
```

### 3.19 How do I get the latest image if a new image was released?

From time to time raspberry.org releases new operating systems. To assure you
get the latest version, you can do the following to download the latest lite
abd full images :

```bash
$ cms burn image versions --refresh
$ cms burn image get latest-lite
$ cms burn image get latest-full
```

To safe space you can also delete the old versions. Look at the storage
location where we place the images with

```bash
$ ls -1 ~/.cloudmesh/cmburn/images
```

YOu can delete the ones that do not have the lates date. Such as 

```bash
$ rm  ~/.cloudmesh/cmburn/images/2021-01-11-raspio*
```

If you see any images with the date 2021-01-11 and so on.

## 4. How can I contribute Contributing

The code uses a variety of cloudmesh components. This mainly includes

  * [GitHub cloudmesh-pi-burn](https://github.com/cloudmesh/cloudmesh-pi-burn)
  * [GitHub cloudmesh-pi-cluster](https://github.com/cloudmesh/cloudmesh-pi-cluster)
    
Additional cloudmesh components are used. For example:
  * [GitHub cloudmesh-pi-common](https://github.com/cloudmesh/cloudmesh-common)
  * [GitHub cloudmesh-pi-cmd5](https://github.com/cloudmesh/cloudmesh-cmd5)
  * [GitHub cloudmesh-pi-inventory](https://github.com/cloudmesh/cloudmesh-inventory)
