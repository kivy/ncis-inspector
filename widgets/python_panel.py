from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder

import json

__all__ = ['PythonInfoPanel']


KV = '''
<PythonInfoPanel>:
    text: 'python info'
    TextInput:
        readonly: True
        text: root.info
'''

class PythonInfoPanel(TabbedPanelItem):
    info = StringProperty()
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

        Clock.schedule_interval(self.fetch_info, 1)

    def fetch_info(self, dt):
        self.app.request('/python/version', self._parse_info)

    def _parse_info(self, status, response):
        print(status, response)
        self.info = json.dumps(response, indent=2)


Builder.load_string(KV)
