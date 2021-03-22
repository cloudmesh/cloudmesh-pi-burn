import os
import textwrap

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
        self.script = " ".join(textwrap.dedent("""
        splash
        plymouth.ignore-serial-consoles
        systemd.run=/boot/firstrun.sh 
        systemd.run_success_action=reboot
        systemd.unit=kernel-command-line.target
        """).splitlines()).strip()

    def read(self):
        pass

    def write(self, filename=None):
        if filename is None:
            raise Exception("write called with no filename")
        os.system(f'echo "{self.script}" | sudo tee {filename}')


    def get(self):
        return self.script
