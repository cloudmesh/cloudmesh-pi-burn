import inspect
import os.path
import subprocess

import PySimpleGUI as sg
import oyaml as yaml
from cloudmesh.burn.usb import USB
from cloudmesh.burn.util import os_is_mac
from cloudmesh.common.Host import Host
from cloudmesh.common.Tabulate import Printer
# import PySimpleGUIWx as sg
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.sudo import Sudo
from cloudmesh.common.Shell import Shell


def _execute(command):
    print(".", end="", flush=True)
    os.system(f"{command} >> burn-gui.log")

def image(name):
    with open(path_expand(name), 'rb') as file:
        return file.read()

class Gui:

    def __init__(self, hostnames=None, ips=None):

        self.hostnames_str = hostnames
        self.ips_str = ips
        self.hostnames = hostnames = hostnames or "red,red[01-02]"
        self.ips = ips = ips or "10.0.0.[1-3]"

        hostnames= Parameter.expand(hostnames)
        manager, workers = Host.get_hostnames(hostnames)

        if workers is None:
            n = 1
        else:
            n = len(workers) + 1
        if ips is None:
            ips = Parameter.expand(f"10.1.1.[1-{n}]")
        else:
            ips = Parameter.expand(ips)

        # cluster_hosts = tuple(zip(ips, hostnames))

        self.key = path_expand("~/.ssh/id_rsa.pub")

        banner("Parameters", figlet=True)

        print("Manager:      ", manager)
        print("Workers:      ", workers)
        print("IPS:          ", ips)
        print("Key:          ", self.key)

        self.manager = manager
        self.workers = workers
        self.ips = ips

        self.create_diag(self.manager)


        self.load_data()
        self.layout()

    def burn(self, kind, hostname):
        #subprocess.run("cms burn cluster --device=/dev/disk4s1 --hostname=red,red00[1-2] --ssid=Router23165")

        if hostname == 'red':
            # Burn manager
            pass
        else:
            # Burn worker
            pass

        return

    def load_data(self):

        self.background = '#64778d'

        if os_is_mac():
            self.details = USB.get_from_diskutil()
        else:
            self.details = USB.get_from_dmesg()

        self.devices = yaml.safe_load(Printer.write(self.details,
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


    def layout(self):

        def line(msg):
            title = f'__ {msg} '
            title = title.ljust(120, '_')

            burn_layout.append([sg.Text(title)])

        width = 10
        location = os.path.dirname(os.path.abspath(inspect.getsourcefile(Gui)))

        print(location)
        print("======")

        cm_logo = f'{location}/images/cm-logo-100.png'
        pi_logo = f'{location}/images/raspberry-logo-white-100.png'

        burn_layout = [
            [sg.T('')]
        ]

        rack_file = f"~/.cloudmesh/gui/{self.manager}-rack.png"
        net_file = f"~/.cloudmesh/gui/{self.manager}-net.png"

        net_layout = [
            [sg.Image(data=image(net_file), key='net-image', background_color='white')]

        ]
        rack_layout = [
            [sg.Image(data=image(rack_file), key='rack-image', background_color='white')]

        ]

        log_layout = [
            [sg.T('Here comes the Log Data')],
        ]

        burn_layout.append(
            [sg.Image(data=image(cm_logo), key='cm-logo'),
            sg.Image(data=image(pi_logo), key='pi-logo')]

        )


        # burn_layout.append([sg.Button('',
        #                               button_color=(self.background, self.background),
        #                               image_filename=cm_logo,
        #                               image_size=(30, 30),
        #                               image_subsample=2,
        #                               border_width=0,
        #                               key='LOGO')])

        # layout.append([sg.Image(filename=logo, size=(30,30))])

        line("Devices")

        devices = USB.get_dev_from_diskutil()

        count = 0
        for device in devices:
            default = count == 0
            burn_layout.append(
                [sg.Radio(device, group_id="DEVICE", default=default, key=f"device-{device}")]
            )
            count = count + 1

        line("Operating System")

        count = 0
        for entry in ["Raspberry", "Ubuntu 20.10", "Ubuntu 20.04"]:
            default = count == 0
            burn_layout.append(
                [sg.Radio(entry, group_id="OS", default=default, key=f"os-{entry}")]
            )
            count = count + 1



        # for device in self.devices:
        #    burn_layout.append([sg.Radio(device['dev'], group_id="DEVICE"),
        #                        sg.Text(d),
        #                        sg.Text(device["size"]),
        #                        sg.Text(device["info"]),
        #                        sg.Text(device["formatted"]),
        #                        ])

        # this has wrong layout it must be vertical
        # BUG: THIS IS A BUG AS IT SHOULD RENDER ANYWAYS WE NEED THE KEY
        line("Security")
        if self.key is not None:
            burn_layout.append([sg.Text("Key", size=(15,1)), sg.Input(key="key", default_text=self.key)])

        burn_layout.append([sg.Text("SSID", size=(15,1)), sg.Input(key="ssid", default_text="")])
        burn_layout.append([sg.Text("Wifi Password", size=(15,1)), sg.Input(key="wifi", default_text="", password_char='*')])


        line("Manager")

        if self.manager is not None:
            manager = self.manager
            i = 0
            burn_layout.append(
                    [
                        sg.Text(' todo ', size=(5, 1), key=str('status-manager')),
                        sg.Button('Burn', key=str('button-manager')),
                        sg.Text(manager, size=(width, 1)),
                        sg.Text("manager", size=(8, 1)),
                        sg.Input(default_text=manager, size=(width, 1), key=str('name-manager')),
                        sg.Input(default_text=self.ips[i], size=(width, 1), key=str('ip-manager')),
                        sg.Text('Image'),
                        sg.Input(default_text="latest-full", size=(width, 1), key=str('tags-manager'))
                    ]
            )

        line("Workers")

        if self.workers is not None:
            i = 1
            for worker in self.workers:
                burn_layout.append([
                    sg.Text(' todo ', size=(5, 1), key=str(f'status-worker-{worker}')),
                    sg.Button('Burn', key=str(f'button-worker-{worker}')),
                    sg.Text(worker, size=(width, 1)),
                    sg.Text("worker", size=(8, 1)),
                    sg.Input(default_text=worker, size=(width, 1), key=str(f'name-worker-{worker}')),
                    sg.Input(default_text=self.ips[i], size=(width, 1), key=str(f'ip-worker-{worker}')),
                    sg.Text('Image'),
                    sg.Input(default_text="latest-lite", size=(width, 1), key=str(f'tags-worker-{worker}')),
                ])
                i = i + 1

        self.layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab('Burn', burn_layout, key="panel-burn"),
                            sg.Tab('Log', log_layout, key="panel-lg", background_color='white'),
                            sg.Tab('Network', net_layout, key="panel-net", background_color='white'),
                            sg.Tab('Rack', rack_layout, key="panel-rack", background_color='white')
                        ]
                    ],
                    tooltip='Rack', key="mytabs")
            ],
            [sg.Button('Cancel', key="cancel"), sg.Button('Next Card', key="next"),]
        ]

    def value_mapper(self, values, arguments):
        arguments["key"] = values["key"]
        arguments["manager"] = values["name-manager"]

        # 'key': '/Users/grey/.ssh/id_rsa.pub',
        # 'name-manager-red':
        # 'red', 'ip-manager-red': '10.0.0.1',
        # 'tags-manager-red': 'latest-full',
        # 'Browse': '',
        # 'name-worker-red01': 'red01',
        # 'ip-worker-red01': '10.0.0.2',
        # 'tags-worker-red01': 'latest-lite',
        # 'Browse0': '',
        # 'name-worker-red02': 'red02',
        # 'ip-worker-red02': '10.0.0.3',
        # 'tags-worker-red02': 'latest-lite',
        # 'Browse1': '',
        # 1: 'Burn'}


    def create_diag(self, name):
        print("Creating Diagrams .", end="", flush=True)
        Shell.mkdir("~/.cloudmesh/gui")
        _execute(f'cd ~/.cloudmesh/gui; cms diagram set {name} --hostname="{self.hostnames}"')
        _execute(f'cd ~/.cloudmesh/gui; cms diagram net {name} -n --output=png')
        _execute(f'cd ~/.cloudmesh/gui; cms diagram rack {name} -n --output=png')
        print(" ok", flush=True)

    def run(self):

        Sudo.password()

        window = sg.Window('Cloudmesh Pi Burn', self.layout, size=(650, 600))
        # print(self.devices)
        # print(self.details)


        host = None
        ips = None
        hostnames = None
        key = None
        event = None
        tags = None
        kind = None
        device = None

        while True:

            event, values = window.read()
            if event in ("Cancel", 'cancel', None):
                break

            VERBOSE(event)
            VERBOSE(values)

            ips = []
            hostnames = []
            for entry in values:
                if str(entry).startswith("name"):
                    hostnames.append(values[entry])
                if str(entry).startswith("ip"):
                    ips.append(values[entry])
                if str(entry).startswith("device-") and values[entry]:
                    device = "/dev/" + entry.replace("device-", "")

            key = values['key']

            if event == 'button-manager':
                host = values['name-manager']
                kind = "manager"
                tags = values['tags-manager']
                self.burn(kind, host)
            elif event.startswith('button-worker'):
                host = event.replace("button-worker-", "")
                kind = "worker"
                self.burn(kind, host)

            ssid = values['ssid']
            print()
            print("Host:    ", host)
            print("IPs:     ", ips)
            print("Hostnames", hostnames)
            print("Ssid:    ", ssid)
            print("Key:     ", key)
            print("Event:   ", event)
            print("Tags:    ", tags)
            print("Kind:    ", kind)
            print("Device:  ", device)
            print()


            self.hostnames_str = ','.join(hostnames)
            self.ips_str = ','.join(ips)


            command = "cms burn cluster --device=/dev/disk2"\
                      f" --hostname={self.hostnames_str}"\
                      f" --ssid={ssid}"\
                      f" --ip={self.ips_str}"\
                      f" --burning={host}"\
                      " -y"

            print (command)
            # os.system(command)

        print('exit')
        window.close()
