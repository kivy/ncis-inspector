from kivy.factory import Factory as F
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty

Builder.load_string("""
#:import _ inspector.widgets.splitterlayout
#:import _ inspector.panels.python_info
#:import _ inspector.panels.kivy_tree
#:import _ inspector.panels.kivy_properties
<KivyInspectorView>:
    SplitterGrid:
        size: root.size
        size_hint: 1, 1
        margin: dp(5)
        rows: 1

        PythonObjectPanel:
            obj: root.obj

        KivyPropertiesPanel:
            widget_uid: root.widget_selected
            on_widget_selected: root.widget_selected = args[1]
            on_value_selected: root.obj = args[1]

        KivyTreePanel:
            on_widget_selected: root.widget_selected = args[1]
            highlight_widget: root.widget_selected
""")


class KivyInspectorView(F.RelativeLayout):
    ICON = "kivy.png"
    widget_selected = NumericProperty(None, allownone=True)
    obj = ObjectProperty(None, allownone=True)