__all__ = ['KivyTreePanel']

import json

from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty, ObjectProperty, ListProperty, NumericProperty,
    BooleanProperty, DictProperty
)

from inspector.controller import ctl


KV = '''
#:import dp kivy.metrics.dp

<KivyTreeItem>:
    indent: dp(15)
    Widget:
        size_hint_x: None
        width: root.indent * root.depth

    InspectorIconButton:
        text: '\ue804' if not root.closed else '\ue805'
        size_hint_x: None
        width: self.height
        state: 'normal' if root.closed else 'down'
        disabled: not root.have_children or root.widget_uid == 0
        opacity: 1 if not self.disabled else 0

        on_release:
            root.toggle()

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
            size_hint_y: None

        RecycleView:
            data: root.items
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            viewclass: 'KivyTreeItem'

            RecycleBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(4)
                spacing: dp(4)
                default_size_hint: 1, None
                default_size: None, dp(24)
'''


class KivyTreeItem(BoxLayout):
    name = StringProperty()
    indent = NumericProperty()
    depth = NumericProperty()
    closed = BooleanProperty(True)
    manager = ObjectProperty()
    visible = BooleanProperty()
    widget_uid = NumericProperty()
    have_children = BooleanProperty()

    def toggle(self):
        self.manager._toggle(self.widget_uid)


class KivyTreePanel(TabbedPanelItem):
    info = StringProperty()
    app = ObjectProperty()
    tree = DictProperty()
    items = ListProperty()
    opened = ListProperty()
    flag = BooleanProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_info, 1)

    def fetch_info(self, dt):
        ctl.request('/kivy/tree', self._parse_info)

    def _parse_info(self, status, response):
        self.tree = response
        print(self.opened)
        self._tree = response['tree']
        if not self.opened:
            self.opened.append(0)
        self.flag = not self.flag

    def on_flag(self, *args):
        self.items = self._parse_tree(self._tree, 0, [])

    def _parse_tree(self, root, depth, result):
        if not root:
            return

        node, children = root
        if node:
            if isinstance(node, dict):
                cls = node['__pyobject__']['type']
                uid = node['__pyobject__']['id']
                name = '<{}@{}>'.format(cls, uid)
            else:
                name = node
                uid = 0
            closed = uid not in self.opened

            node = {
                'name': name,
                'manager': self,
                'widget_uid': uid,
                'depth': depth,
                'closed': closed,
                'have_children': bool(children)
            }
            result.append(node)

            if not closed:
                for widget in children:
                    self._parse_tree(widget, depth + 1, result)
        return result

    def _toggle(self, uid):
        opened = self.opened
        if uid not in opened:
            opened.append(uid)
        else:
            opened.remove(uid)
        self.flag = not self.flag

Builder.load_string(KV)
