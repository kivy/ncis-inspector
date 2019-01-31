from inspector.controller import InspectorController
from inspector.widgets.switchcontainer import SwitchContainer
from kivy.factory import Factory as F
from kivy.lang import global_idmap, Builder
from kivy.clock import Clock

Builder.load_string("""
#:import rgba kivy.utils.get_color_from_hex
#:set NCIS_COLOR_TOPBAR "#03A9F4"
#:set NCIS_COLOR_LEFTBAR "#01579B"

#:set NCIS_ICON_CANCEL "\uE800"
#:set NCIS_ICON_SPINNER "\uE830"
#:set NCIS_ICON_UNHAPPY "\uE802"

<InspectorIconLabel@Label>:
    font_name: "inspector/data/ncis.ttf"

<InspectorIconButton@Button>:
    font_name: "inspector/data/ncis.ttf"

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


class InspectorViews(F.GridLayout):
    def __init__(self, **kwargs):
        super(InspectorViews, self).__init__(**kwargs)
        self.views_cls = None
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

    def show_view(self, cls):
        instance = self.views_cls.get(cls)
        if not instance:
            instance = self.views_cls[cls] = cls()
        self.ids.view_container.clear_widgets()
        self.ids.view_container.add_widget(instance)

class InspectorApplicationRoot(F.SwitchContainer):
    def __init__(self, **kwargs):
        self.ctl = InspectorController.instance()
        global_idmap["ins"] = self.ctl
        super(InspectorApplicationRoot, self).__init__(**kwargs)

