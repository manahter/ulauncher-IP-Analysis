import re
import subprocess

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from src.consts import ME_IMAGE, ANALYZE_IMAGE, ASSOCIATED_IP, NMAP_HOST_REGEX, NMAP_IP_REGEX
from src.local import get_local_hosts


def generate_local_item(command, name, ip):
    return ExtensionResultItem(
        icon=ANALYZE_IMAGE,
        name=f'{name} - {ip}',
        description='Select to analyze ip network hosts',
        on_enter=SetUserQueryAction(f'{command} analyze {ip}/24')
    )


def generate_analyze_item(ip_mask, name, ip):
    return ExtensionResultItem(
        icon=ANALYZE_IMAGE,
        name=name,
        description=ip,
        on_enter=CopyToClipboardAction(f'{name} - {ip}')
    )


def show_analyze_items(command, query):
    local_hosts = [
        (name, ip) for (name, ip, ip_type) in get_local_hosts()
        if ip_type == ASSOCIATED_IP
    ]

    if query == '':
        return [
            ExtensionResultItem(
                icon=ME_IMAGE,
                name="Local IPs to analyze:",
                description="Select for local/private information",
                on_enter=SetUserQueryAction(f'{command} local')
            )
        ] + [
            generate_local_item(command, name, ip) for (name, ip) in local_hosts
        ]

    args = query.split('/')
    searched = args[0]
    searched_ip = None
    mask = args[1] if len(args) == 2 else '24'

    if not mask.isnumeric() or int(mask) < 20:
        return [
            ExtensionResultItem(
                icon=ANALYZE_IMAGE,
                name='Network mask must be between 20 and 32',
                description='Select for default mask',
                on_enter=SetUserQueryAction(f'{command} analyze {searched}/24')
            )
        ]

    mask = int(mask)
    possible_ip = searched.split('.')

    if len(possible_ip) == 4:
        if mask >= 24:
            searched_ip = '.'.join(possible_ip[:2]) + '.'
        elif mask >= 16:
            searched_ip = '.'.join(possible_ip[:1]) + '.'
        elif mask >= 8:
            searched_ip = '.'.join(possible_ip[:0]) + '.'


    for (name, ip) in local_hosts:
        if (searched_ip is not None and ip.startswith(searched_ip)) or ip == searched or name == searched:
            ip_mask = f'{ip}/{mask}'
            analyzed_hosts = []

            process = subprocess.Popen(f'nmap -sn {ip_mask}', shell=True, stdout=subprocess.PIPE)
            errorcode = process.wait()

            if errorcode != 0:
                return [
                    ExtensionResultItem(
                        icon=ANALYZE_IMAGE,
                        name='Nmap failed or it is not installed',
                        description='Only associated local ips are allowed',
                        on_enter=HideWindowAction()
                    )
                ]

            result = process.stdout.read().decode()
            lines = result.split('\n')[1:-2]

            for i in range(0, len(lines), 2):
                line = lines[i]

                match = re.match(NMAP_HOST_REGEX, line)
                if match is not None:
                    analyzed_hosts.append((match.group(1), match.group(2)))

                    continue

                match = re.match(NMAP_IP_REGEX, line)
                if match is not None:
                    analyzed_hosts.append((match.group(1), match.group(1)))

            return [
                ExtensionResultItem(
                    icon=ME_IMAGE,
                    name=f'Hosts detected in {name} network:',
                    description="Select for local/private information",
                    on_enter=SetUserQueryAction(f'{command} local')
                )
            ] + [generate_analyze_item(ip_mask, name, ip) for (name, ip) in analyzed_hosts]

    return [
        ExtensionResultItem(
            icon=ANALYZE_IMAGE,
            name='IP cannot be analyzed',
            description='Only associated local ips are allowed',
            on_enter=HideWindowAction()
        )
    ]

# print(show_analyze_items('a', '192.168.1.14/24'))