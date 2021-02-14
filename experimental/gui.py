import PySimpleGUI as sg  # Part 1 - The import
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.Tabulate import Printer
from cloudmesh.burn.util import os_is_mac
from cloudmesh.burn.usb import USB
import oyaml as yaml

""""

Layout

Icon csentered

Burn on 

[ ] /dev/dev/disk2
[ ] /dev/dev/disk3    

Image: __________________

       [File Selector]

[x] Format

Manager:  _______________
Workers:  _______________

[Burn] [Cancel]

"""
logo = './cm-logo.png'

# TODO: we do teh device wrong for now as we want to show radio button

if os_is_mac():
    details = USB.get_from_diskutil()
else:
    details = USB.get_from_dmesg()

devices = yaml.safe_load(Printer.write(details,
                    order=[
                        "dev",
                        "info",
                        "formatted",
                        "size",
                        "active",
                        "readable",
                        "empty",
                        "direct-access",
                        "removable",
                        "writeable"],
                    header=[
                        "Path",
                        "Info",
                        "Formatted",
                        "Size",
                        "Plugged-in",
                        "Readable",
                        "Empty",
                        "Access",
                        "Removable",
                        "Writeable"],
                    output="yaml"))
layout = []
background = '#000000'

layout.append([sg.Button('',
                         button_color=(background,background),
                         image_filename=logo,
                         image_size=(30, 30),
                         image_subsample=2,
                         border_width=0,
                         key='LOGO')])

for device in devices:
    layout.append([sg.Radio(device['dev'], group_id="DEVICE"),
                   sg.Text(device["size"]),
                   sg.Text(device["info"]),
                   sg.Text(device["formatted"]),
                   ])

layout.append([sg.Text('Master'), sg.Input(default_text="red")])
layout.append([sg.Text('Workers'), sg.Input(default_text="red[01-02")])

layout.append([sg.Text('Image'), sg.Input(default_text="latest-lite")])
layout.append([sg.Text("Choose Image: "), sg.FileBrowse()])


layout.append([sg.Text('Continue'), sg.Button('Burn'), sg.Button('Cancel')])

window = sg.Window('Cloudmesh Pi Burn', layout)

event, values = window.read()

Console.ok(f"You entered: {values[0]}")

window.close()
