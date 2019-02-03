from ast import literal_eval
from kivy.factory import Factory as F
from kivy.lang import Builder
from kivy.properties import (
    NumericProperty, ObjectProperty, ConfigParserProperty, StringProperty)

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
        col_ratios: root.split_ratios
        on_col_ratios: root.split_ratios = self.col_ratios

        on_resize_complete: app.config.write()

        KivyTreePanel:
            on_widget_selected: root.widget_selected = args[1]
            highlight_widget: root.widget_selected

        KivyPropertiesPanel:
            widget_uid: root.widget_selected
            on_widget_selected: root.widget_selected = args[1]
            on_property_selected: root.obj, root.propertyname = args[1], args[2]

        PythonObjectPanel:
            obj: root.obj
""")

def float_list(value):
    if isinstance(value, (list, tuple)):
        return value
    else:
        return literal_eval(value)


class KivyInspectorView(F.RelativeLayout):
    ICON = "kivy.png"
    widget_selected = NumericProperty(None, allownone=True)
    obj = ObjectProperty(None, allownone=True)
    propertyname = StringProperty()
    split_ratios = ConfigParserProperty(
        [.2, .5, .3], 'kivy', 'view_split', 'app',
        val_type=float_list
    )
