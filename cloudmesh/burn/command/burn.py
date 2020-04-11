from cloudmesh.burn.interprete import interprete
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.debug import VERBOSE


class BurnCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_burn(self, args, arguments):
        """
        ::

            Usage:
              burn execute network list [--ip=IP] [--used]
              burn network address
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

              >      +------------+---------------+----------+-----------+
              >      | Name       | IP            | Status   | Latency   |
              >      |------------+---------------+----------+-----------|
              >      | Router     | 192.168.1.1   | up       | 0.0092s   |
              >      | iPhone     | 192.168.1.4   | up       | 0.061s    |
              >      | red01      | 192.168.1.46  | up       | 0.0077s   |
              >      | laptop     | 192.168.1.78  | up       | 0.058s    |
              >      | unkown     | 192.168.1.126 | up       | 0.14s     |
              >      | red03      | 192.168.1.158 | up       | 0.0037s   |
              >      | red02      | 192.168.1.199 | up       | 0.0046s   |
              >      | red        | 192.168.1.249 | up       | 0.00021s  |
              >      +------------+----------------+----------+-----------+

                cms burn network list [--used]

                    Lists the used ip addresses as a comma separated parameter
                    list

                       192.168.50.1,192.168.50.4,...

                cms burn network address

                    Lists the own network address

              >      +---------+----------------+----------------+
              >      | Label   | Local          | Broadcast      |
              >      |---------+----------------+----------------|
              >      | wlan0   | 192.168.1.12   | 192.168.1.255  |
              >      +---------+----------------+----------------+

            Example:
              > cms burn create --image=2019-09-26-raspbian-buster-lite \
              >                --device=/dev/mmcblk0
              >                --hostname=red[5-7] \
              >                --ipaddr=192.168.1.[5-7] \
              >                --sshkey=id_rsa
              > cms burn image get latest
              > cms burn image get https://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-10-11/2018-10-09-raspbian-stretch-lite.zip
              > cms burn image delete 2019-09-26-raspbian-buster-lite

        """

        map_parameters(arguments,
                       "refresh",
                       "image",
                       "device",
                       "hostname",
                       "ipaddr",
                       "sshkey",
                       "blocksize",
                       "dryrun",
                       "passwd",
                       "ssid",
                       "wifipassword",
                       "version")
        arguments.FORMAT = arguments["--format"]

        VERBOSE(arguments)

        return interprete(arguments)
