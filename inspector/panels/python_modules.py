__all__ = ['PythonModulesPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial


Builder.load_string('''
<PythonModuleEntry@ButtonBehavior+Label>:
    callback: None
    text_size: self.width - dp(20), None
    on_release: root.callback()

<PythonModulesPanel>:
    GridLayout:
        cols: 1
        GridLayout:
            rows: 1
            size_hint_y: None
            height: dp(44)
            Label:
                text: "{} modules loaded".format(len(rv.data))
        RecycleView:
            id: rv
            viewclass: "PythonModuleEntry"
            RecycleBoxLayout:
                id: bl
                spacing: dp(4)
                default_size: None, dp(44)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
''')

class PythonModulesPanel(F.RelativeLayout):
    __events__ = ["on_module_selected"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh()

    def refresh(self):
        ctl.request('/python/modules', self._parse_info)

    def _parse_info(self, status, response):
        data = [
            {
                "text": entry,
                "callback": partial(self.dispatch, "on_module_selected", entry)
            }
            for entry in sorted(response)
        ]
        self.ids.rv.data = data

    def on_module_selected(self, *largs):
        pass
