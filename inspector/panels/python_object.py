__all__ = ['PythonObjectPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial
import json


Builder.load_string('''
<JSONPythonObjectPanel@Label>:
    font_name: "RobotoMono-Regular"
    text_size: self.width, None

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
        self.clear_widgets()
        text = json.dumps(obj, indent=2)
        self.add_widget(F.JSONPythonObjectPanel(
            text=text,
            font_name="RobotoMono-Regular"
        ))