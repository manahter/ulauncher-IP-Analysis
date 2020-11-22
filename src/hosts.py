from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


def get_hosts():
    hosts = {}

    with open('/etc/hosts', 'r') as f:
        for line in f:
            splited = line.split()

            if len(splited) != 2:
                continue

            (ip, host) = splited

            if ip.strip()[0] in ['#', '/'] or not ip or not host:
                continue
            
            hosts[host] = ip

    return hosts


def show_hosts_items():
    return [
        ExtensionResultItem(
            icon='images/icon.png',
            name=host,
            description=ip,
            on_enter=CopyToClipboardAction(ip))
        for (host, ip) in get_hosts().items()
    ]


def get_host_ip(query):
    return get_hosts().get(query)