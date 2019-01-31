from inspector.controller import InspectorController
from inspector.widgets.switchcontainer import SwitchContainer
from kivy.factory import Factory as F
from kivy.lang import global_idmap, Builder
from kivy.clock import Clock
from kivy.properties import DictProperty, ObjectProperty, BooleanProperty
from functools import partial

Builder.load_string("""
#:import rgba kivy.utils.get_color_from_hex
#:set NCIS_COLOR_TOPBAR "#0D47A1"
#:set NCIS_COLOR_LEFTBAR "#0D47A1"
#:set NCIS_COLOR_LEFTBAR_ICON_SELECTED "#64B5F6"
#:set NCIS_COLOR_TRANSPARENT "#00000000"

#:set NCIS_ICON_CANCEL "\uE800"
#:set NCIS_ICON_SPINNER "\uE830"
#:set NCIS_ICON_UNHAPPY "\uE802"

<InspectorIconLabel@Label>:
    font_name: "inspector/data/ncis.ttf"

<InspectorIconButton@ButtonBehavior+Label>:
    font_name: "inspector/data/ncis.ttf"

<InspectorImageButton@ButtonBehavior+Image>:
    size_hint_y: None
    height: self.width

<InspectorLeftbarImageButton>:
    selected: isinstance(ins.view, root.view)
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
        size_hint_y: None
        height: dp(44)
        spacing: dp(4)
        canvas.before:
            Color:
                rgba: rgba(NCIS_COLOR_TOPBAR)
            Rectangle:
                pos: self.pos
                size: self.size
        Widget:
            size_hint_x: None
            width: self.height
        Label:
            text: "NCIS Inspector"
        InspectorIconButton:
            text: NCIS_ICON_CANCEL
            on_release: ins.disconnect()
            size_hint_x: None
            width: self.height

    GridLayout:
        rows: 1

        GridLayout:
            cols: 1
            size_hint_x: None
            width: dp(44)
            id: view_icons
            padding: dp(8)
            spacing: dp(16)
            canvas.before:
                Color:
                    rgba: rgba(NCIS_COLOR_LEFTBAR)
                Rectangle:
                    pos: self.pos
                    size: self.size

        RelativeLayout:
            id: view_container


<InspectorApplicationRoot>:
    index: int(ins.is_connected)
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
        self.views_cls = {
            PythonInspectorView: None,
            KivyInspectorView: None
        }
        self.show_view(PythonInspectorView)

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
        self.ids.view_container.clear_widgets()
        self.ids.view_container.add_widget(instance)
        InspectorController.instance().view = instance


class InspectorApplicationRoot(F.SwitchContainer):
    def __init__(self, **kwargs):
        self.ctl = InspectorController.instance()
        global_idmap["ins"] = self.ctl
        super(InspectorApplicationRoot, self).__init__(**kwargs)

