@windows_not_supported
def detect(self):
    """
    Detects if a USB card writer can be found. and just prints the result
    """
    # Clear dmesg table so that info doesn't get confused with previous detects
    self.system('sudo dmesg -c')
    banner("Detecting USB Card Writers(s)")

    print("Make sure the USB Writers(s) is removed ...")
    if not yn_choice("Is the writer(s) removed?"):
        sys.exit()
    usb_out = set(Shell.execute("lsusb").splitlines())
    print("Now plug in the Writer(s) ...")
    if not yn_choice("Is the writer(s) plugged in?"):
        sys.exit()
    usb_in = set(Shell.execute("lsusb").splitlines())

    writer = usb_in - usb_out
    if len(writer) == 0:
        print(
            "ERROR: we did not detect the device, make sure it is plugged.")
        sys.exit()
    else:
        banner("Detected Card Writers")

        print("\n".join(writer))
        print()
