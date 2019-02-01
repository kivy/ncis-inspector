from kivy.factory import Factory as F
from kivy.lang import Builder
from kivy.properties import NumericProperty
from inspector.controller import ctl
from json import loads

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.panels.python_modules
#:import _ inspector.panels.python_eval

<-LineStdioInspectorView@Label>:
    font_name: "RobotoMono-Regular"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.texture_size
            texture: self.texture

<StdioInspectorView>:
    # approximation of the number of character
    # works only for RobotoMono-Regular at default font_size.
    line_character_max: int(self.width / dp(9)) - 1
    RecycleView:
        id: rv
        viewclass: "LineStdioInspectorView"
        RecycleBoxLayout:
            spacing: dp(4)
            padding: dp(8)
            default_size: None, dp(14)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
""")

class StdioInspectorView(F.RelativeLayout):
    ICON = "logs.png"
    line_character_max = NumericProperty(256)

    def __init__(self, **kwargs):
        self.rv_data = []
        self.lines = []
        self.pipes = {
            "stdout": "",
            "stderr": ""
        }
        super(StdioInspectorView, self).__init__(**kwargs)
        ctl.stream_bind(self.callback, events=["stdout", "stderr"])

    def callback(self, event):
        evname = event.event
        data = loads("".join(event.data))
        if evname == "stdout":
            self.append_to("stdout", data)
        elif evname == "stderr":
            self.append_to("stderr", data)

    def append_to(self, pipename, data):
        lines = data.split("\n")
        self.pipes[pipename] += lines[0]
        if len(lines) > 1:
            self.append_line(self.pipes[pipename])
            for line in lines[1:-1]:
                self.append_line(line)
            self.pipes[pipename] = lines[-1]
        self.refresh()

    def append_line(self, line):
        self.lines.append(line)
        self.rv_data.extend(list(self._wrap_line(line)))

    def on_line_character_max(self, *largs):
        self.refresh(force=True)

    def refresh(self, force=False):
        if force:
            rv_data = []
            for line in self.lines:
                rv_data.extend(list(self._wrap_line(line)))
            self.rv_data = rv_data
        lastline = list(self._wrap_line(self.pipes["stdout"]))
        self.ids.rv.data = self.rv_data + lastline

    def _wrap_line(self, line):
        n = max(20, self.line_character_max)
        for i in range(0, len(line), n):
            yield {
                "text": line[i:i+n]
            }