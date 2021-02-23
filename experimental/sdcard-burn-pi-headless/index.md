---
date: 2021-02-07
title: "Easy Raspberry PI Cluster Setup with Cloudmesh SDCard Burner without Desktop"
linkTitle: "Burn many SD Cards with a Pi for clusters without a desktop manager"
description: >
  Set up many SD Cards that are preconfigured to create PI clusters without a desktop manager.
author: Gregor von Laszewski ([laszewski@gmail.com](mailto:laszewski@gmail.com), [laszewski.github.io](https://laszewski.github.io)), 
  Richard Otten, 
  Anthony Orlowski
  Adam ...
draft: True
categories:
- tutorial
tags:
- Raspberry Pi
- Cluster  
- SD Cards
- Burn
- Tutorial
resources:
- src: "**.{png,jpg}"
  title: "Image #:counter"
---

{{< imgproc many Fill "600x300" >}}
{{< /imgproc >}}

<!--
## Upload an image

![Many Pi's](many-pis.jpg)
-->


{{% pageinfo %}}

In this tutorial, we explain how to easily set up a cluster of Pis
while burning preconfigured SD Cards. We assume you use an SD Card reader/writer that
is plugged into your manager PI that we configure initially with Pi Imager.

**Learning Objectives**

* Learn how to use cloudmesh burn to create many SD Cards for a cluster
* Test the cluster after burning
  
**Topics covered**

{{% table_of_contents %}}

{{% /pageinfo %}}


## 1. Introduction

Over time we have seen many efforts to create Clusters using Pi's as a
platform. There are many reasons for this. You have full control over the PIs,
you use an inexpensive platform, and you use a highly usable platform
and provides an enormous benefit to get educated about cluster computing in
general.

There are different methods of how to set up a cluster. This includes setups
that are known under the terms *headless*, *network booting*, and *booting from
SD Cards*. Each of the methods has its advantages and disadvantages. However,
the last method is most familiar to the users in the Pi community that come
from single Pis. While reviewing the many efforts that describe a cluster set up
most of them contain many complex steps that require a significant amount of
time as they are executed individually on these Pis. Even starting is
non-trivial as a network needs to be set up to access them. 

Despite the much improved Pi imager and the availability of Pi bakery, the
process is still involved. So we started asking:

> Is it possible to develop a tool that is specifically targeted to burn 
> SDCards for the PIs in a cluster one at a time, so we can just  plug 
> the cards in, and with minimal effort start the cluster that simply works?

You are in luck, we have spent some time to develop such a tool and present it at 
as part of [PiPlanet](https://piplanet.org)[^piplanet] 
. No more
spending hours upon hours to replicate the steps, learn complex DevOps
tutorials, but instead get a cluster set up easily with just a few commands.

For this, we developed `cms burn` which is a program that you can execute
either on a "manager" Pi (or in a Linux or macOS computers) to burn cards for
your cluster. 

We have set up on GitHub a comprehensive package that can be installed easily
we hope that it is useful to you. All of this is discussed in detail at the
[cloudmesh-pi-burn README](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md)[^README].
There you can also find detailed instructions on how to use a Mac or Linux
computer to burn directly from them. To showcase to you how easy it is to use
we demonstrate here the setup of a cluster with five nodes.

## 2. Requirements

* 5 Raspberry Pis
* 5 SD Cards
* Network Switch (unmanaged or managed)
* 5 Ethernet Cables
* Wifi Access
* Monitor, Mouse, Keyboard (for desktop access on Pi)
* 1 SD Card Burner(s) (we recommend one that supports USB 3.0 speeds)

For a list of possible part choices, please see:

* [Parts Choices](/pi/docs/hardware/parts/)[^parts]

## 3. The Goal

We will be creating the following setup using **5 Raspberry Pis** (you need a
minimum of 2, but our method works also for larger numbers of PIs).
Consequentially, you will also need 5 SD cards for each of the 5 Pis.
You will also want a network switch (managed or unmanaged) with 5 ethernet
cables (one for each Pi).

Figure 1 shows our network configuration. From the five Raspberry Pis, one is
dedicated as a manager and four as workers. We use WiFi between the manager
PI to allow for you to set it up anywhere in your house or dorm (other
configurations are discussed in the 
[README](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md)).

We use an unmanaged network switch, where the manager and workers can
communicate locally with each other, and the manager provides
internet access to the workers via a bridge that we configure for you.

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Pi Cluster setup with bridge network

## 4. Steps

### Burning and Configuring the Manager

### Create an SSH key for yor Computer

If yo do nt yet have an ssh key on your computer, create one now. If you do
have one, please skip this step. we assume you use an id_rsa key.

As we will be using keys to authenticate with the workers, you need to create
one  in a terminal with

```bash
pi@managerpi:~ $ ssh-keygen
```

It will ask you for a location, choose the default. It will also ask you for a
passphrase. Please use a strong one and do not make it the same as the password
for your manager PI.


#### Install Cloudmesh on your Computer

Create a Python virtual environment `ENV3` in which to install cloudmesh. 
This will keep cloudmesh and its dependencies separate from your default 
environment. 

Always make sure to `source` this environment when working with cloudmesh.

```bash
you@laptop:~ $ python -m venv ~/ENV3
you@laptop:~ $ source ~/ENV3/bin/activate 
(ENV3) you@laptop:~ $ mkdir cm
(ENV3) you@laptop:~ $ cd cm
(ENV3) you@laptop:~/cm $ pip install cloudmesh-installer
(ENV3) you@laptop:~/cm $ cloudmesh-installer get pi 
```

####  Find the device for your USB reader/writer

Plug your USB reade writer in your computer and find the device i=t uses.
Please use the command

```bash
you@laptop:~ $ cms burn info
```

On MacOS it will be something like /dev/deviceN where N is a number, likely 2.
On Linux it will be something like /dev/sdX where X is a letter, likely b

For convenience, lets set a shell variable for it, lets assume you have a Mac. 
If not adapt for Linux

```bash
you@laptop:~ $ export SDCARD=/dev/deviceN
````

#### Burn the Maanager

We will name the manager pi `red`. SSID is the name of your WIFI ssid.

```bash
you@laptop:~ $ cms burn cluster --device=$SDCARD --hostname=red --ssid=SSID
```

#### Start the Maanager

After burning, put the card into the manager and power on the manager.

#### Connect to the Manager

> TODO: verify this step, I know we have an ssh command, but it may not yet be
>  installed. We may have to put this in its own new package cloudmesh-ssh

From your laptop issue the command. we could look at 

cms host ssh command, but that may not yet have a repeat option and does not d o
interactive but just a command at a time. We do have however the ssh command 
somehwere, maybe in cloudmesh-cloud

```
cms ssh pi@red.local
```

THis will connect you to your manager pi. It will probe the pi repeatedtly 
and connect when it has booted up. If this command does not return after several 
minutes something is wrong. Maybe check the SSID or see if you can see the manager 
on your WIFI using other methods.


### Plug in the SD Card Reader/writer into the manager PI

Once you have logged into the manager, Plug in the SD Card Reader/writer into
the manager PI. You are all set to continue

## Setting up the Manager PI for burning workers

### Step 2. Create an SSH key on the Manager Pi

As we will be using keys to authenticate with the workers, you need to create
one  in a terminal with

```bash
pi@red:~ $ ssh-keygen
```

It will ask you for a location, choose the default. It will also ask you for a
passphrase. Please use a strong one and do not make it the same as the password
for your manager PI.

### Step 3. Installing Cloudmesh

Now let us install cloudmesh burn, which allows us to burn preconfigured SD
Cards for clusters easily. Open a new terminal window and run the following
command. To make the installation and needed updates to your PI simple, we have
provided a one-line install script that you can run via curl:

```
pi@red:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -
```

This will set up a python venv on your computer manager Pi. It may take 5-7
minutes as it will also update your Pi and install all other requirements.

You will want to reboot your Pi after this.

```
pi@red:~ $ sudo reboot
```

### Step 4. Creating our Cluster Inventory

To manage information about our cluster, we will use a Cloudmesh Inventory.
This will allow you to easily track and manage the configuration of your
cluster nodes.  Let us create an inventory for our cluster as follows:

```
(ENV3) pi@red:~ $ cms inventory create --hostnames="red,red0[1-4]" --ip="10.1.1.[1-5]"  --inventory=cluster.yaml latest-lite
```

You can inspect the inventory with the list command as shown next. Double-check
if it looks like:


```
(ENV3) pi@red:~ $ cms inventory list --inventory=cluster.yaml

+-----------+-------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| host      | name  | type | tag         | cluster | label | service | services | ip       | dns | project | owners | comment | description | keyfile           | status   |
+-----------+-------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| red       |   red |      | latest-lite | cluster |       | manager |          | 10.1.1.1 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red01     | red01 |      | latest-lite | cluster |       | worker  |          | 10.1.1.2 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red02     | red02 |      | latest-lite | cluster |       | worker  |          | 10.1.1.3 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red03     | red03 |      | latest-lite | cluster |       | worker  |          | 10.1.1.4 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| red04     | red04 |      | latest-lite | cluster |       | worker  |          | 10.1.1.5 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
```


### Step 5. Burning the SD Cards

We can now begin burning.

You can now plug in your SD Card reader/writer into the `managerpi`. Ensure you
have also inserted an SD card into your reader/writer. *Warning* this SD Card
will be formatted, thus all content will be deleted and lost.

Verify your device is detected with the following command:

```bash
(ENV3) pi@red:~ $ cms burn info

# ----------------------------------------------------------------------
# SD Cards Found
# ----------------------------------------------------------------------

+----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+
| Path     | Info                   | Formatted   | Size             | Plugged-in   | Readable   | Empty   | Access   | Removable   | Writeable   |
|----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------|
| /dev/sdb | Generic STORAGE DEVICE | True        | 64.1 GB/59.7 GiB | True         | True       | False   | True     | True        | True        |
+----------+------------------------+-------------+------------------+--------------+------------+---------+----------+-------------+-------------+
```

> Note we omit some information from `cms burn info` for simplicity

From `cms burn info`, we see our device is `/dev/sdb`. Note this may be
different on your Pi. If your device is not showing up, ensure you have an SD
Card inserted, and try unplugging and plugging the SD Card reader/writer.

We can now begin burning our cluster. The following command will download the
necessary Raspberry Pi OS images, configure `manager` as a Wifi bridge to
provide internet access to workers and burn the SD Cards. Note you will need
to cycle SD cards after each burn.

```
(ENV3) pi@red:~ $ cms burn create --inventory=cluster.yaml --device=/dev/sdb --name=red,red0[1-4]

Manager hostname is the same as this system's hostname. Is this intended? (Y/n) Y
Do you wish to configure this system as a WiFi bridge? A restart is required after this command terminates (Y/n) Y

```
> Some output of cms burn has been omitted for simplicity. Note that image 
> extraction may take more than a minute.

As each SD Card is burned, `cms burn` will prompt you to insert a new SD Card
to be burned.


After all the cards are burned, plug them into your worker Pis and boot. Reboot the
managerpi red.

```
(ENV3) pi@red:~ $ sudo reboot
```

### Step 6. Verifying the Workers

Once your workers are booted, you can verify the connection with the following
simple command. This command will return the temperature of the Pis.

```
(ENV3) pi@red:~ $ cms pi temp red0[1-4]
pi temp red0[1-4]
+-----------+--------+-------+----------------------------+
| host      |    cpu |   gpu | date                       |
|-----------+--------+-------+----------------------------|
| red01     | 36.511 |  36.5 | 2021-02-22 00:06:48.873427 |
| red02     | 36.998 |  37   | 2021-02-22 00:06:48.813539 |
| red03     | 36.998 |  37   | 2021-02-22 00:06:48.843944 |
| red04     | 36.498 |  36   | 2021-02-22 00:06:48.843956 |
+-----------+--------+-------+----------------------------+
```

## 5. Using the Pis

As we use ssh keys to authenticate between manager and workers, you can 
directly log into the workers from the manager.

More details are provided on our web pages at

* [README](https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md)
* [piplanet.org](https://piplanet.org)

Other cloudmesh components are discussed in the [cloudmesh manual](<https://cloudmesh.github.io/cloudmesh-manual/>)[^cloudmesh-manual].


## Acknowledgement

We would like to thank the following community members for testing the recent
versions:
Venkata Sai Dhakshesh Kolli,
Rama Asuri,
Adam Ratzman.
Previous versions of the software obtained code contributions from 
Sub Raizada,
Jonathan Branam,
Fugang Wnag,
Anand Sriramulu, 
Akshay Kowshik.

## References

[^cloudmesh-manual]: Cloudmesh Manual, <https://cloudmesh.github.io/cloudmesh-manual/>
[^piplanet]: PiPlanet Web Site, <https://piplanet.org>
[^parts]: Parts for building clusters, <https://cloudmesh.github.io/pi/docs/hardware/parts/>
[^README]: Cloudmesh pi burn README, <https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md>






