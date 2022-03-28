#!/usr/bin/env python
# coding: utf-8

# In[1]:
import sys

# from cloudmesh.burn.windowssdcard import WindowsSDCard
import time
from cloudmesh.burn.util import os_is_windows

import string
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile as common_writefile
from cloudmesh.common.util import readfile as common_readfile
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import path_expand
from pathlib import Path
import os
import sys
import string
import subprocess
import re
from pathlib import Path

# In[2]:

class WindowsSDCard:
    tmp = "tmp.txt"

    def __init__(self):
        pass

    def assign_drive(self,volume=None,drive=None):
        if drive is None:
            drive = self.guess_drive()
        result = self.diskpart(f"select volume {volume}\nassign letter={drive}")
        return result

    def info(self):

        b = self.diskpart("list volume")
        volumes = self.process_volumes_text(text=b)

        d = volumes[0]["drive"]
        v = volumes[0]["volume"]

        drive_assigned = d != ""
        if not drive_assigned:
            pass
            #assign the drive letter
            self.assign_drive(volume=v,drive)
            #find more info for sdb
            #self.remove_letter()

        else:
            pass
            #find more info


        return volumes

    def process_volumes_text(self,text=None):
        if text is None:
            Console.error("No volume info provided")
        else:
            lines = text.splitlines()
            result = []
            for line in lines:
                if "Removable" in line and "Healthy" in line:
                    result.append(line)

            content = []
            for line in result:
                data = {

                    "volume": line[0:13].replace("Volume", "").strip(),
                    "drive": line[13:18].strip(),
                    "label": line[18:31].strip(),
                    "fs": line[31:38].strip(),
                    "type": line[38:50].strip(),
                    "size": line[50:59].strip(),
                    "status": line[59:70].strip(),
                    "info": line[70:].strip()

                }
                content.append(data)

            return content


    def diskpart(self, command):
        _diskpart = Path("C:/Windows/system32/diskpart.exe")
        common_writefile(WindowsSDCard.tmp, f"{command}\nexit")
        b = Shell.run(f"{_diskpart} /s {WindowsSDCard.tmp}")
        WindowsSDCard.clean()
        return b

    @staticmethod
    def clean():
        os.remove(WindowsSDCard.tmp)

card = WindowsSDCard()
print(card.info())

'''card = WindowsSDCard()
def Info():
    content = card.info()
    content2 = card.device_info()
    print(content)
    print(content2)


# In[3]:


# card.inject(volume="5")


# In[4]:


# card.unmount(drive="D")


# In[5]:


# card.format_drive(drive="D")


# In[6]:


# card.assign_drive(volume="5")


# User buys card
# cards are empty and formatted with fat32
# 
# we need to put the card in
# test if the letter is there (table with all three values in there vol drive device)
# we need to format the card no matter what is on there

# In[7]:


content = card.info()
print(content)
d = content[0]["drive"]
v = content[0]["volume"]
l = content[0]["label"]
if d == "":
    drive = card.guess_drive()
    card.assign_drive(volume=v,drive=drive)
content = card.info()
print(content)


# In[8]:


card.diskpart(command=f"select volume {v}\nonline volume")
#card.mount(label=l)


# In[9]:


content = card.info()
print(content)


# In[10]:


device = card.filter_info(card.device_info(),{'win-mounts':d})
success = card.format_drive(drive=d)
if not success:
    print("Exited with Error ++++++++++++++++++++")
    sys.exit()

# we need to unmount the card so we can burn (which removes drive letter)  

# In[11]:


device = card.filter_info(card.device_info(),{'win-mounts':d})
Info()
print(device)
dev = "/dev/" + device[0]["name"][0:3]
print(dev)


# In[12]:


card.unmount(drive=d)
Info()


# In[18]:


image_path = "/c/Users/venkata/.cloudmesh/cmburn/images/2021-03-04-raspios-buster-armhf-lite.img"
os.system(f"ls {image_path}")
# card.dd(image_path=image_path,device=dev)
command = f"dd bs=4M if={image_path} oflag=direct of={dev} conv=fdatasync iflag=fullblock status=progress"
print(command)
os.system(command)
print("done")


# In[16]:




# We need to do dd burn with image_path  
# ?
# We want to test if card has been properly written  
# We eject the card  
# We take the card out  
# 
# release drive letter  
# repeat for second card  

# In[ ]:





# In[ ]:


card.device_info()


# In[ ]:


card.info()

'''
