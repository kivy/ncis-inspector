__all__ = ['KivyTreePanel']

import json

from kivy.factory import Factory as F
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty, ObjectProperty, ListProperty, NumericProperty,
    BooleanProperty, DictProperty
)
from kivy.utils import escape_markup
from ncis_inspector.controller import ctl

Builder.load_string('''
<KivyTreeItem>:
    indent: dp(15)

    canvas.before:
        Color:
            rgba: rgba(NCIS_COLOR_LEFTBAR_ICON_SELECTED if root.highlight else (NCIS_COLOR_LEFTBAR if root.selected else NCIS_COLOR_TRANSPARENT))
        Rectangle:
            pos: -dp(2), -dp(2)
            size: self.width + dp(4), self.height + dp(4)

    BoxLayout:
        x: -self.height + dp(5)
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

        InspectorLabelButton:
            text: root.name
            text_size: self.width, None
            halign: 'left'
            markup: True
            shorten: True
            shorten_from: 'right'
            on_release: root.manager.dispatch('on_widget_selected', root.widget_uid)

<KivyTreePanel>:
    orientation: 'vertical'
    RelativeLayout:
        size_hint_y: None
        height: dp(44)
        TextInput:
            id: ti
            text: root.text_filter
            on_text: root.apply_filter(self.text)
            multiline: False
            padding: dp(40), dp(12)

        InspectorIconLabel:
            text: NCIS_ICON_FINDER
            color: rgba(NCIS_COLOR_TEXT_PLACEHOLDER)
            size_hint_x: None
            width: self.height
            x: self.x
            y: dp(2)

        InspectorIconButton:
            text: NCIS_ICON_CANCEL
            color: rgba(NCIS_COLOR_TEXT_PLACEHOLDER)
            size_hint_x: None
            width: self.height
            right: [ti.right, self.width][0]
            opacity: 1 if root.text_filter else 0
            on_release: root.text_filter = ""

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
''')


class KivyTreeItem(F.RelativeLayout):
    name = StringProperty()
    indent = NumericProperty()
    depth = NumericProperty()
    closed = BooleanProperty(True)
    manager = ObjectProperty()
    visible = BooleanProperty()
    widget_uid = NumericProperty()
    have_children = BooleanProperty()
    selected = BooleanProperty(False)
    highlight = BooleanProperty(False)

    def toggle(self):
        self.manager._toggle(self.widget_uid)


class KivyTreePanel(F.BoxLayout):
    text_filter = StringProperty()
    app = ObjectProperty()
    tree = DictProperty()
    items = ListProperty()
    opened = ListProperty()
    highlight_widget = NumericProperty(None, allownone=True)

    __events__ = ["on_widget_selected"]

    def __init__(self, **kwargs):
        self._tree = None
        super().__init__(**kwargs)
        Clock.schedule_interval(self.fetch_info, 0)

    def fetch_info(self, dt):
        ctl.request('/kivy/tree', self._parse_info)

    def on_highlight_widget(self, *largs):
        self.refresh()

    def apply_filter(self, text_filter):
        self.text_filter = text_filter
        self.refresh()

    def refresh(self, *largs):
        if not self._tree:
            return
        self.items = self._parse_tree(self._tree, 0, [])

    def _parse_info(self, status, response):
        if status != "ok":
            self.items = []
            return
        self.tree = response
        self._tree = response['tree']
        if not self.opened:
            self.opened.append(0)
        self.refresh()

    def _parse_tree(self, root, depth, result):
        if not root:
            return

        text_filter = self.text_filter

        node, children = root
        if node:
            if isinstance(node, dict):
                cls = node['__pyobject__']['type']
                uid = node['__pyobject__']['id']
                name = '{}'.format(cls)
            else:
                name = node.capitalize()
                uid = 0

            closed = uid not in self.opened
            if text_filter:
                closed = False

            node = {
                'name': name,
                'manager': self,
                'widget_uid': uid,
                'depth': depth,
                'closed': closed,
                'have_children': bool(children),
                'highlight': uid == self.highlight_widget,
            }

            if text_filter:
                node['selected'] = text_filter in name
                node['name'] = name.replace(
                    text_filter,
                    '[color=dcb67a]{}[/color]'.format(
                        escape_markup(text_filter)))
            else:
                node['selected'] = False
            result.append(node)

            # if text_filter:
            #     node["have_children"] = False
            #     node["closed"] = False
            #     node["depth"] = 0
            #     if text_filter in name:
            #         result.append(node)
            # else:
            #     result.append(node)

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
        self.refresh()

    def on_widget_selected(self, uid):
        self.highlight_widget = uid