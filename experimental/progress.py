#!/usr/bin/env python

import PySimpleGUI as sg
import sys

layout = [[sg.Text('Cloudmesh Burn Progress')],
          [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar')],
          [sg.Cancel()]]

window = sg.Window('Cloudmesh Burn Progress', layout)
progress_bar = window['progressbar']

i = 0
while True:
    line = sys.stdin.readline()
    try:
        i = int(line)
    except Exception as e:
        break

    event, values = window.read(timeout=10)
    if event == 'Cancel'  or event == sg.WIN_CLOSED:
        break
    progress_bar.UpdateBar(i + 1)

window.close()
