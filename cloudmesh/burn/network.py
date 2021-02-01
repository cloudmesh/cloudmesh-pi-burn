import json
import socket
import subprocess


# TODO: ther eseems to be some overlap with hardware.py and some functions in
#       hardware introduced that are not used here such as getfqdn and hostname.
#       Should it be removed form hardware, or should this be changed here to
#       use the methods from hardware?
#
# TODO: get method is not implemented

class Network:

    @staticmethod
    def address():
        hostname = socket.gethostname()
        full = socket.getfqdn()

        # ipv4
        result = []
        try:
            details = json.loads(subprocess.getoutput("ip -json a"))
        except Exception as e:
            details = None
        for entry in details:
            try:
                adresses = entry['addr_info']
                for n in adresses:
                    if entry['ifname'] not in ['lo']:
                        element = {
                            'ip': socket.gethostbyname(hostname),
                            'hostname': hostname,
                            'ifname': entry['ifname'],
                            'fullname': full,
                            'ipbyname': socket.gethostbyname(hostname),

                        }
                        # print ("nnn", n)
                        element.update(n)
                        if 'broadcast' in n.keys():
                            result.append(element)
            except Exception as e:
                pass
        return result

    @staticmethod
    def nmap(ip=None):
        if ip is None:
            ip = Network.address()['ip']
        mask = ip.rsplit(".", 1)[0]
        command = f"nmap -sP {mask}.*"
        print(command)
        result = subprocess.getoutput(command)
        result = result.replace("Nmap scan report for ", "")
        result = result.replace("Host is ", "")
        result = result.replace(" latency.", "")

        result = result.splitlines()[1:]
        details = []
        for i in range(0, int(len(result) / 2)):
            position = 2 * i
            a = result[position]
            b = result[position + 1]
            line = f"{a} {b}"
            if "(" not in a:
                line = f"unkown {a} {b}"

            line = line.replace("(", "")
            line = line.replace(")", "")

            attributes = line.split()
            details.append({
                'name': attributes[0],
                'ip': attributes[1],
                'status': attributes[2],
                'latency': attributes[3],
                'line': line
            })

        return details

    @staticmethod
    def get():

        return
