from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.panels.python_modules
#:import _ inspector.panels.python_eval

<PythonInspectorView>:
    TabbedPanel:
        do_default_tab: False
        id: tp
        TabbedPanelItem:
            id: tph_modules
            text: 'Modules'
            PythonModulesPanel:
                on_module_selected: root.inspect_module(args[1])

        TabbedPanelItem:
            text: 'Eval'
            id: tph_eval
            PythonEvalPanel:
                id: python_eval_module

""")

class PythonInspectorView(F.RelativeLayout):
    def inspect_module(self, module):
        self.ids.python_eval_module.cmd = "sys.modules['%s']" % module
        self.ids.tp.switch_to(self.ids.tph_eval)