## On macOS

mount | fgrep " /Volumes"
/dev/disk2s1 on /Volumes/UNTITLED (msdos, local, nodev, nosuid, noowners)

df -H | fgrep " /Volumes"
/dev/disk2s1      32G   1.9M    32G     1%       0           0  100%   /Volumes/UNTITLED


diskutil list external
/dev/disk2 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:     FDisk_partition_scheme                        *31.9 GB    disk2
   1:                 DOS_FAT_32 ⁨UNTITLED⁩                31.9 GB    disk2s1

diskutil list external -plist
Could not find disk for -plist
grey@gamera cm % diskutil -plist list external       
diskutil: did not recognize verb "-plist"; type "diskutil" for a list
grey@gamera cm % diskutil list -plist external 
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>AllDisks</key>
	<array>
		<string>disk2</string>
		<string>disk2s1</string>
	</array>
	<key>AllDisksAndPartitions</key>
	<array>
		<dict>
			<key>Content</key>
			<string>FDisk_partition_scheme</string>
			<key>DeviceIdentifier</key>
			<string>disk2</string>
			<key>OSInternal</key>
			<false/>
			<key>Partitions</key>
			<array>
				<dict>
					<key>Content</key>
					<string>DOS_FAT_32</string>
					<key>DeviceIdentifier</key>
					<string>disk2s1</string>
					<key>MountPoint</key>
					<string>/Volumes/UNTITLED</string>
					<key>Size</key>
					<integer>31913410560</integer>
					<key>VolumeName</key>
					<string>UNTITLED</string>
					<key>VolumeUUID</key>
					<string>38F4AF4D-37EF-33DD-AA53-0FFA97FCC8C3</string>
				</dict>
			</array>
			<key>Size</key>
			<integer>31914983424</integer>
		</dict>
	</array>
	<key>VolumesFromDisks</key>
	<array>
		<string>UNTITLED</string>
	</array>
	<key>WholeDisks</key>
	<array>
		<string>disk2</string>
	</array>
</dict>
</plist>


diskutil info disk2s1
   Device Identifier:         disk2s1
   Device Node:               /dev/disk2s1
   Whole:                     No
   Part of Whole:             disk2

   Volume Name:               UNTITLED
   Mounted:                   Yes
   Mount Point:               /Volumes/UNTITLED

   Partition Type:            DOS_FAT_32
   File System Personality:   MS-DOS FAT32
   Type (Bundle):             msdos
   Name (User Visible):       MS-DOS (FAT32)

   OS Can Be Installed:       No
   Media Type:                Generic
   Protocol:                  USB
   SMART Status:              Not Supported
   Volume UUID:               38F4AF4D-37EF-33DD-AA53-0FFA97FCC8C3
   Partition Offset:          1048576 Bytes (2048 512-Byte-Device-Blocks)

   Disk Size:                 31.9 GB (31913410560 Bytes) (exactly 62330880 512-Byte-Units)
   Device Block Size:         512 Bytes

   Volume Total Space:        31.9 GB (31897812992 Bytes) (exactly 62300416 512-Byte-Units)
   Volume Used Space:         1.9 MB (1900544 Bytes) (exactly 3712 512-Byte-Units) (0.0%)
   Volume Free Space:         31.9 GB (31895912448 Bytes) (exactly 62296704 512-Byte-Units) (100.0%)
   Allocation Block Size:     16384 Bytes

   Media OS Use Only:         No
   Media Read-Only:           No
   Volume Read-Only:          No

   Device Location:           External
   Removable Media:           Removable
   Media Removal:             Software-Activated

   Solid State:               Info not available
