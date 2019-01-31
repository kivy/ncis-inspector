from kivy.factory import Factory as F
from kivy.lang import Builder

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.widgets.python_panel
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

        BoxLayout:
            orientation: 'vertical'

            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                TextInput:
                    multiline: False
                    size_hint_y: None
                    height: self.minimum_height
                    on_text_validate: app.target_ip = self.text

                TextInput:
                    multiline: False
                    size_hint_y: None
                    height: self.minimum_height
                    on_text_validate: app.target_port = int(self.text)

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