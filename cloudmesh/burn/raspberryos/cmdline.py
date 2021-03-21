import textwrap

class Cmdline:

    def __init__(self):
        self.script = " ".join(textwrap.dedent("""
        console=serial0,115200
        console=tty1
        root=PARTUUID=904a3764-02
        rootfstype=ext4
        elevator=deadline
        fsck.repair=yes
        rootwait
        quiet
        init=/usr/lib/raspi-config/init_resize.sh
        splash
        plymouth.ignore-serial-consoles
        systemd.run=/boot/firstrun.sh
        systemd.run_success_action=reboot
        systemd.unit=kernel-command-line.target
        """).splitlines()).strip()

    def get(self):
        return self.script
