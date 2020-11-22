import json
from requests import get
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class IplikExtension(Extension):
    def __init__(self):
        super(IplikExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


descriptions = {
    "query" : ["Associated IP",0],
    "status" : ["Status",0],
    "message" : ["Message",1],
    "continent" : ["Continent Name",2],
    "continentCode" : ["Continent Code (Two letter)",3],
    "country" : ["Country Name",4],
    "countryCode" : ["Country Code (Two letter)",5],
    "regionName" : ["Region/State Name",6],
    "region" : ["Region/State short code (FIPS or ISO)",7],
    "city" : ["City",8],
    "district" : ["District (subdivision of city)",9],
    "zip" : ["Zip Code",10],
    "lat" : ["Latitude",11],
    "lon" : ["Longitude",12],
    "timezone" : ["City Timezone",13],
    "currency" : ["National currency",14],
    "isp" : ["ISP Name",15],
    "org" : ["Organization Name",16],
    "as" : ["AS number and organization, separated by space (RIR).\n Empty for IP blocks not being announced in BGP tables.",17],
    "asname" : ["AS name (RIR). \nEmpty for IP blocks not being announced in BGP tables.",18],
    "reverse" : ["Reverse DNS of the IP",19],
    "mobile" : ["Mobile (Cellular) Connection",20],
    "proxy" : ["Proxy (Anonymous)",21]
}


def sirasi(item):
    return descriptions[item][1]


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or str()

        if query == 'local' or query == 'private':
            try:
                from src.local import get_local_items

                return RenderResultListAction([
                    ExtensionResultItem(icon='images/me.png',
                        name="My local/private IP Information",
                        description="Select for public information",
                        on_enter=SetUserQueryAction(extension.preferences['iplik'] + ' '))
                ] + get_local_items())
            except ImportError:
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='Ifcfg python package is required',
                        description='Installation: pip3 install ifcfg --user',
                        on_enter=OpenUrlAction('https://pypi.org/project/ifcfg/')
                    )
                ])
        
        liste = [i if extension.preferences[i] == "Yes" else "" for i in extension.preferences.keys()]
        liste_str = ",".join(liste)
        json_data = get("http://ip-api.com/json/{}?fields={}".format(query, liste_str)).json()
        
        if 'message' in json_data.keys():
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                    name='Invalid query',
                    description='No information for query `{}`'.format(query),
                    on_enter=HideWindowAction()
                )
            ])

        liste_sirali = [i for i in json_data.keys()]
        liste_sirali.sort(key=sirasi)

        items = [
            ExtensionResultItem(icon='images/icon.png',
                                name=str(json_data[i]),
                                description=descriptions[i][0],
                                on_enter=CopyToClipboardAction(str(json_data[i])))
            for i in liste_sirali
        ]
        
        if not query:
            o = ExtensionResultItem(icon='images/me.png',
                                name="My public IP Information",
                                description="Select for local/private information",
                                on_enter=SetUserQueryAction(extension.preferences['iplik'] + ' local'))
            items = [o] + items
        return RenderResultListAction(items)


if __name__ == '__main__':
    IplikExtension().run()
