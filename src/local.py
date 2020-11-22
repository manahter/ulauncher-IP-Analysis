import ifcfg

from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


def generate_local_item(name, ip, description):
    return ExtensionResultItem(icon='images/icon.png',
        name='{}: {}'.format(name, ip),
        description=description,
        on_enter=CopyToClipboardAction(ip)
    )


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
