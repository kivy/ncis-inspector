__all__ = ['KivyPropertiesPanel']

import json

from kivy.factory import Factory as F
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    StringProperty, ObjectProperty, ListProperty, NumericProperty,
    BooleanProperty, DictProperty
)
from kivy.utils import escape_markup

from inspector.controller import ctl

Builder.load_string('''
<KivyPropertiesItem>:
    canvas.before:
        Color:
            rgba: rgba(NCIS_COLOR_LEFTBAR_ICON_SELECTED if root.highlight else NCIS_COLOR_TRANSPARENT)
        Rectangle:
            pos: self.x - dp(2), self.y - dp(2)
            size: self.width + dp(4), self.height + dp(4)

    InspectorLabelButton:
        text: root.key
        text_size: self.width, None
        halign: 'left'
        markup: True
        shorten: True
        shorten_from: 'right'
        size_hint_x: None
        width: dp(100)
        on_release: root.on_property_selected(root.key, root.value)

    PythonObjectPanel:
        oneline: True
        obj: root.value
        on_ref_pressed: root.on_ref_pressed(args[1])

<KivyPropertiesPanel>:
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
        id: rv
        scroll_type: ['bars', 'content']
        bar_width: dp(10)
        viewclass: 'KivyPropertiesItem'

        RecycleBoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: dp(4)
            spacing: dp(4)
            default_size_hint: 1, None
            default_size: None, dp(24)
''')


class KivyPropertiesItem(F.BoxLayout):
    key = StringProperty()
    value = ObjectProperty(None, allownone=True)
    highlight = BooleanProperty()
    on_ref_pressed = ObjectProperty(None, allownone=True)


class KivyPropertiesPanel(F.BoxLayout):
    text_filter = StringProperty()
    app = ObjectProperty()
    tree = DictProperty()
    items = ListProperty()
    opened = ListProperty()
    widget_uid = NumericProperty(None, allownone=True)
    response = ObjectProperty(None, allownone=True)
    highlight_key = StringProperty(None, allownone=True)

    __events__ = [
        "on_value_selected",
        "on_widget_selected",
        "on_property_selected"]

    def on_widget_uid(self, *largs):
        self.fetch_info()

    def fetch_info(self, *largs):
        ctl.request(
            '/kivy/inspect/{}'.format(self.widget_uid),
            self._on_inspect_response)

    def apply_filter(self, text_filter):
        self.text_filter = text_filter
        self.refresh()

    def _on_inspect_response(self, status, response):
        self.response = response
        self.refresh()

    def refresh(self):
        data = []
        text_filter = self.text_filter
        response = self.response
        if not response:
            self.ids.rv.data = []
            return
        for key in sorted(response.keys()):
            if text_filter and text_filter not in key:
                continue
            key_txt = key
            if text_filter:
                key_txt = key.replace(
                    text_filter,
                    '[color=dcb67a]{}[/color]'.format(
                        escape_markup(text_filter)))
            data.append({
                "key": key_txt,
                "value": response[key],
                "on_ref_pressed": self._on_ref_pressed,
                "on_property_selected": self._on_property_selected,
                "highlight": key == self.highlight_key
            })
        self.ids.rv.data = data

    def _on_ref_pressed(self, ref):
        if isinstance(ref, dict) and ref.get("__pyobject__"):
            uid = ref["__pyobject__"]["id"]
            if not uid:
                return
            self.dispatch("on_widget_selected", uid)

    def _on_property_selected(self, key, value):
        self.highlight_key = key
        self.dispatch("on_value_selected", value)
        self.refresh()

    def on_widget_selected(self, uid):
        pass

    def on_property_selected(self, uid):
        pass

    def on_value_selected(self, value):
        pass