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
dd bs=4M if=/c/Users/venkata/.cloudmesh/cmburn/images/2021-03-04-raspios-buster-armhf-lite.img oflag=direct | \
tqdm --bytes --total 68719441552 --ncols 80 | \
dd bs=4M of=/dev/sdb conv=fdatasync oflag=direct iflag=fullblock 
