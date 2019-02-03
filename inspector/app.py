from inspector.controller import InspectorController
from inspector.widgets.switchcontainer import SwitchContainer
from kivy.factory import Factory as F
from kivy.lang import global_idmap, Builder
from kivy.clock import Clock
from kivy.properties import DictProperty, ObjectProperty, BooleanProperty
from functools import partial
import os

Builder.load_string("""
#:import rgba kivy.utils.get_color_from_hex
#:import _ inspector.widgets.progressspinner
#:set NCIS_COLOR_LEFTBAR "#2f333d"
#:set NCIS_COLOR_LEFTBAR_ICON_SELECTED "#373c48"
#:set NCIS_COLOR_TRANSPARENT "#00000000"
#:set NCIS_COLOR_BACKGROUND "#21252b"
#:set NCIS_COLOR_TEXT_PLACEHOLDER "#808080"
#:set NCIS_COLOR_TEXT_HIGHLIGHT "#dcb67a"

#:set NCIS_ICON_CANCEL "\uE800"
#:set NCIS_ICON_SPINNER "\uE830"
#:set NCIS_ICON_UNHAPPY "\uE802"
#:set NCIS_ICON_DOWNARROW "\uF103"
#:set NCIS_ICON_TRASH "\uF1F8"
#:set NCIS_ICON_SETTINGS "\uE807"
#:set NCIS_ICON_EXIT "\uE806"
#:set NCIS_ICON_FINDER "\uE80A"

<InspectorLabelButton@ButtonBehavior+Label>:

<InspectorIconLabel@Label>:
    font_name: "inspector/data/ncis.ttf"

<InspectorIconButton@ButtonBehavior+Label>:
    font_name: "inspector/data/ncis.ttf"

<InspectorImageButton@ButtonBehavior+Image>:
    size_hint_y: None
    height: self.width

<InspectorButton@ButtonBehavior+Label>:
    canvas.before:
        Color:
            rgba: rgba(NCIS_COLOR_LEFTBAR) if root.state == "normal" else rgba(NCIS_COLOR_LEFTBAR_ICON_SELECTED)
        Rectangle:
            pos: self.pos
            size: self.size

<InspectorLeftbarImageButton>:
    selected: isinstance(ins.view, root.view)
    opacity: 1 if self.selected else 0.5
    canvas.before:
        Color:
            rgba: rgba(NCIS_COLOR_LEFTBAR_ICON_SELECTED if self.selected else NCIS_COLOR_TRANSPARENT)
        Rectangle:
            pos: self.x - dp(8), self.y - dp(8)
            size: self.width + dp(16), self.height + dp(16)

<InspectorConnection@AnchorLayout>:
    disabled: ins.is_connecting
    GridLayout:
        cols: 1
        spacing: dp(4)
        size_hint_y: None
        size_hint_max_x: dp(250)
        height: self.minimum_height
        Label:
            text: "NCIS - Connect to"
            size_hint_y: None
            height: dp(44)

        Label:
            text: ins.error

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(4)

            Label:
                text: "Host"
                size_hint_x: None
                width: dp(80)


            TextInput:
                multiline: False
                on_text_validate: ins.target_host = self.text
                padding: dp(12)
                font_size: dp(16)
                text: ins.target_host
                hint_text: "192.168.1.x"

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(4)

            Label:
                text: "Port"
                size_hint_x: None
                width: dp(80)

            TextInput:
                multiline: False
                text: str(ins.target_port)
                on_text_validate: ins.target_port = int(self.text)
                padding: dp(12)
                font_size: dp(16)

        Button:
            text: "Connect"
            size_hint_y: None
            height: dp(44)
            on_release: ins.connect()

<InspectorViews>:
    cols: 1

    GridLayout:
        rows: 1

        GridLayout:
            cols: 1
            size_hint_x: None
            width: dp(48)
            padding: dp(8)
            canvas.before:
                Color:
                    rgba: rgba(NCIS_COLOR_LEFTBAR)
                Rectangle:
                    pos: self.pos
                    size: self.size

            GridLayout:
                cols: 1
                id: view_icons
                spacing: dp(16)

            GridLayout:
                cols: 1
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height
                InspectorIconButton:
                    text: NCIS_ICON_EXIT
                    on_release: ins.disconnect()
                    size_hint_y: None
                    height: self.width

        RelativeLayout:
            id: view_container


<InspectorApplicationRoot>:
    index: int(ins.is_connected)
    canvas.before:
        Color:
            rgba: rgba(NCIS_COLOR_BACKGROUND)
        Rectangle:
            pos: self.pos
            size: self.size
    InspectorConnection
    InspectorViews
""")


class InspectorLeftbarImageButton(F.InspectorImageButton):
    view = ObjectProperty(allownone=True)
    selected = BooleanProperty(False)


class InspectorViews(F.GridLayout):
    views_cls = DictProperty()

    def __init__(self, **kwargs):
        _ = F.InspectorImageButton()
        super(InspectorViews, self).__init__(**kwargs)
        Clock.schedule_once(self.discover_views)

    def discover_views(self, *largs):
        # TODO make it dynamic
        from inspector.views.view_python import PythonInspectorView
        from inspector.views.view_kivy import KivyInspectorView
        from inspector.views.view_stdio import StdioInspectorView
        self.views_cls = {
            PythonInspectorView: None,
            KivyInspectorView: None,
            StdioInspectorView: None
        }

        default_view = os.environ.get("INSPECTOR_VIEW", "PythonInspectorView")
        self.show_view(locals().get(default_view))

        # icons
        for view in self.views_cls.keys():
            icon = "inspector/data/icons/{}".format(view.ICON)
            btn = F.InspectorLeftbarImageButton(
                source=icon,
                view=view,
                on_release=partial(self.show_view, view)
            )
            self.ids.view_icons.add_widget(btn)

    def show_view(self, cls, *largs):
        instance = self.views_cls.get(cls)
        if not instance:
            instance = self.views_cls[cls] = cls()
        c = self.ids.view_container
        if c.children:
            if hasattr(c.children[0], "leave"):
                c.children[0].leave()
        c.clear_widgets()
        c.add_widget(instance)
        InspectorController.instance().view = instance
        if hasattr(instance, "enter"):
            instance.enter()

class InspectorApplicationRoot(F.SwitchContainer):
    def __init__(self, **kwargs):
        self.ctl = InspectorController.instance()
        global_idmap["ins"] = self.ctl
        super(InspectorApplicationRoot, self).__init__(**kwargs)

