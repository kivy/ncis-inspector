__all__ = ['PythonObjectPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial
import json


Builder.load_string('''
<EntryJSONPythonObjectPanel@Label>:
    text_size: self.width, None
    size_hint_y: None
    font_name: "RobotoMono-Regular"

<JSONPythonObjectPanel@RecycleView>:
    viewclass: "EntryJSONPythonObjectPanel"
    RecycleBoxLayout:
        spacing: dp(4)
        default_size: None, dp(12)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

<PythonObjectPanel>:
''')

class PythonObjectPanel(F.RelativeLayout):
    obj = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.obj:
            self.refresh()

    def on_obj(self, *largs):
        self.refresh()

    def refresh(self, *largs):
        obj = self.obj

        if isinstance(obj, str):
            text = obj
        elif isinstance(obj, bytes):
            text = repr(obj)
        else:
            text = json.dumps(obj, indent=2)

        self.clear_widgets()

        # build a json panel, but each line = one entry in rv
        data = [
            {
                "text": line
            } for line in text.split("\n")
        ]
        print(data)
        wid = F.JSONPythonObjectPanel()
        wid.data = data
        self.add_widget(wid)