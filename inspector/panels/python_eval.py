__all__ = ['PythonEvalPanel']

from kivy.factory import Factory as F
from kivy.properties import StringProperty, ObjectProperty
from kivy.clock import Clock, mainthread
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

            RelativeLayout:
                TextInput:
                    id: ti
                    multiline: False
                    text: root.cmd
                    on_text: root._on_text(self.text)
                    on_text_validate: root._on_text_validate(self.text)
                    font_size: dp(16)
                    padding: dp(12)
                InspectorLeftLabel:
                    text: root.error
                    color: rgba("#F44336")
                    font_size: dp(10)
                    size_hint_y: None
                    height: dp(20)
                    y: 0
                    x: dp(12)

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
            PythonInspectPanel:
                cmd: root.cmd if root.eval_type == "inspect" else None
''')

class PythonEvalPanel(F.RelativeLayout):
    cmd = StringProperty()
    obj = ObjectProperty(allownone=True)
    eval_type = StringProperty("eval")
    error = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.cmd:
            self.refresh()

    def refresh(self, *largs):
        def callback(status, response):
            if status == "ok":
                self.error = ""
                self.obj = response
            elif status == "error":
                self.error = response

        self.error = ""
        ctl.request(
            '/python/eval',
            callback,
            params={"cmd": self.cmd},
            method="POST")

    def on_cmd(self, *largs):
        self.refresh()

    def focus(self):
        self.ids.ti.focus = True

    def _on_text(self, text):
        self.error = ""
        self.tmptext = text
        Clock.unschedule(self._on_text_validate_tmp)
        Clock.schedule_once(self._on_text_validate_tmp, 0.3)

    @mainthread
    def _on_text_validate(self, text):
        Clock.unschedule(self._on_text_validate_tmp)
        self.cmd = text
        self.refresh()
        self.focus = True

    def _on_text_validate_tmp(self, *largs):
        self._on_text_validate(self.tmptext)

