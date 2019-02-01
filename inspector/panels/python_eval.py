__all__ = ['PythonEvalPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from inspector.controller import ctl
from functools import partial


Builder.load_string('''
#:import _ inspector.panels.python_object
#:import _ inspector.panels.python_inspect
#:import mainthread kivy.clock.mainthread
<PythonEvalPanel>:
    GridLayout:
        cols: 1
        spacing: dp(4)

        GridLayout:
            rows: 1
            spacing: dp(4)
            size_hint_y: None
            height: dp(44)

            TextInput:
                multiline: False
                text: root.cmd
                on_text_validate:
                    root.cmd = self.text
                    mainthread(lambda *x: setattr(self, "focus", True))()
                font_size: dp(16)
                padding: dp(12)

            ToggleButton:
                group: "python-eval-type"
                size_hint_x: None
                width: dp(90)
                text: "Eval"
                allow_no_selection: False
                state: "down" if root.eval_type == "eval" else "normal"
                on_state: root.eval_type = "eval" if self.state == "down" else "inspect"
                on_release: root.refresh()

            ToggleButton:
                group: "python-eval-type"
                size_hint_x: None
                width: dp(90)
                text: "Inspect"
                allow_no_selection: False
                on_release: root.refresh()

        SwitchContainer:
            index: 0 if root.eval_type == "eval" else 1
            PythonObjectPanel:
                obj: root.obj if root.eval_type == "eval" else None
                # on_ref_pressed: print(args)
            PythonInspectPanel:
                cmd: root.cmd if root.eval_type == "inspect" else None
''')

class PythonEvalPanel(F.RelativeLayout):
    cmd = StringProperty()
    obj = ObjectProperty(allownone=True)
    eval_type = StringProperty("eval")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.cmd:
            self.refresh()

    def refresh(self, *largs):
        def callback(status, response):
            self.obj = response

        ctl.request(
            '/python/eval',
            callback,
            params={"cmd": self.cmd},
            method="POST")

    def on_cmd(self, *largs):
        self.refresh()
