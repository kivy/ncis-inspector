__all__ = ['PythonObjectPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.utils import PythonObjectRepr
from inspector.controller import ctl
from functools import partial
import json


Builder.load_string('''
<EntryJSONPythonObjectPanel@AnchorLayout>:
    ref_callback: None
    anchor_x: "left"
    text: ""
    Label:
        text: root.text
        size_hint: None, None
        width: self.texture_size[0]
        font_name: "RobotoMono-Regular"
        markup: True
        shorten: True
        on_ref_press: root.ref_callback(args[1])

<JSONPythonObjectPanel@RecycleView>:
    viewclass: "EntryJSONPythonObjectPanel"
    RecycleBoxLayout:
        spacing: dp(4)
        padding: dp(4)
        default_size: None, dp(18)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'

<PythonObjectPanel>:
''')



class PythonObjectPanel(F.RelativeLayout):
    __events__ = [
        "on_ref_pressed"
    ]
    obj = ObjectProperty(allownone=True)
    oneline = BooleanProperty(False)

    def __init__(self, **kwargs):
        _ = F.EntryJSONPythonObjectPanel()
        super().__init__(**kwargs)
        if self.obj:
            self.refresh()

    def on_obj(self, *largs):
        self.refresh()

    def create_ref(self, o):
        uid = o["__pyobject__"]["id"]
        if uid is None:
            return
        uid = str(uid)
        self.refs[uid] = o
        return uid

    def ref_callback(self, ref):
        self.dispatch("on_ref_pressed", self.refs[ref])

    def refresh(self, *largs):
        obj = self.obj

        self.refs = {}
        pyr = PythonObjectRepr(obj, self.refs, self)
        if self.oneline:
            text = pyr.render_full(oneline=True, max=256)
        else:
            text = pyr.render_full()

        self.clear_widgets()

        # build a json panel, but each line = one entry in rv
        data = [
            {
                "text": line,
                "ref_callback": self.ref_callback
            } for line in text.split("\n")
        ]
        wid = F.JSONPythonObjectPanel()
        wid.data = data
        self.add_widget(wid)

    def on_ref_pressed(self, ref):
        pass
