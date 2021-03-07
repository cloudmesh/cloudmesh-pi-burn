@windows_not_supported
def info(self,
         print_os=True,
         print_fdisk=True,
         print_stdout=True,
         output="table"):
    """
    Finds out information about USB devices

    TODO: should we rename print_stdout to debug? seems more in
          line with cloudmesh

    :param print_os:
    :type print_os:
    :param print_fdisk:
    :type print_fdisk:
    :param print_stdout: if set to True prints debug information
    :type print_stdout: bool
    :param output:
    :type output:
    :return: dict with details about the devices
    :rtype: dict
    """

    if print_os and print_stdout:
        if os_is_pi():
            banner("This is  Raspberry PI")
        elif os_is_mac():
            banner("This is Mac")
        elif os_is_windows():
            banner("This is a Windows Computer")
        elif os_is_linux():
            banner("This is a Linux Computer")
        else:
            Console.error("unkown OS")
            sys.exit(1)

    if os_is_pi() and print_fdisk and print_stdout:
        result = USB.fdisk("/dev/mmcblk0")
        if print_stdout:
            banner("Operating System SD Card")
            print(result)

    details = USB.get_from_usb()

    if print_stdout and details is not None:
        banner("USB Device Probe")
        print(Printer.write(
            details,
            order=["address",
                   "bus",
                   "idVendor",
                   "idProduct",
                   "hVendor",
                   "hProduct",
                   "iManufacturer",
                   "iSerialNumber",
                   "usbVersion",
                   "comment"],
            header=["Adr.",
                    "bus",
                    "Vendor",
                    "Prod.",
                    "H Vendor",
                    "H Prod.",
                    "Man.",
                    "Ser.Num.",
                    "USB Ver.",
                    "Comment"],
            output=output)
        )

    # devices = USB.get_devices()

    # banner("Devices found")

    # print ('\n'.join(sorted(devices)))

    if os_is_mac():

        names = USB.get_dev_from_diskutil()

        details = USB.get_from_diskutil()
    else:
        details = USB.get_from_dmesg()

    if print_stdout:
        banner("SD Cards Found")

        if os_is_mac():
            print("We found the follwing cards:")
            print("  - /dev/" + "\n  - /dev/".join(names))
            print()
            print("We found the follong file systems on these disks:")
            print()

        print(Printer.write(details,
                            order=[
                                "dev",
                                "info",
                                "formatted",
                                "size",
                                "active",
                                "readable",
                                "empty",
                                "direct-access",
                                "removable",
                                "writeable"],
                            header=[
                                "Path",
                                "Info",
                                "Formatted",
                                "Size",
                                "Plugged-in",
                                "Readable",
                                "Empty",
                                "Access",
                                "Removable",
                                "Writeable"],
                            output=output)
              )

        # lsusb = USB.get_from_lsusb()
        # from pprint import pprint
        # pprint (lsusb)

        # endors = USB.get_vendor()
        # print(vendors)

        # udev = subprocess.getoutput("udevadm info -a -p  $(udevadm info -q path -n /dev/sda)")
        #
        # attributes = ["vendor","model", "model", "version", "manufacturer",
        #     "idProduct", "idVendor"]
        # for line in udev.splitlines():
        #    if any(word in line for word in attributes):
        #        print(line)

    if print_stdout:

        if os_is_linux():
            card = SDCard()
            m = card.ls()

            banner("Mount points")
            if len(m) != 0:
                print(Printer.write(m,
                                    order=["name", "path", "type", "device", "parameters"],
                                    header=["Name", "Path", "Type", "Device", "Parameters"],
                                    output=output))
            else:
                Console.warning("No mount points found. Use cms burn mount")
                print()

    # Convert details into a dict where the key for each entry is the device
    details = {detail['dev']: detail for detail in details}

    return details
