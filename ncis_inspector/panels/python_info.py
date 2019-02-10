__all__ = ['PythonInfoPanel']

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from ncis_inspector.controller import ctl
import json


Builder.load_string('''
<PythonInfoPanel>:
    text: 'python info'
    TextInput:
        readonly: True
        text: root.info
''')

class PythonInfoPanel(TabbedPanelItem):
    info = StringProperty()
    app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_info, 1)

    def fetch_info(self, dt):
        ctl.request('/python/version', self._parse_info)

    def _parse_info(self, status, response):
        self.info = json.dumps(response, indent=2)
