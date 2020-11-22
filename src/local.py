from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


def generate_local_item(name, ip, description):
    return ExtensionResultItem(icon='images/icon.png',
        name='{}: {}'.format(name, ip),
        description=description,
        on_enter=CopyToClipboardAction(ip)
    )


try:
    import ifcfg


    def get_local_items():
        items = []

        for name, interface in ifcfg.interfaces().items():
            interface_ip = interface['inet']

            if interface_ip is None:
                continue

            items.append(generate_local_item(name, interface_ip, 'Associated IP'))

            for ip in [ip for ip in interface['inet4'] if ip != interface_ip]:
                items.append(generate_local_item(name, ip, 'IPv4 alias'))

            for ip in [ip for ip in interface['inet6'] if ip != interface_ip]:
                items.append(generate_local_item(name, ip, 'IPv6 alias'))

        return items
except:
    import os
    import re
    import subprocess as sp


    # Resource: https://stackoverflow.com/a/57447014
    def get_nics():
        """
            Get all NICs from the Operating System.

            Returns
            -------
            nics : list
                All Network Interface Cards.
        """
        result = sp.check_output(["ip", "addr", "show"])
        result = result.decode().splitlines()
        nics = [l.split()[1].strip(':') for l in result if l[0].isdigit()]
        return nics


    def get_ip_from_nic(nic, inet=""):
        re_comp = rf'(?<=inet{inet} )(.*)(?=\/)'
        try:
            # Resource: https://stackoverflow.com/a/38394394
            ip = re.search(re.compile(re_comp, re.M), os.popen(f'ip addr show {nic}').read()).groups()[0]
            return ip
        except:
            return ""


    def get_local_items():
        items = []

        for nic in get_nics():
            interface_ip = ""

            for inet, description in (("", "Associated IP"), ("4", "IPv4 alias"), ("6", "IPv6 alias")):
                ip = get_ip_from_nic(nic, inet)

                if not ip or ip == interface_ip:
                    continue

                elif not inet:
                    interface_ip = ip

                items.append(generate_local_item(nic, ip, description))

        return items
