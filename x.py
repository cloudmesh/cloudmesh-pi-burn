from cloudmesh.common.Tabulate import Printer

script = '''

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 0     C   OS           NTFS   Partition    930 GB  Healthy    Boot
  Volume 1         ESP          FAT32  Partition    500 MB  Healthy    System
  Volume 2                      NTFS   Partition    851 MB  Healthy    Hidden
  Volume 3     D                       Removable       0 B  No Media
  Volume 4     E                       Removable       0 B  No Media
  Volume 5     F                FAT32  Removable    256 MB  Healthy
  Volume 6     F                FAT32  Removable    256 MB  Healthy

'''.strip()

lines = script.splitlines()
result = []
for line in lines:
    if "Removable" in line and "Healthy" in line:
        result.append(line)

info = []
for line in result:
    data = {

        "volume" : line[0:12].replace("Volume", "").strip(),
        "drive"    : line[12:17].strip(),
        "label"  : line[17:30].strip(),
        "fs"     : line[30:37].strip(),
        "type"   : line[37:49].strip(),
        "size"   : line[49:58].strip(),
        "status" : line[58:69].strip(),

    }
    info.append(data)
print(info)

print(Printer.write(info, order=["volume","drive", "fs", "label", "size"]))




