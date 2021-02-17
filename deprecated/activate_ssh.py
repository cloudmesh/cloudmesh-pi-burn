# originally from burner.py


# IMPROVE
# ok osx
# @windows_not_supported
def activate_ssh(self, public_key, debug=False, interactive=False):
    """
    Sets the public key path and copies it to the SD card

    TODO: this has bugs as we have not yet thought about debug,
          interactive, yesno yesno we can take form cloudmesh.common

    BUG: this just raise a non implementation error

    :param public_key: the public key location
    :type public_key: str
    :param debug: if set to tru debug messages will be printed
    :type debug: bool
    :param interactive: set to tru if you like interactive mode
    :type interactive: bool
    :return: True if successful
    :rtype: bool
    """

    raise NotImplementedError

    # set the keypath
    self.keypath = public_key
    if debug:
        print(self.keypath)
    if not os.path.isfile(self.keypath):
        Console.error("key does not exist", self.keypath)
        sys.exit()

    if self.dryrun:
        print("DRY RUN - skipping:")
        print("Activate ssh authorized_keys pkey:{}".format(public_key))
        return
    elif interactive:
        if not yn_choice("About to write ssh config. Please confirm:"):
            return

    # activate ssh by creating an empty ssh file in the boot drive
    pathlib.Path(self.filename("/ssh")).touch()
    # Write the content of the ssh rsa to the authorized_keys file
    key = pathlib.Path(public_key).read_text()
    ssh_dir = self.filename("/home/pi/.ssh")
    print(ssh_dir)
    if not os.path.isdir(ssh_dir):
        os.makedirs(ssh_dir)
    auth_keys = ssh_dir / "authorized_keys"
    auth_keys.write_text(key)

    # We need to fix the permissions on the .ssh folder but it is hard to
    # get this working from a host OS because the host OS must have a user
    # and group with the same pid and gid as the raspberry pi OS. On the PI
    # the pi uid and gid are both 1000.

    # All of the following do not work on OS X:
    # execute("chown 1000:1000 {ssh_dir}".format(ssh_dir=ssh_dir))
    # shutil.chown(ssh_dir, user=1000, group=1000)
    # shutil.chown(ssh_dir, user=1000, group=1000)
    # execute("sudo chown 1000:1000 {ssh_dir}".format(ssh_dir=ssh_dir))

    # Changing the modification attributes does work, but we can just handle
    # this the same way as the previous chown issue for consistency.
    # os.chmod(ssh_dir, 0o700)
    # os.chmod(auth_keys, 0o600)

    # /etc/rc.local runs at boot with root permissions - since the file
    # already exists modifying it shouldn't change ownership or permissions
    # so it should run correctly. One lingering question is: should we clean
    # this up later?

    new_lines = textwrap.dedent('''
                # FIX298-START: Fix permissions for .ssh directory
                if [ -d "/home/pi/.ssh" ]; then
                    chown pi:pi /home/pi/.ssh
                    chmod 700 /home/pi/.ssh
                    if [ -f "/home/pi/.ssh/authorized_keys" ]; then
                        chown pi:pi /home/pi/.ssh/authorized_keys
                        chmod 600 /home/pi/.ssh/authorized_keys
                    fi
                fi
                # FIX298-END
                ''')
    rc_local = self.filename("/etc/rc.local")
    new_rc_local = ""
    already_updated = False
    with rc_local.open() as f:
        for line in f:
            if "FIX298" in line:
                already_updated = True
                break
            if line == "exit 0\n":
                new_rc_local += new_lines
                new_rc_local += line
            else:
                new_rc_local += line
    if not already_updated:
        with rc_local.open("w") as f:
            f.write(new_rc_local)
    self.disable_password_ssh()
