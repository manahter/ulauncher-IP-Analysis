from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from src.consts import ICON_IMAGE, ASSOCIATED_IP, IP_V4, IP_V6


def generate_local_item(name, ip, description):
    text = f'{name} - {ip}'

    return ExtensionResultItem(
        icon=ICON_IMAGE,
        name=text,
        description=description,
        on_enter=CopyToClipboardAction(text)
    )


def get_local_items():
    return [generate_local_item(name, ip, ip_type) for (name, ip, ip_type) in get_local_hosts()]


try:
    import ifcfg

    def get_local_hosts():
        hosts = []

        for name, interface in ifcfg.interfaces().items():
            interface_ip = interface['inet']

            if interface_ip is None:
                continue

            hosts.append((name, interface_ip, ASSOCIATED_IP))

            for ip in [ip for ip in interface['inet4'] if ip != interface_ip]:
                hosts.append((name, ip, IP_V4))

            for ip in [ip for ip in interface['inet6'] if ip != interface_ip]:
                hosts.append((name, ip, IP_V6))

        return hosts


except:
    import os
    import re
    import subprocess as sp

    # Resource: https://stackoverflow.com/a/57447014
    def get_nics():
        '''
            Get all NICs from the Operating System.

            Returns
            -------
            nics : list
                All Network Interface Cards.
        '''
        result = sp.check_output(['ip', 'addr', 'show'])
        result = result.decode().splitlines()
        nics = [l.split()[1].strip(':') for l in result if l[0].isdigit()]
        return nics


    def get_ip_from_nic(nic, inet=''):
        re_comp = rf'(?<=inet{inet} )(.*)(?=\/)'
        try:
            # Resource: https://stackoverflow.com/a/38394394
            ip = re.search(re.compile(re_comp, re.M), os.popen(f'ip addr show {nic}').read()).groups()[0]
            return ip
        except:
            return ''


    def get_local_hosts():
        hosts = []

        for nic in get_nics():
            interface_ip = ''

            for inet, description in (('', ASSOCIATED_IP), ('4', IP_V4), ('6', IP_V6)):
                ip = get_ip_from_nic(nic, inet)

                if not ip or ip == interface_ip:
                    continue

                elif not inet:
                    interface_ip = ip

                hosts.append((nic, ip, description))

        return hosts
