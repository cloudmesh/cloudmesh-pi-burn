# Easy Raspberry PI Cluster Setup with Cloudmesh SDCard Burner

## Upload an image

![Many Pi's](images/many-pis.jpg)

## Description

Authors: 
- Gregor von Laszewski, laszewski@gmail.com
- Richard Otten
- Anthony Orlowski

### Introduction

Over time we have seen many efforts to create Clusters using Pi's as a
platform. There are many reasons for this. You have full control over the PIs,
you use an inexpensive platform, and you use a highly usable platform
and provides an enormous benefit to get educated about cluster computing in
general.

There are different methods of how to set up a cluster. This includes setups
that are known under the terms *headless*, *network booting*, and *booting from
SDCards*. Each of the methods has its advantages and disadvantages. However,
the last method is most familiar to the users in the Pi community that come
from single Pis. While reviewing the many efforts that describe a cluster set up
most of them contain many complex steps that require a significant amount of
time as they are executed individually on these Pis. Even starting is
non-trivial as a network needs to be set up to access them. 

Despite the much improved Pi imager and the availability of Pi bakery, the
process is still involved. So we started asking:

> Is it possible to develop a tool that is specifically targeted to burn 
> SDCards in a cluster one at a time so we can just  plug 
> the cards in, and with minimal effort start the cluster that simply works?

You are in luck, we have spent some time to develop such a tool. No more
spending hours upon hours to replicate the steps, learn complex DevOps
tutorial, but instead get a cluster set up easily with just a few commands.

For this, we developed `cms burn` which is a program that you can execute
either on a "manager" Pi (or in a Linux or macOS computers) to burn cards for
your cluster. 

We have set up on GitHub a comprehensive package that can be installed  easily
we hope that it is useful to you.

All of this is discussed in detail at 
<https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md>

To showcase to you that this tool is useful we demonstrate from our quickstart 
how easy it is to use it.

## QuickStart

### Requirements

* 5 Raspberry Pis
* 5 SD Cards
* Network Switch (unmanaged or managed)
* 5 Ethernet Cables
* Wifi Access
* Monitor, Mouse, Keyboard (for desktop access on Pi)
* 1 (or more) SD Card Burner(s) (USB)

We will be creating the following setup using **5 Raspberry Pis** 
(you need a minimum of 2, but our method works also for larger 
numbers of PIs). Consequentially, you will also need 5 SD cards for each of the 5 Pis.

You will also went a network switch (managed or unmanaged) with 5 ethernet cables (one fo reach Pi).

Figure 1 below describes our network configuration. We have 5 Raspberry Pi 4s: 1
manager and 4 workers. We use WiFi access to the manager PI to allow for you to
set it up anywhere in your house or dorm (other configurations are discussed
on our home page).

We use a network switch (unmanaged in our case), where the manager and workers can
communicate locally, but we will configure the manager to provide
internet access to devices on the network switch via a "network
bridge".

![](https://github.com/cloudmesh/cloudmesh-pi-burn/raw/main/images/network-bridge.png)

Figure 1: Pi Cluster setup with bridge network


### Step 1. Burning and Configuring the Manager

Choose one SD card to be the manager (yellow card in figure 1). Using your laptop, download the [Raspberry Pi Imager]
(https://www.raspberrypi.org/software/) for your respective operating system. We will use the Pi Imager to burn our 
manager. Note this is the only time we will need to use PI Imager.

You should select the recommended Raspberry Pi OS. (Raspberry PI OS Full (32-bit) with recommended software and applications).

<center>
<img src="images/imager-with-options.png" width="50%" />

Figure 2. Pi Imager
</center>

Write to your SD card. Once the process is complete and verified, insert into your manager
Pi. Connect your manager to the peripherals (keyboard, mouse, monitor).

> Note you may also use a headless setup. See [here](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md) for more information on headless setups.

Walk through the initial setup process of the Pi and configure the settings in accordance with your situation. 
We have provided images that depict this process below:

<center>
<img src="images/setup1.png" width="50%" />

Figure 3. Welcome Page for Raspberry Pi
</center>



</center>
<img src="images/setup2.png" width="50%" />

Figure 4. Set country, language, and timezone. Additionally, we recommend you enable "Use US Keyboard".
</center>




<center>
<img src="images/setup3.png" width="50%" />

Figure 5. Set your password to a strong password.
</center>




<center>
<img src="images/setup4.png" width="50%" />

Figure 6. Choose your Wifi network.
</center>




<center>
<img src="images/setup5.png" width="50%" />

Figure 7. The setup prompt will ask you if you wish to update the software. You may do so, or you may skip, as our installation script that we will run will do this for you.

</center>

<center>
<img src="images/setup6.png" width="50%" />

Figure 8. Setup is now complete.
</center>



### Step 2. Installing Cloudmesh

Open a new terminal window and run the following command. This will install cloudmesh and upgrade your system if needed.

```
pi@managerpi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh -
```

This will set up a python venv on your computer manager Pi. This may take 5-7 minutes as it will update your Pi and install all requirements.

You will want to reboot your Pi after this.

```
pi@managerpi:~ $ sudo reboot
```

### Step 3. Creating our Cluster Inventory

To manage information about our cluster, we will use a Cloudmesh Inventory file, which comes 
installed with cloudmesh. This will allow you to easily track and manage the configuration of your workers.

Let us create an inventory for our cluster as follows:

```
(ENV3) pi@managerpi:~ $ cms inventory create --hostnames="managerpi,worker00[1-4]" --ip="10.1.1.[1-5]"  --inventory=cluster.yaml latest-lite
```

We can list the information in our inventory as follows. Confirm all is as expected:

```
(ENV3) pi@managerpi:~ $ cms inventory list --inventory=cluster.yaml
inventory list --inventory=cluster.yaml
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| host      | name      | type | tag         | cluster | label | service | services | ip       | dns | project | owners | comment | description | keyfile           | status   |
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
| managerpi | managerpi |      | latest-lite | cluster |       | manager |          | 10.1.1.1 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| worker001 | worker001 |      | latest-lite | cluster |       | worker  |          | 10.1.1.2 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| worker002 | worker002 |      | latest-lite | cluster |       | worker  |          | 10.1.1.3 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| worker003 | worker003 |      | latest-lite | cluster |       | worker  |          | 10.1.1.4 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
| worker004 | worker004 |      | latest-lite | cluster |       | worker  |          | 10.1.1.5 |     |         |        |         |             | ~/.ssh/id_rsa.pub | inactive |
+-----------+-----------+------+-------------+---------+-------+---------+----------+----------+-----+---------+--------+---------+-------------+-------------------+----------+
```

We can now begin burning.

### Step 4. Burning SD Cards

You can now plug in your SD Card writer into the `managerpi`. Ensure you have also inserted an SD card into your writer. *Warning* this SD Card will be formatted, thus all content will be deleted.

Verify your device is detected with the following command:

```bash
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

> Note we omit some information from `cms burn info` for simplicity

From `cms burn info`, we see our device is `/dev/sdb`. Note this may be different on your Pi. If your device is not showing up, ensure you have an SD Card inserted, and try unplugging and plugging the SD Card writer.

We can now begin burning our cluster. The following command will download the necessary Raspberry Pi OS images, configure `manager` as a Wifi bridge to provide internet access to workers, and burn the SD Cards. Note you will need to cycle SD cards after each burn.

```
(ENV3) pi@managerpi:~ $ cms burn create --inventory=cluster.yaml --device=/dev/sdb --name=managerpi,worker00[1-5]

Manager hostname is the same as this system's hostname. Is this intended? (Y/n) Y
Do you wish to configure this system as a WiFi bridge? A restart is required after this command terminates (Y/n) Y

```
> Some output of cms burn has been omitted for simplicity. Note that image extraction may take more than a minute.

As each SD Card is burned, `cms burn` will prompt you to insert a new SD Card to be burned.


After all curds are burned, plug them into your worker Pis and boot. Reboot the managerpi.

```
(ENV3) pi@managerpi:~ $ sudo reboot
```

### Step 5. Verifying Workers

Once your workers are booted, you can verify connection with the following simple command. This command will return the temperature of the Pis.

```
(ENV3) pi@managerpi:~ $ cms pi temp worker00[1-4]
pi temp worker00[1-4]
+-----------+--------+-------+----------------------------+
| host      |    cpu |   gpu | date                       |
|-----------+--------+-------+----------------------------|
| worker001 | 36.511 |  36.5 | 2021-02-22 00:06:48.873427 |
| worker002 | 36.998 |  37   | 2021-02-22 00:06:48.813539 |
| worker003 | 36.998 |  37   | 2021-02-22 00:06:48.843944 |
| worker004 | 36.498 |  36   | 2021-02-22 00:06:48.843956 |
+-----------+--------+-------+----------------------------+
```

#### Acknowledgement

We would like to thank the following community members for testing the recent versions:
Venkata Sai Dhakshesh Kolli,
Rama Asuri,
Adam Ratzman.
Previous versions of the software obtained code contributions from 
Sub Raizada,
Jonathan Branam,
Fugang Wnag,
Anand Sriramulu, 
Akshay Kowshik.

### Refernces

* TODO: include here the links


## Category

Software

## Project Status

Ongoing project

## Privacy Status

Public project

## Public Messaging Room

Disabled

## Tags

Raspberry
Raspberry PI
Cluster
SDCard

## External Links

Have source code somewhere else or a homepage?

How about a thank-you link to the project that inspired you?

    Select Network

Add More Links

## Team

* Gregor von Laszewski
* Richard Otten https://hackaday.io/devrick
* Anthony Orlowski https://hackaday.io/antorlowski

You need to create an account on hackaday.io, I need the account name.

## Feed

Do you want this update to show up in the feed?

Yes

Show update in the feed

