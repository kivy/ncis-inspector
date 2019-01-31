__all__ = ['PythonInspectPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial
import json


Builder.load_string('''
#:import _ inspector.panels.python_object
<EntryPythonInspectPanel>:
    text: ""
    cols: 2
    spacing: dp(4)
    Label:
        text: root.text
        size_hint_x: None
        width: dp(150)
        text_size: self.width, None
        font_name: "RobotoMono-Regular"
        markup: True
        shorten: True
        on_ref_press: root.ref_callback(args[1])

    PythonObjectPanel:
        obj: root.obj
        oneline: True

<PythonInspectPanel>:
    RecycleView:
        id: rv
        viewclass: "EntryPythonInspectPanel"
        RecycleBoxLayout:
            spacing: dp(4)
            padding: dp(4)
            default_size: None, dp(24)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

''')

class EntryPythonInspectPanel(F.GridLayout):
    obj = ObjectProperty(allownone=True)
    ref_callback = ObjectProperty(allownone=True)


class PythonInspectPanel(F.RelativeLayout):
    __events__ = [
        "on_ref_pressed"
    ]
    cmd = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        _ = F.EntryPythonInspectPanel()
        super().__init__(**kwargs)
        if self.cmd:
            self.refresh()

    def on_cmd(self, *largs):
        self.refresh()

    def refresh(self, *largs):
        self.ids.rv.data = []
        if isinstance(self.cmd, dict) and self.cmd.get("__pyobject__"):
            o = self.cmd["__pyobject__"]
            ctl.request(
                "/python/inspect/{}".format(o["id"]),
                self.on_inspect_callback)
        else:
            ctl.request(
                "/python/inspect",
                self.on_inspect_callback,
                method="POST",
                params={"cmd": self.cmd})

    def on_inspect_callback(self, status, response):
        if not response or status != "ok":
            self.ids.rv.data = []
            return
        data = [{
            "text": entry[0],
            "obj": entry[1]
        } for entry in response]
        self.ids.rv.data = data

    def on_ref_pressed(self, ref):
        pass