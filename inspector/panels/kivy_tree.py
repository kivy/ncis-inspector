__all__ = ['KivyTreePanel']

import json

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty, ObjectProperty, ListProperty, NumericProperty,
    BooleanProperty, DictProperty
)

from inspector.controller import ctl


Builder.load_string('''
<ButtonLabel@ButtonBehavior+Label,ToggleButtonLabel@ToggleButtonBehavior+Label>:

<WidgetTreeItem>:
    indent: '15dp'

    BoxLayout:
        Widget:
            size_hint_x: None
            width: root.indent * root.depth
        ButtonLabel:
            text: 'v'
            size_hint_x: None
            width: self.height
            state: 'normal' if root.closed else 'down'

            on_state:
                root.closed = self.state == 'normal'

            canvas.before:
                PushMatrix
                Rotate:
                    origin: self.center
                    angle: 90 if root.closed else 0

            canvas.after:
                PopMatrix

        Label:
            text: root.name
            text_size: self.width, None
            halign: 'left'


<KivyTreePanel>:
    text: 'kivy tree'
    BoxLayout:
        orientation: 'vertical'
        TextInput:
            text: root.info
            multiline: False
            height: self.minimum_height

        RecycleView:
            data: [x for x in root.items]
            viewclass: WidgetTreeItem

            RecycleBoxLayout:
                size_hint_y: None
                heihgt: self.minimum_height
                default_size_hint: 1, None
                default_size: 0, '48dp'
''')


class WidgetTreeItem(Label):
    indent = NumericProperty()
    depth = NumericProperty()
    closed = BooleanProperty(True)


class KivyTreePanel(TabbedPanelItem):
    info = StringProperty()
    app = ObjectProperty()
    tree = DictProperty()
    items = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_info, 1)

    def fetch_info(self, dt):
        ctl.request('/kivy/tree', self._parse_info)

    def _parse_info(self, status, response):
        self.tree = response
        self.items = self._parse_tree(response['tree'], 0)

    def _parse_tree(self, root, depth):
        result = []
        if not root:
            return result

        parent, children = root
        if parent:
            result.append({
                'text': parent,
                'closed': True,
                'depth': depth,
                'parent': root
            })

        for widget in children:
            result.extend(self._parse_tree(widget, depth + 1))

        return result
