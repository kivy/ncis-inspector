from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.panels.python_modules

<PythonInspectorView>:
    TabbedPanel:
        do_default_tab: False
        TabbedPanelItem:
            text: 'Modules'

            PythonModulesPanel:
                on_module_selected: root.inspect_module(args[1])

""")

class PythonInspectorView(F.RelativeLayout):
    def inspect_module(self, module):
        print("TODO: inspect module")