from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile
from cloudmesh.common.util import yn_choice

class USB:
    @staticmethod
    def info():
        print("Prints the table of information about devices on the  usb info")

class SdCard:

   # Take a look at Gregor's SDCard init method
    def format(disknumber):
        print(f"format :{disknumber}")

    def mount(disknumber, drivenumber):
        pass

    def unmount(disknumber, drivenumber):
        pass

    def write(disknumber, drivenumber):
        pass

writefile("s.txt", "list disk")
r = Shell.run("diskpart /s s.txt").splitlines()[8:]

for line in r:
    line = line.strip()
    if "*" not in line:
        line = line.replace("No Media", "NoMedia")
        line = line.replace("Disk ", "")
        line = ' '.join(line.split())
        num, kind, size, unit, unused1, unused2  = line.split(" ")
        size = int(size)

        if unit == "GB" and (size > 7 and size < 128):
            print(num)

if yn_choice (f"Would you like to contine burning on disk {num}"):
    print("Great")





