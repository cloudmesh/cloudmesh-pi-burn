from cloudmesh.burn.image import Image
import os

i = Image()

os.system("touch ~/.cloudmesh/cmburn/images/junk.img")
os.system("touch ~/.cloudmesh/cmburn/images/junk.zip")

r = i.ls()
print (r)

r = i.clear()

print (r)
