'''
Font-based ProgressSpinner
==========================
'''

from kivy.lang import Builder
from kivy.properties import (
    NumericProperty, BooleanProperty, StringProperty,
    ListProperty, AliasProperty)
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.metrics import sp

Builder.load_string("""
<ProgressSpinner>:
    color: [.5, .5, .5, .5]
    font_size: sp(30)
    canvas.before:
        PushMatrix
        Rotate:
            origin: self.adjusted_center
            axis: 0, 0, 1
            angle: root.rotation
    canvas.after:
        PopMatrix

    Label:
        font_name: "inspector/data/fonts/ncis.ttf"
        text: root.symbol
        size: self.texture_size
        center: (root.adjusted_center, self.size)[0]
        color: root.color
        font_size: root.font_size
        opacity: root.opacity
""")


class ProgressSpinner(Widget):
    rotation = NumericProperty()
    auto_start = BooleanProperty(True)
    symbol = StringProperty(u"\ue830")
    offset_x = NumericProperty(0)
    offset_y = NumericProperty(0)
    adjusted_center = ListProperty([0, 0])
    active = BooleanProperty(False)

    def on_active(self, instance, active):
        self.stop_spinning()
        if active:
            self.start_spinning()

    def _get_adjusted_center(self):
        w, h = self.size
        x, y = self.pos
        x = int(x + w / 2.)
        y = int(y + h / 2.)
        return x + x % 2, y + y % 2 + sp(0.5)

    adjusted_center = AliasProperty(_get_adjusted_center,
                                    None,
                                    bind=("pos", "size"))

    def on_opacity(self, instance, value):
        if not value:
            self.stop_spinning()
        elif self.auto_start:
            self.start_spinning()

    def on_parent(self, instance, value):
        if value is None:
            self.stop_spinning()
        elif self.auto_start:
            self.start_spinning()

    def start_spinning(self):
        Clock.unschedule(self._rotate)
        Clock.schedule_interval(self._rotate, 1 / 10.)

    def stop_spinning(self):
        Clock.unschedule(self._rotate)
        self.rotation = 0

    def _rotate(self, dt):
        self.rotation = (self.rotation + dt * -360.)


if __name__ == "__main__":
    from kivy.base import runTouchApp
    runTouchApp(Builder.load_string("""
Widget:
    ProgressSpinner:
        pos: 0, 10
        size: 100, 100

    ProgressSpinner:
        pos: 100, 11
        size: 100, 100

    ProgressSpinner:
        pos: 200, 12
        size: 100, 100

    ProgressSpinner:
        pos: 1, 100
        size: 100, 100

    ProgressSpinner:
        pos: 2, 200
        size: 100, 100



    ProgressSpinner:
        pos: 300, 300
        size: sp(100), sp(101)

    ProgressSpinner:
        pos: 300, 400
        size: 100, 102

    ProgressSpinner:
        pos: 400, 400
        size: 102, 100

    ProgressSpinner:
        pos: 400, 300
        size: 102, 100


"""))
