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

        "volume" : line[0:13].replace("Volume", "").strip(),
        "drive"  : line[13:18].strip(),
        "label"  : line[18:31].strip(),
        "fs"     : line[31:38].strip(),
        "type"   : line[38:50].strip(),
        "size"   : line[50:59].strip(),
        "status" : line[59:70].strip(),

    }
    info.append(data)
print(info)

print(Printer.write(info, order=["volume","drive", "fs", "label", "size"]))




