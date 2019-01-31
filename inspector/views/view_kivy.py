from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.panels.python_info
<KivyInspectorView>:
    SplitterGrid:
        size: root.size
        size_hint: 1, 1

        rows: 1

        SplitterGrid:
            cols: 1
            TabbedPanel:
                do_default_tab: False
                TabbedPanelItem:
                    text: 'capture'

                    Button:
                        text: 'test'

                TabbedPanelItem:
                    text: 'log'

                    TextInput:
                        text: 'test'
                        readonly: True

                TabbedPanelItem:
                    text: 'editor'

                    TextInput:
                        text: 'test'

                TabbedPanelItem:
                    text: 'app state'

                    TextInput:
                        text: '{}'
                        readonly: True

            TextInput:

        TabbedPanel:
            do_default_tab: False
            PythonInfoPanel:

            TabbedPanelItem:
                text: 'widget tree'
                SplitterGrid:
                    cols: 1
                    Button:
                        text: 'test'

                    Button:
                        text: 'test'

            TabbedPanelItem:
                text: 'file tree'
                Button
""")


class KivyInspectorView(F.RelativeLayout):
    pass