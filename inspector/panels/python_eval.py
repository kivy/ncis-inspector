__all__ = ['PythonEvalPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial


Builder.load_string('''
#:import _ inspector.panels.python_object
<PythonEvalPanel>:
    GridLayout:
        cols: 1
        spacing: dp(4)
        TextInput:
            multiline: False
            text: root.cmd
            on_text: root.cmd = self.text
            size_hint_y: None
            height: dp(44)
            font_size: dp(16)
            padding: dp(12)

        PythonObjectPanel:
            obj: root.obj
''')

class PythonEvalPanel(F.RelativeLayout):
    cmd = StringProperty()
    obj = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.cmd:
            self.refresh()

    def refresh(self, *largs):
        def callback(status, response):
            self.obj = response
            print("self", self, self.obj)

        ctl.request(
            '/python/eval',
            callback,
            method="POST")

    def on_cmd(self, *largs):
        self.refresh()
