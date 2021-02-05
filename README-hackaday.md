# Easy Raspberry PI Cluster Setup with Cloudmesh SDCard Burner

## Upload an image

## Description

### Introduction

Over time we have seen many efforts to create Clusters using Pi's 
as a platform. There are many reasons for this. You have full controll 
over teh PIs, you use a platform that is inexpensive, and you use a platform 
that is highly usable and provides an enormpus benefit to get eductted about 
cluster computing in general.

There are several different methods on how to set up a cluster. This includes
setups known under the terms *headless*, *network booting*, and *booting form
SDCards* and describe them in more detail next.
Each of the methods has its advantages and disadvantages. HOwever the last 
method is most familiar to the community. However, all tutorials we have seen 
are consisting a number of complex steps that require a significant amount 
of time. Despite the much improved Pi imager and teh availability of Pi 
bakery the process is still involved. So we started asking:

> Is it possible to develop a tool that is specifically targeted to burn 
> SDCards that creates all Cards for the cluster one at a tim. We than plug 
> the cards in, and the cluster simply works?

So you are in luck, we have developed such a tool. No more spendiing hours 
upon hours to replicate the steps, but get a cluster set up easily with just 
a few commands.

For this we developed `cloudmesh burn` whish is a programm that you can 
execute either on a "manager" Pi (or in a Linux desktop) to burn cards 
for youe cluster

We have set up on github a comprehensive package that is easily installable 
and we hope that it is useful to you.

All of this is discussed in detail at 
<https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md>

To showcase you that this tool is useful we demonstrate form our quickstart 
how easy it is to use it.

### Example

We will be creating the following setup using 4 Raspberry Pis 
(you need a minimum of 2, but our method works also for larger 
numbers of PIs).

TODO: image and details of quickstart

First, install the program with


```
pi@raspberrypi:~ $ pip install pip -U
pi@raspberrypi:~ $ curl -Ls http://cloudmesh.github.io/get/pi | sh
pi@raspberrypi:~ $ source ~/ENV3/bin/activate
```


Second, plugin your SDCard writer and  identify the device on which your 
SDCard is plugged in. in the PI this will be typically be `/dev/sda`. On other 
operating systems this will be differnt. You can use our  `info` command 
to find it with

```bash
(ENV3) pi@raspberrypi:~ $ cms pi burn info
```

set yur device with 

pi@raspberrypi:~ $ export DEV=/dev/sda

Next, download the newest raspbianOS with

```
(ENV3) pi@raspberrypi:~ $ cms burn image versions --refresh
(ENV3) pi@raspberrypi:~ $ cms burn image get latest-lite
```

TODO: fill out the rest

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
SDCrad

## External Links

Have source code somewhere else, or a homepage?

How about a thank you link to the project that inspired you?

    Select Network

Add More Links

## Team

* Gregor von Laszewski
* Richard Otten
* Anthony Orlowski

You need to craete an account on hackaday.io, i need the account name.

## Feed

Do you want this update to show up in the feed?

Yes

Show update in feed

