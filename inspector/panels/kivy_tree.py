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

<ButtonLabel@ButtonBehavior+Label,ToggleButtonLabel@ToggleButtonBehavior+Label>:

<WidgetTreeItem>:
    indent: dp(15)
    Widget:
        size_hint_x: None
        width: root.indent * root.depth

    ToggleButtonLabel:
        text: 'v'
        size_hint_x: None
        width: self.height
        state: 'normal' if root.closed else 'down'

        on_state:
            print(self.state)
            root.toggle(self.state)

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
            size_hint_y: None

        RecycleView:
            data: (root.flag, [x for x in root.items if x['visible']])[1]
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            viewclass: 'WidgetTreeItem'

            RecycleBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(2)
                default_size_hint: 1, None
                default_size: None, dp(38)
'''


class WidgetTreeItem(BoxLayout):
    name = StringProperty()
    indent = NumericProperty()
    depth = NumericProperty()
    closed = BooleanProperty(True)
    manager = ObjectProperty()
    visible = BooleanProperty()
    item_id = NumericProperty()
    widget_uid = StringProperty()

    def toggle(self, state):
        opened = self.manager.opened
        if state == 'down':
            opened.append(self.widget_uid)
            self.closed = False
        else:
            opened.remove(self.widget_uid)
            self.closed = True

        # XXX ok, this is not beautiful, but no better idea at the
        # moment
        found = False
        print(self.item_id)
        for d in self.manager.items:
            print(found, d)
            if found:
                if d['depth'] <= self.depth:
                    print('break')
                    break
                elif d['depth'] == self.depth + 1:
                    d['visible'] = not self.closed
                    print('->', d)

            elif d['item_id'] == self.item_id:
                found = True
        self.manager.flag = not self.manager.flag


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
        self.items = self._parse_tree(response['tree'], 0, 0)

    def _parse_tree(self, root, depth, index):
        result = []
        if not root:
            return result

        parent, children = root
        if parent:
            if isinstance(parent, dict):
                cls = parent['__pyobject__']['type']
                uid = parent['__pyobject__']['id']
                name = '<{}@{}>'.format(cls, uid)
            else:
                name = parent
                uid = None
            closed = str(uid) not in self.opened

            result.append({
                'name': name,
                'manager': self,
                'visible': depth < 1,
                'widget_uid': str(uid),
                'depth': depth,
                # 'closed': closed,
                'item_id': index,
            })
            index += 1

        for widget in children:
            sub = self._parse_tree(widget, depth + 1, index)
            index += len(sub)
            if not closed:
                for s in sub:
                    s['visible'] = True
            result.extend(sub)

        return result


Builder.load_string(KV)
