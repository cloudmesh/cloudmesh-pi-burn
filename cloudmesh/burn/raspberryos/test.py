#
# python cloudmesh/burn/raspberryos/test.py
#
from cloudmesh.burn.raspberryos.cmdline import Cmdline
from cloudmesh.burn.raspberryos.runfirst import Runfirst
from cloudmesh.common.parameter import Parameter

cmsline = Cmdline()

print (cmsline.get())
print()


names = Parameter.expand("red,red[0-1]")
ips = Parameter.expand("10.0.0.[1-3]")

runfirst = Runfirst()
runfirst.set_key()
runfirst.set_wifi("abc", "123")
runfirst.set_locale()
runfirst.set_hostname("name")
runfirst.set_hosts(names, ips)

runfirst.info()

print(runfirst.get())
