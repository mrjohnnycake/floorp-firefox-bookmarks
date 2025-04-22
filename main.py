from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, SystemExitEvent,PreferencesUpdateEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from history import FloorpBookmarks

class FloorpBookmarksExtension(Extension):
    def __init__(self):
        super(FloorpBookmarksExtension, self).__init__()
        #   Floorp Bookmarks Getter
        #   Delayed initialisation, need to get path from preferences
        self.fb = None
        #   Ulauncher Events
        self.subscribe(KeywordQueryEvent,KeywordQueryEventListener())
        self.subscribe(SystemExitEvent,SystemExitEventListener())
        self.subscribe(PreferencesEvent,PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,PreferencesUpdateEventListener())

    def init_fb(self, floorp_path: str):
        #   Initialise Floorp Bookmarks Getter with path from preferences
        if self.fb is None:
            self.fb = FloorpBookmarks(floorp_path)

class PreferencesEventListener(EventListener):
    def on_event(self,event,extension):
        extension.init_fb(event.preferences['path'])
        #   Aggregate Results
        #extension.fb.aggregate = event.preferences['aggregate']
        #   Results Order
        #extension.fb.order = event.preferences['order']
        #   Results Number
        try:
            n = int(event.preferences['limit'])
        except:
            n = 10
        extension.fb.limit = n
        
class PreferencesUpdateEventListener(EventListener):
    def on_event(self,event,extension):
        extension.init_fb(event.preferences['path'])
        #   Results Order
        #if event.id == 'order':
        #    extension.fb.order = event.new_value
        #   Results Number
        if event.id == 'limit':
            try:
                n = int(event.new_value)
                extension.fb.limit = n
            except:
                pass
        #elif event.id == 'aggregate':
        #    extension.fb.aggregate = event.new_value

class SystemExitEventListener(EventListener):
    def on_event(self,event,extension):
        if extension.fb is not None:
            extension.fb.close()

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        extension.init_fb(extension.preferences['path'])
        query  = event.get_argument()
        #   Blank Query
        if query == None:
            query = ''
        items = []
        #   Search into Floorp Bookmarks
        results = extension.fb.search(query)
        for link in results:
            #   Encode 
            hostname = link[0]
            #   Split Domain Levels
            dm = hostname.split('.')
            #   Remove WWW
            if dm[0]=='www':
                i = 1
            else:
                i = 0
            #   Join remaining domains and capitalize
            name = ' '.join(dm[i:len(dm)-1]).title()
            #   TODO: favicon of the website
            #if extension.fb.aggregate == "true":
            #    items.append(ExtensionResultItem(icon='images/icon.png',
                                            #    name=name,
                                            #    on_enter=OpenUrlAction('https://'+hostname)))
            #else:
            title = link[0]
            url = link[1]
                #if link[1] == None:
                #    title = hostname
                #else:
                #    title = link[1]
            items.append(ExtensionResultItem(icon='images/icon.png',
                                            name=title,
                                            description=url,
                                            on_enter=RunScriptAction(f"xdg-open {url}")))

        return RenderResultListAction(items)

if __name__ == '__main__':
    FloorpBookmarksExtension().run()
