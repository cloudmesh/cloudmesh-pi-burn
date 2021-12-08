## Recommendations:

3. Old hackaday,opensource, and medium tutorials can be deleted or modified with a note at the top pointing them to the three up-to-date pi-planet tutorials:
       https://cloudmesh.github.io/pi/tutorial/raspberry-burn/ (linux,mac)
       https://cloudmesh.github.io/pi/tutorial/ubuntu-burn/ (linux, max)
       https://cloudmesh.github.io/pi/tutorial/raspberry-burn-windows/ (windows)
       
4. Replace most of the out-of-date pi-burn Github README with links to the up-to-date pi-planet tutorials. https://github.com/cloudmesh/cloudmesh-pi-burn/blob/main/README.md 

## Working Pi Burning Tutorials:

Burning a set of pre-configured Raspberry OS cards for Raspberry Pis with Wifi Access

- https://cloudmesh.github.io/pi/tutorial/raspberry-burn/

Burning a set of Ubuntu Server Cards for Raspberry Pis with Internet Access

- https://cloudmesh.github.io/pi/tutorial/ubuntu-burn/

DRAFT: Burning a pre-configured RaspberryOS Cluster on Windows 10

- https://cloudmesh.github.io/pi/tutorial/raspberry-burn-windows/
- NOTE: Works for raspi OS only

Burning a set of pre-configured SD cards with a GUI for Raspberry Pis with Wifi Access

- https://cloudmesh.github.io/pi/tutorial/gui-burn/
- NOTE: Based only on code inspection I expect this to still work, or be easiyly fixed.

## FIX Prepared Burning Tutorials:

### Opensource.com

Rapidly configure SD cards for your Raspberry Pi cluster
- https://opensource.com/article/21/3/raspberry-pi-cluster
- STATUS: DEFUNCT
- Expected BURNER OS: Linux and Mac
- REASON: uses `cms burn cluster...` command which is out of date 

### Hackaday.io

Easy Raspberry PI Cluster Setup with Cloudmesh from MacOS
- https://hackaday.io/project/177904-headless-rasbery-pi-cluster-from-macs/details
- STATUS: DEFUNCT
- Expected BURNER OS: Mac
- REASON: uses `cms burn cluster...` command which is out of date

### Medium.com

Easy Raspberry PI Cluster Setup with Cloudmesh from MacOS
- https://laszewski.medium.com/easy-raspberry-pi-cluster-setup-with-cloudmesh-from-macos-e160ac848bf
- STATUS: DEFUNCT
- Expected BURNER OS: Mac
- REASON: uses `cms burn cluster...` command which is out of date

### Github.com

README.md
- https://github.com/cloudmesh/cloudmesh-pi-burn
- STATUS: DEFUNCT
- Expected BURNER OS: Raspberry Pi
- REASON: uses `cms burn cluster...` command which is out of date. Also has out of date instructions for Mac OS and Linux in the FAQ.


All of these tutorials are mostly out of date because of the older burn command insturctions used. They have the same correction, they needs to use `cms burn raspberry` or `cms burn ubuntu` as described in our up-to-date pi-planet tuts:
     https://cloudmesh.github.io/pi/tutorial/raspberry-burn/ (linux,mac)
     https://cloudmesh.github.io/pi/tutorial/ubuntu-burn/ (linux, max)
     https://cloudmesh.github.io/pi/tutorial/raspberry-burn-windows/ (windows)
     

## NO FIX Prepared Burning Tutorials:

### Hackaday.io

Preconfigured SDCards for Raspberry Pi Clusters
- https://hackaday.io/project/177874-preconfigured-sdcards-for-raspberry-pi-clusters
- STATUS: DEFUNCT
- Expected BURNER OS: Linux and Mac, also provides manager pi imaging instructions to burn from Pi
- REASON: uses `cms burn create..` which is out of date

### Medium.com

Easy Raspberry PI Cluster Setup with Cloudmesh SDCard Burner
- https://laszewski.medium.com/easy-raspberry-pi-cluster-setup-with-cloudmesh-sdcard-burner-a2035dfea22
- STATUS: DEFUNCT
- Expected BURNER OS: Linux and Mac, also provides manager pi imaging instructions to burn from Pi
- REASON: uses `cms burn create..` which is out of date

## Removed Pi Burning Tutorials:

### Pi-planet.org

Easy Raspberry PI Cluster Setup with Cloudmesh from MacOS
- https://cloudmesh.github.io/pi/tutorial/sdcard-burn-pi-headless/
- STATUS: DEFUNCT
- Expected BURNER OS: Mac
- REASON: uses `cms burn cluster...` command which is out of date

Easy Raspberry PI Cluster Setup with Cloudmesh SDCard Burner
- https://cloudmesh.github.io/pi/tutorial/sdcard-burn-pi-as-burner/
- STATUS: DEFUNCT
- Expected BURNER OS: Linux and Mac, also provides manager pi imaging instructions to burn from Pi
- REASON: uses `cms burn create..` which is out of date
