# dd bs=4M if=/c/Users/venkata/.cloudmesh/cmburn/images/2021-03-04-raspios-buster-armhf-lite.img of=/dev/sdb conv=fdatasync status=progress
#     command = f"sudo dd if={image_path} bs={blocksize} |" \
#               f' tqdm --bytes --total {size} --ncols 80 |' \
#               f" sudo dd of={device} bs={blocksize}"
# else:
#     # command = f"sudo dd if={image_path} of={device} bs={blocksize} status=progress conv=fsync"
#     command = f"sudo dd if={image_path} bs={blocksize} oflag=direct |" \
#               f' tqdm --bytes --total {size} --ncols 80 |' \
#               f" sudo dd of={device} bs={blocksize} iflag=fullblock " \
#               f"oflag=direct conv=fsync"

DVC_IGNORE_ISATTY=true
FILE=/c/Users/blue/.cloudmesh/cmburn/images/2021-05-07-raspios-buster-armhf-lite.img
SIZE=`stat --print="%s" $FILE`
DEV=/dev/sdc

echo $SIZE
echo $FILE

dd bs=4M if=$FILE oflag=direct |
   tqdm --desc="format" --bytes --total=$SIZE --ncols=80 | \
   dd bs=4M of=$DEV conv=fsync oflag=direct iflag=fullblock

#dd bs=4M if=$FILE oflag=direct  | dd of=$DEV bs=4M status=progress conv=fsync oflag=direct iflag=fullblock
