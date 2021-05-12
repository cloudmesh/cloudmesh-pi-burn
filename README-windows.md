'''
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
'''
