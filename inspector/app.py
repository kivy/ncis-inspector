from inspector.controller import InspectorController
from inspector.widgets.switchcontainer import SwitchContainer
from kivy.factory import Factory as F
from kivy.lang import global_idmap, Builder
from kivy.clock import Clock

Builder.load_string("""
#:import rgba kivy.utils.get_color_from_hex
#:set ins_color_topbar "#03A9F4"
#:set ins_color_leftbar "#01579B"
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
                rgba: rgba(ins_color_topbar)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "NCIS Inspector"
        Button:
            text: "X"
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
                    rgba: rgba(ins_color_leftbar)
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
        from inspector.views.view_kivy import KivyInspectorView
        self.views_cls = {
            KivyInspectorView: None
        }
        self.show_view(KivyInspectorView)

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

