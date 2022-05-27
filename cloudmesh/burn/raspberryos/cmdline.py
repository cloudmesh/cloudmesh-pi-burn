import textwrap
import io
import os

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import path_expand


class Cmdline:

    def __init__(self):

        self.template = \
            {
                "lite": "console=serial0,115200 " +
                        "console=tty1 " +
                        "root=PARTUUID={partuuid} " +
                        "rootfstype=ext4 " +
                        "elevator=deadline " +
                        "fsck.repair=yes " +
                        "rootwait " +
                        "quiet " +
                        "init=/usr/lib/raspi-config/init_resize.sh " +
                        "systemd.run=/boot/firstrun.sh " +
                        "systemd.run_success_action=reboot " +
                        "systemd.unit=kernel-command-line.target",
                "full": "console=serial0,115200 " +
                        "console=tty1 " +
                        "root=PARTUUID={partuuid} " +
                        "rootfstype=ext4 " +
                        "elevator=deadline " +
                        "fsck.repair=yes " +
                        "rootwait " +
                        "quiet " +
                        "init=/usr/lib/raspi-config/init_resize.sh " +
                        "splash " +
                        "plymouth.ignore-serial-consoles " +
                        "systemd.run=/boot/firstrun.sh " +
                        "systemd.run_success_action=reboot " +
                        "systemd.unit=kernel-command-line.target"
            }
        self.template["lite-32"] = self.template["lite"]
        self.template["full-32"] = self.template["full"]
        self.template["lite-64"] = self.template["lite"]
        self.template["full-64"] = self.template["full"]

        # Commented out above since we should just append
        # the lines below to the existing cmdline.txt since
        # root PARTUUID may vary

        # self.cmdline will be populated when .read() is called
        self.cmdline = None
        # the space-separated values to add to the end of cmdline
        # self.script = " ".join(textwrap.dedent("""
        # splash
        # plymouth.ignore-serial-consoles
        # systemd.run=/boot/firstrun.sh
        # systemd.run_success_action=reboot
        # systemd.unit=kernel-command-line.target
        # """).splitlines()).strip()
        self.script = None

    def update(self, filename, version="lite"):
        """
        NEW:
        * [ ] TODO: test on windows
        * [ ] TODO: test on Linux
        * [ ] TODO: test on macOS

        filename: the filename to be changed on the sdkard reade.
            On windows you need the driveletter + "cmdline.txt"
        """
        self.cmdline = readfile(filename).split(" ")

        for partuuid in self.cmdline:
            if partuuid.startswith("root=PARTUUID="):
                partuuid = partuuid.split("root=PARTUUID=")[1].strip()
                break
        self.script = self.template[version].format(partuuid=partuuid)

        self.writefile(filename, self.script)

    def writefile(self, filename, content):
        """
        NEW:
        * [ ] TODO: test on windows
        * [ ] TODO: test on Linux
        * [ ] TODO: test on macOS

        writes the content into the file
        :param filename: the filename to be changed on the sdcard cmdline.txt.
                         On Windows it must start with the drive letter such as "f:/"
        :param content: the content
        :return:
        """
        outfile = io.open(path_expand(filename), 'w', newline='\n')
        outfile.write(content)
        outfile.flush()
        os.fsync(outfile)

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
