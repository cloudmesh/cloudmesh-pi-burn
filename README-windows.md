```
DISKPART> LIST VOLUME

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 0     F                       DVD-ROM         0 B  No Media
  Volume 1         BDEDrive     NTFS   Partition   1024 MB  Healthy
  Volume 2     C   OSDisk       NTFS   Partition    463 GB  Healthy    Boot
  Volume 3                      FAT32  Partition    512 MB  Healthy    System
  Volume 4                      NTFS   Partition    496 MB  Healthy    Hidden
  Volume 5     D   UNTITLED     exFAT  Removable     59 GB  Healthy

DISKPART> list disk

  Disk ###  Status         Size     Free     Dyn  Gpt
  --------  -------------  -------  -------  ---  ---
  Disk 0    Online          465 GB  1024 KB        *
  Disk 1    Online           59 GB      0 B

DISKPART> list volume

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 0     F                       DVD-ROM         0 B  No Media
  Volume 1         BDEDrive     NTFS   Partition   1024 MB  Healthy
  Volume 2     C   OSDisk       NTFS   Partition    463 GB  Healthy    Boot
  Volume 3                      FAT32  Partition    512 MB  Healthy    System
  Volume 4                      NTFS   Partition    496 MB  Healthy    Hidden
  Volume 5     D   system-boot  FAT32  Removable    256 MB  Healthy

DISKPART> list disk

  Disk ###  Status         Size     Free     Dyn  Gpt
  --------  -------------  -------  -------  ---  ---
  Disk 0    Online          465 GB  1024 KB        *
  Disk 1    Online           59 GB      0 B

DISKPART> list volume

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 0     F                       DVD-ROM         0 B  No Media
  Volume 1         BDEDrive     NTFS   Partition   1024 MB  Healthy
  Volume 2     C   OSDisk       NTFS   Partition    463 GB  Healthy    Boot
  Volume 3                      FAT32  Partition    512 MB  Healthy    System
  Volume 4                      NTFS   Partition    496 MB  Healthy    Hidden
  Volume 5     D   boot         FAT32  Removable    256 MB  Healthy

DISKPART> list disk

  Disk ###  Status         Size     Free     Dyn  Gpt
  --------  -------------  -------  -------  ---  ---
  Disk 0    Online          465 GB  1024 KB        *
  Disk 1    Online           59 GB    51 GB

DISKPART>


DISKPART> select disk 3

Disk 3 is now the selected disk.

DISKPART> select volume 5

Volume 5 is the selected volume.

DISKPART> format fs=fat32 quick

  100 percent completed

DiskPart successfully formatted the volume.

DISKPART> list disk

  Disk ###  Status         Size     Free     Dyn  Gpt
  --------  -------------  -------  -------  ---  ---
  Disk 0    Online          931 GB    12 MB        *
  Disk 1    No Media           0 B      0 B
  Disk 2    No Media           0 B      0 B
* Disk 3    Online           59 GB  3072 KB

DISKPART> list disk volume

The arguments specified for this command are not valid.
For more information on the command type: HELP LIST DISK

DISKPART> list volume

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 0     C   OS           NTFS   Partition    930 GB  Healthy    Boot
  Volume 1         ESP          FAT32  Partition    500 MB  Healthy    System
  Volume 2                      NTFS   Partition    851 MB  Healthy    Hidden
  Volume 3     D                       Removable       0 B  No Media
  Volume 4     E                       Removable       0 B  No Media
* Volume 5     F                FAT32  Removable    256 MB  Healthy

```
