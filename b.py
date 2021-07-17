import os
from cloudmesh.common.util import path_expand

os.system("cms burn sdcard latest-lite --disk=4")
firstrun = path_expand("~/.cloudmesh/cmburn/firstrun.sh")
os.system(f"cp {firstrun} /f/")

#print (inventory)

