Cloudmesh Raspberry Pi Mass Image Burner.
Usage:
  cm-burn create [--image=IMAGE]
                 [--group=GROUP]
                 [--names=HOSTS]
                 [--ips=IPS]
                 [--key=PUBLICKEY]
                 [--ssid=SSID]
                 [--psk=PSK]
                 [--domain=DOMAIN]
                 [--bootdrive=BOOTDRIVE]
                 [--rootdrive=ROOTDRIVE]
                 [-n --dry-run]
                 [-i --interactive]
  cm-burn ls [-ni]
  cm-burn rm IMAGE [-ni]
  cm-burn get [URL]
  cm-burn update
  cm-burn check install
  cm-burn hostname [HOSTNAME] [-ni]
  cm-burn ssh [PUBLICKEY] [-ni]
  cm-burn ip IPADDRESS [--domain=DOMAIN] [-ni]
  cm-burn wifi SSID [PASSWD] [-ni]
  cm-burn info [-ni]
  cm-burn image [--image=IMAGE]
                [--device=DEVICE]
                [-ni]
  cm-burn (-h | --help)
  cm-burn --version

Options:
  -h --help         Show this screen.
  -n --dry-run      Show output of commands but don't execute them
  -i --interactive  Confirm each change before doing it
  --version         Show version.
  --key=KEY         the path of the public key [default: ~/.ssh/id_rsa.pub].
  --ips=IPS         the IPs in hostlist format
  --image=IMAGE     the image [default: 2019-09-26-raspbian-buster.img]


Previously [default: 2018-06-27-raspbian-stretch.img]
Other images can be found at

https://downloads.raspberrypi.org/raspbian/images/

Files:
  This is not fully thought through and needs to be documented
  ~/.cloudmesh/images
  ~/.cloudmesh/inventory
  Location where the images will be stored for reuse

BUG:
  bootdrive and rootdrive will be removed in a future release as they are self
  discoverable

Description:
  cm-burn
  cm-burn create [--image=IMAGE]
                 [--group=GROUP]
                 [--names=HOSTS]
                 [--ip=IPS]
                 [--key=PUBLICKEY]
                 [--ssid=SSID]
                 [--psk=PSK]
                 [--bootdrive=BOOTDRIVE]
                 [--rootdrive=ROOTDRIVE]
  cm-burn update
        updates the downloaded images if new once are available
  cm-burn ls
        lists the downloaded images
  cm-burn rm IMAGE
        remove the image
  cm-burn get URL
        downloads the image at the given URL
  cm-burn get jessie
        abbreviation to download a specific version of an image.
        Identify what would be useful.
  cm-burn hostname HOSTNAME
        writes the HOSTNAME as hostname on the currently inserted SD Card
  cm-burn hostname
        reads the hostname form the current SD card

Example:
  cm-burn create --group=red --names=red[5-6] --ip=192.168.1.[5-6]
