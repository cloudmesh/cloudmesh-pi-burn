import inspect
import os.path
import time

import PySimpleGUI as sg  # noqa
import oyaml as yaml
from cloudmesh.burn.usb import USB
from cloudmesh.burn.util import os_is_linux
from cloudmesh.burn.util import os_is_mac
from cloudmesh.common.Host import Host
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Tabulate import Printer
# import PySimpleGUIWx as sg
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.sudo import Sudo
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.diagram.diagram import Diagram
from cloudmesh.burn.wifi.ssid import get_ssid
from cloudmesh.inventory.inventory import Inventory


def _execute(command):
    # print(".", end="", flush=True)
    os.system(f"{command} >> burn-gui.log")


def image(name):
    with open(path_expand(name), 'rb') as file:
        return file.read()


window_size = (800, 800)
log_size = (600, 600)
status_width = (10, 1)
name_width = (10, 1)
tag_width = (15, 1)
entry_width = (10, 1)
security_width = (20, 1)

image_tags = {
    "os_raspberryos": {
        "name": "Raspberry OS",
        "manager": "latest-full",
        "worker": "latest-lite",
    },
    "os_ubuntu_64bit_20_04": {
        "name": "Ubuntu 64-bit 20.04",
        "manager": "ubuntu-20.04.2-64-bit ",
        "worker": "ubuntu-20.04.2-64-bit "
    },
    "os_ubuntu_64bit_20_10": {
        "name": "Ubuntu 64-bit 20.10",
        "manager": "ubuntu-20.10-64-bit",
        "worker": "ubuntu-20.10-64-bit"
    },
    "os_ubuntu_64bit_20_10_desktop": {
        "name": "Ubuntu 64-bit 20.10 desktop",
        "manager": "ubuntu-desktop",
        "worker": "ubuntu-desktop"
    }
}


class Gui:

    def __init__(self, hostname=None, ip=None, dryrun=False, no_diagram=False):

        self.dryrun = dryrun or False
        self.hostnames_str = hostname
        self.ips_str = ip
        self.hostnames = hostnames = hostname or "red,red[01-02]"
        self.ips = ips = ip or "10.0.0.[1-3]"
        self.ssid = get_ssid()
        self.imaged = ""
        self.wifipassword = ""
        self.no_diagram = no_diagram

        hostnames = Parameter.expand(hostnames)
        manager, workers = Host.get_hostnames(hostnames)

        if workers is None:
            n = 1
        else:
            n = len(workers) + 1
        if ip is None:
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
        print("Dryrun:       ", self.dryrun)

        self.manager = manager
        self.workers = workers
        self.ips = ips

        self.load_data()

        if not self.no_diagram:
            self.create_diag(self.manager)
        self.create_layout()
        # sg.change_look_and_feel('SystemDefault')
        self.window = sg.Window('Cloudmesh Pi Burn', self.layout, resizable=True, size=window_size)

    def burn(self, kind, hostname):
        """
        if hostname == 'red':
            ip = self.ips[0]
            print("in red")
            print(ip)
        else:
            ip_location = int(hostname.replace('red', ""))
            print("in red00x")
            print(ip_location)
            ip = self.ips[ip_location]
            print("in red")
            print(ip)
        """

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

    def create_layout(self):

        def line(msg):
            title = f'__ {msg} '
            title = title.ljust(120, '_')

            burn_layout.append([sg.Text(title)])

        location = os.path.dirname(os.path.abspath(inspect.getsourcefile(Gui)))

        cm_logo = f'{location}/images/cm-logo-100.png'
        pi_logo = f'{location}/images/raspberry-logo-white-100.png'
        rack_file = f"~/.cloudmesh/gui/{self.manager}-rack.png"
        net_file = f"~/.cloudmesh/gui/{self.manager}-net.png"

        burn_layout = [
            [sg.T('')]
        ]

        if not self.no_diagram:
            net_layout = [
                [sg.Image(data=image(net_file), key='net-image', background_color='white')]

            ]
            rack_layout = [
                [sg.Image(data=image(rack_file), key='rack-image', background_color='white')]
            ]
        else:
            net_layout = []
            rack_layout = []

        size = log_size
        log_layout = [[sg.T('', key="log", size=size)]]
        log_scroll_layout = [
            [sg.Column(layout=log_layout, scrollable=True)]
        ]

        burn_layout.append(
            [
                sg.Text(40 * " "),
                sg.Image(data=image(cm_logo), key='cm-logo'),
                sg.Image(data=image(pi_logo), key='pi-logo')
            ]
        )

        #
        # DEVICES
        #
        line("Devices")
        if os_is_mac():
            devices = USB.get_dev_from_diskutil()
        elif os_is_linux():
            devices = USB.get_from_dmesg()
        else:
            devices = {}

        count = 0
        for device in devices:
            default = count == 0
            if os_is_linux():
                burn_layout.append(
                    [sg.Radio(device['dev'], group_id="DEVICE",
                              default=default,
                              key=f"device-{device['name']}")]
                )
            else:
                burn_layout.append(
                    [sg.Radio(device, group_id="DEVICE", default=default, key=f"device-{device}")]
                )
            count = count + 1

        #
        # SDCARD
        #
        line("SD Card")

        burn_layout.append(
            [sg.Checkbox("format", default=True, key="imaged")]
        )

        #
        # OPERATING SYSTEM
        #
        line("Operating System")

        count = 0
        for entry in image_tags:
            data = image_tags[entry]
            name = data["name"]
            default = count == 0
            burn_layout.append(
                [sg.Radio(name,
                          group_id="OS",
                          enable_events=True,
                          default=default,
                          key=entry)]
            )
            count = count + 1

        #
        # SECURITY
        #
        line("Security")
        if self.key is not None:
            burn_layout.append([sg.Text("Key", size=security_width), sg.Input(key="key", default_text=self.key)])

        burn_layout.append([sg.Text("SSID", size=security_width), sg.Input(key="ssid", default_text=self.ssid)])
        burn_layout.append(
            [sg.Text("Wifi Password", size=security_width), sg.Input(key="wifi", default_text="", password_char='*')])

        #
        # MANAGER
        #
        line("Manager")

        if self.manager is not None:
            manager = self.manager
            i = 0
            burn_layout.append(
                [
                    sg.Text('', size=status_width, key=str(f'status-{manager}')),
                    sg.Button('Burn', key=str(f'button-{manager}')),
                    sg.Text(manager, size=name_width),
                    sg.Text("manager", size=name_width),
                    sg.Input(default_text=manager, size=name_width, key=str(f'name-{manager}')),
                    sg.Input(default_text=self.ips[i], size=name_width, key=str(f'ip-{manager}')),
                    sg.Text('Image'),
                    sg.Input(default_text="latest-full", size=tag_width, key=str(f'tags-{manager}'))
                ]
            )

        #
        # WORKERS
        #
        line("Workers")

        worker_layout = []
        if self.workers is not None:
            i = 1
            for worker in self.workers:
                worker_layout.append(
                    [
                        sg.Text('', size=status_width, key=str(f'status-{worker}')),
                        sg.Button('Burn', key=str(f'button-{worker}')),
                        sg.Text(worker, size=name_width),
                        sg.Text("worker", size=name_width),
                        sg.Input(default_text=worker, size=name_width, key=str(f'name-{worker}')),
                        sg.Input(default_text=self.ips[i], size=name_width, key=str(f'ip-{worker}')),
                        sg.Text('Image'),
                        sg.Input(default_text="latest-lite", size=tag_width, key=str(f'tags-{worker}')),
                    ])
                i = i + 1
        burn_layout.append([sg.Column(worker_layout, scrollable=True, size=(800, 400))])

        #
        # TABS
        #

        self.cancel_layout = [sg.Button('Cancel', key="cancel")]

        self.layout = [
            self.cancel_layout,  # , sg.Button(' Next Card -> ', key="next")],
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab('Burn', burn_layout, key="panel-burn"),
                            sg.Tab('Log', log_scroll_layout, key="panel-lg", background_color='white'),
                            sg.Tab('Network', net_layout, key="panel-net", background_color='white'),
                            sg.Tab('Rack', rack_layout, key="panel-rack", background_color='white')
                        ]
                    ],
                    tooltip='Rack', key="mytabs")
            ]
        ]
        return self.layout

    def create_diag(self, name, _new=True):

        self.logger("Creating Diagrams")

        directory = path_expand("~/.cloudmesh/gui")
        Shell.mkdir(directory)
        location = f"{directory}/{name}"

        hostnames = Parameter.expand(self.hostnames)
        if _new:
            rack = Diagram(names=hostnames, name=hostnames[0])
            rack.save(location)

        diagram = Diagram()
        diagram.load(location)

        diagram.render_rack()
        diagram.saveas(f"{location}-rack", kind="rack", output="png")

        diagram.render_bridge_net()
        diagram.saveas(f"{location}-net", kind="net", output="png")

    def logger(self, msg, end="\n\n"):
        try:
            text = self.window['log']
            text.update(text.get() + msg + end)
            self.window.Refresh()
        except:  # noqa
            print(msg)

    def set_diagram_value(self, name, entry, attribute, value):
        directory = path_expand("~/.cloudmesh/gui")
        Shell.mkdir(directory)
        location = f"{directory}/{name}"
        diagram = Diagram()
        diagram.load(location)
        data = {
            attribute: value
        }
        diagram.set(entry, **data)
        diagram.save(location)

    def update_diagram_colors(self, cluster, host, color):

        self.set_diagram_value(cluster, host, "rack.color", color)
        self.set_diagram_value(cluster, host, "net.color", color)
        self.create_diag(cluster, _new=False)

        rack_file = f"~/.cloudmesh/gui/{cluster}-rack.png"
        net_file = f"~/.cloudmesh/gui/{cluster}-net.png"

        self.window['net-image'].update(data=image(net_file))
        self.window['rack-image'].update(data=image(rack_file))
        self.window.Refresh()

    def set_button_color(self, host, color):
        host = str(host)
        try:
            self.window.FindElement(f'button-{host}').Update(button_color=('white', color))
            self.window.Refresh()
        except:   # noqa
            pass

    def run(self):

        Sudo.password()

        host = None
        ips = None
        hostnames = None
        key = None
        event = None
        tags = None
        kind = None
        device = None

        while True:

            event, values = self.window.read()

            if event in ("Cancel", 'cancel', None):
                if not self.no_diagram:
                    rack_file = f"~/.cloudmesh/gui/{self.manager}-rack.png"
                    net_file = f"~/.cloudmesh/gui/{self.manager}-net.png"
                    os.remove(path_expand(rack_file))
                    os.remove(path_expand(net_file))
                break

            #
            # UPDATE OS SELECTION
            #
            if event.startswith("os"):
                for image in values:
                    if image.startswith("os") and values[image]:
                        break

                self.logger(f"Switch OS to: {image}")

                image_manager = image_tags[image]["manager"]
                image_worker = image_tags[image]["worker"]

                self.window[f'tags-{self.manager}'].update(image_manager)
                for worker in self.workers:
                    self.window[f'tags-{worker}'].update(image_worker)
                self.window.Refresh()

            if event.startswith("button"):

                #
                # set imaged string
                #
                imaged = values['imaged']
                if not imaged:
                    self.imaged_str = "--imaged"
                else:
                    self.imaged_str = ""
                #
                # handle device, hostnames and ips
                #
                ips = []
                hostnames = []
                tags = []
                for entry in values:
                    if str(entry).startswith("name"):
                        hostnames.append(values[entry])
                    if str(entry).startswith("ip"):
                        ips.append(values[entry])
                    if str(entry).startswith("device-") and values[entry]:
                        device = "/dev/" + entry.replace("device-", "")
                    if str(entry).startswith("tag") and values[entry]:
                        tags.append(values[entry])

                key = values['key']
                self.hostnames_str = ','.join(hostnames)
                self.ips_str = ','.join(ips)
                #
                # get the ssid
                #
                self.ssid = values['ssid']
                self.wifipassword = values['wifi']

                host = event.replace("button-", "")
                self.set_button_color(host, 'grey')
                if host == self.manager:
                    kind = "manager"
                else:
                    kind = "worker"

                print()
                print("Host:    ", host)
                print("IPs:     ", ips)
                print("Hostnames", hostnames)
                print("Ssid:    ", self.ssid)
                print("Key:     ", key)
                print("Event:   ", event)
                print("Tags:    ", tags)
                print("Kind:    ", kind)
                print("Device:  ", device)
                print("Format   ", imaged)
                print()

                # Call burn function for manager and workers
                self.logger(f"Burning {kind} {host}")
                # tags = values[f'tags-{host}']
                self.window[f'status-{host}'].update(' Burning ')

                if not self.no_diagram:
                    self.update_diagram_colors(self.manager, host, "blue")
                self.hostnames_str = ','.join(hostnames)
                self.ips_str = ','.join(ips)
                # command = f"cms burn cluster --device={device}" \
                #          f" --hostname={self.hostnames_str}" \
                #          f" --ssid={self.ssid}" \
                #          f" --wifipassword={self.wifipassword}" \
                #          f" --ip={self.ips_str}" \
                #          f" --burning={host}" \
                #          " -y" \
                #          f" {self.imaged_str}"

                manager, workers = Host.get_hostnames(hostnames)
                filename = path_expand(f"~/.cloudmesh/inventory-{manager}.yaml")
                Inventory.build_default_inventory(filename=filename, manager=manager,
                                         workers=workers, ips=ips,
                                         gui_images=tags)

                if "ubuntu" in tags[0]:
                    os_cmd = 'ubuntu'
                else:
                    os_cmd = 'raspberry'

                if host == manager:
                    command = f"cms burn {os_cmd} {host}" \
                              f" --device={device}" \
                              f" --ssid={self.ssid}" \
                              f" --wifipassword={self.wifipassword}" \
                              f" --country={Shell.locale().upper()}"
                else:
                    command = f"cms burn {os_cmd} {host}" \
                              f" --device={device}"
                    print(command)

                try:
                    self.logger(f"Executing: {command}")
                    if self.dryrun:
                        time.sleep(0.5)
                    else:
                        os.system(command)
                    self.window[f'status-{host}'].update(' Completed ')
                    if not self.no_diagram:
                        self.update_diagram_colors(self.manager, host, "green")
                    self.set_button_color(host, 'green')

                except Exception as e:
                    print(e)
                    self.logger("Command failed")
                    if not self.no_diagram:
                        self.update_diagram_colors(self.manager, host, "orange")
                    self.set_button_color(host, 'red')

                self.window.FindElement(f'button-{host}').Update(button_color=('white', 'green'))

                self.window.Refresh()

        print('exit')
        self.window.close()
