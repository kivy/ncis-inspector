__all__ = ['PythonObjectPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import escape_markup
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


class PythonObjectRepr(object):
    def __init__(self, o, refs, panel):
        super(PythonObjectRepr, self).__init__()
        self.o = o
        self.refs = refs
        self.panel = panel

    def render_full(self, oneline=False):
        result = []
        for line in self._render_full(self.o, oneline):
            result.append(line)
        joinchar = "" if oneline else "\n"
        return joinchar.join(result)

    def _render_full(self, o, oneline):
        indent_str = "" if oneline else "  "
        commachr = ", " if oneline else ""
        if isinstance(o, (str, int, float, bytes)):
            yield escape_markup(repr(o))

        elif isinstance(o, (list, tuple)):
            yield escape_markup("[") if isinstance(o, list) else "("
            for index, entry in enumerate(o):
                is_last = index == len(o) - 1
                lines = list(self._render_full(entry, oneline))
                for indexline, line in enumerate(lines):
                    is_last_indexline = indexline == len(lines) - 1
                    comma = commachr if (is_last_indexline and not is_last) else ""
                    yield indent_str + line + comma
            yield escape_markup("]") if isinstance(o, list) else ")"

        elif self.is_pyobject(o):
            yield self.convert_pyobject(o)

        elif isinstance(o, dict):
            yield "{"
            items = list(o.items())
            for index, (key, entry) in enumerate(items):
                is_last = index == len(items) - 1
                repr_key = list(self._render_full(key, oneline))[0]
                lines = list(self._render_full(entry, oneline))
                for indexline, line in enumerate(lines):
                    is_last_indexline = indexline == len(lines) - 1
                    comma = commachr if (is_last_indexline and not is_last) else ""
                    if indexline == 0:
                        yield indent_str + repr_key + ": " + line + comma
                    else:
                        yield indent_str + line + comma
            yield "}"

        elif o is None:
            yield "[i][color=#909090]None[/color][/i]"
        else:
            yield "<missing repr for {}>".format(type(o))

    def is_pyobject(self, o):
        return isinstance(o, dict) and o.get("__pyobject__")

    def convert_pyobject(self, o):
        pyo = o["__pyobject__"]
        ref = self.panel.create_ref(o)
        if ref:
            text = "<{} object at 0x{:x}>".format(
                pyo["type"], pyo["id"]
            )
            return "[color=#03A9F4][ref={}]{}[/ref][/color]".format(
                ref, escape_markup(text))
        else:
            return "<{} object>".format(pyo["type"])


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
            text = pyr.render_full(oneline=True)[:256]
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
