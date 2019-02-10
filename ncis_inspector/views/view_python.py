from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import _ ncis_inspector.widgets.splitterlayout
#:import _ ncis_inspector.panels.python_modules
#:import _ ncis_inspector.panels.python_eval

<PythonInspectorView>:
    PythonEvalPanel:
        id: python_eval_module
""")

class PythonInspectorView(F.RelativeLayout):
    ICON = "python.png"
    def inspect_module(self, module):
        self.ids.python_eval_module.cmd = "sys.modules['%s']" % module
        self.ids.tp.switch_to(self.ids.tph_eval)

    def enter(self):
        self.ids.python_eval_module.focus()