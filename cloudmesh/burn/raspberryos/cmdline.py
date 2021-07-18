import textwrap

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from cloudmesh.burn.util import os_is_windows

class Cmdline:

    def __init__(self):
        # self.script = " ".join(textwrap.dedent("""
        # console=serial0,115200
        # console=tty1
        # root=PARTUUID=904a3764-02
        # rootfstype=ext4
        # elevator=deadline
        # fsck.repair=yes
        # rootwait
        # quiet
        # init=/usr/lib/raspi-config/init_resize.sh
        # splash
        # plymouth.ignore-serial-consoles
        # systemd.run=/boot/firstrun.sh
        # systemd.run_success_action=reboot
        # systemd.unit=kernel-command-line.target
        # """).splitlines()).strip()

        # Commented out above since we should just append
        # the lines below to the existing cmdline.txt since
        # root PARTUUID may vary

        # self.cmdline will be populated when .read() is called
        self.cmdline = None
        # the space-separated values to add to the end of cmdline
        self.script = " ".join(textwrap.dedent("""
        splash
        plymouth.ignore-serial-consoles
        systemd.run=/boot/firstrun.sh
        systemd.run_success_action=reboot
        systemd.unit=kernel-command-line.target
        """).splitlines()).strip()

    def read(self, filename=None):
        """
        Read a pre-existing cmdline.txt and store it
        """

        if filename is None:
            raise Exception("read called with no filename")

        self.cmdline = readfile(filename).strip()

    def write(self, filename=None):
        """
        Write the cmdline config to the specified filename
        """
        if self.cmdline is None:
            # Cmdline varies by burn
            raise Exception("Please read a pre-existing cmdline.txt first")
        if filename is None:
            raise Exception("write called with no filename")
        if os_is_windows():
            Shell.run(f'echo "{self.cmdline} {self.script}" | tee {filename}')
        else:
            Shell.run(f'echo "{self.cmdline} {self.script}" | sudo tee {filename}')

    def get(self):
        """
        Return the proper cmdline with the necessary commands
        """
        if self.cmdline is None:
            print("Using example cmdline.txt. Not safe for usage. For testing only")
            self.cmdline = self._example()

        return self.cmdline + self.script

    def _example(self):
        """
        An example cmdline.txt for testing purposes
        """
        return " ".join(textwrap.dedent("""
        console=serial0,115200
        console=tty1
        root=PARTUUID=9730496b-02
        rootfstype=ext4
        elevator=deadline
        fsck.repair=yes
        rootwait
        quiet
        init=/usr/lib/raspi-config/init_resize.sh
        """).splitlines()).strip()

        # root=PARTUUID=904a3764-02

