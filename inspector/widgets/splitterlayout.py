from kivy.uix.layout import Layout
from kivy.properties import ListProperty, NumericProperty
from math import ceil

__all__ = ['SplitterGrid']


class SplitterGrid(Layout):
    cols = NumericProperty(0)
    rows = NumericProperty(0)
    margin = NumericProperty(10)

    col_ratios = ListProperty()
    row_ratios = ListProperty()

    min_col_width = NumericProperty(50)
    min_row_height = NumericProperty(50)

    def __init__(self, **kwargs):
        super(SplitterGrid, self).__init__(**kwargs)
        self.bind(
            pos=self.do_layout,
            size=self.do_layout,
            cols=self.do_layout,
            rows=self.do_layout,
            col_ratios=self.do_layout,
            row_ratios=self.do_layout
        )
        self.bind(
            cols=self.on_children,
            rows=self.on_children,
        )

    def get_rows_cols(self, *args):
        if self.cols:
            cols = float(self.cols)
            rows = ceil(len(self.children) / cols)

        elif self.rows:
            rows = float(self.rows)
            cols = ceil(len(self.children) / rows)

        else:
            return 0, 0

        return rows, cols

    def on_children(self, *args):
        rows, cols = self.get_rows_cols()

        while rows > len(self.row_ratios):
            self.row_ratios.append(1)
        while rows < len(self.row_ratios):
            self.row_ratios.pop()

        while cols > len(self.col_ratios):
            self.col_ratios.append(1)
        while cols < len(self.col_ratios):
            self.col.pop()

    def on_touch_down(self, touch):
        if super(SplitterGrid, self).on_touch_down(touch):
            return True

        result = False
        if self.collide_point(*touch.pos):
            rows, cols = self.get_rows_cols()
            margin = self.margin
            width = self.internal_width
            height = self.internal_height

            x, y = self.pos

            sum_col_ratios = sum(self.col_ratios)
            sum_row_ratios = sum(self.row_ratios)

            for i, col in enumerate(self.col_ratios):
                x += width * col / sum_col_ratios
                if x < touch.x < x + margin:
                    touch.grab(self)
                    touch.ud['{}_col'.format(id(self))] = i
                    result = True
                    break
                x += margin

            for i, row in enumerate(self.row_ratios):
                y += height * row / sum_row_ratios
                if y < touch.y < y + margin:
                    touch.grab(self)
                    touch.ud['{}_row'.format(id(self))] = i
                    result = True
                    break
                y += margin
        return result

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super(SplitterGrid, self).on_touch_move(touch)
        col = touch.ud.get('{}_col'.format(id(self)))
        row = touch.ud.get('{}_row'.format(id(self)))
        width = self.internal_width
        height = self.internal_height

        min_col_width = self.min_col_width
        min_row_height = self.min_row_height

        sum_col_ratios = sum(self.col_ratios)
        sum_row_ratios = sum(self.row_ratios)

        result = False

        if col is not None:
            dx = touch.dx
            col_pos = self.x + self.margin * col + sum((width * c / sum_col_ratios) for c in self.col_ratios[:col + 1])

            if (dx < 0 and touch.x < col_pos) or (dx > 0 and touch.x > col_pos):

                width_1 = width * (self.col_ratios[col] / sum_col_ratios) + dx
                width_2 = width * (self.col_ratios[col + 1] / sum_col_ratios) - dx

                total_width = width_1 + width_2
                width_1 = max(min_col_width, width_1)
                width_2 = total_width - width_1

                width_2 = max(min_col_width, width_2)
                width_1 = total_width - width_2

                # assume the sum of ratios didn't change
                col_ratios = self.col_ratios[:]
                col_ratios[col] = sum_col_ratios * width_1 / width
                col_ratios[col + 1] = sum_col_ratios * width_2 / width

                self.col_ratios = col_ratios

            result = True

        if row is not None:
            dy = touch.dy
            row_pos = self.y + self.margin * row + sum((height * r / sum_row_ratios) for r in self.row_ratios[:row + 1])
            if (dy < 0 and touch.y < row_pos) or (dy > 0 and touch.y > row_pos):
                height_1 = height * (self.row_ratios[row] / sum_row_ratios) + dy
                height_2 = height * (self.row_ratios[row + 1] / sum_row_ratios) - dy

                total_height = height_1 + height_2
                height_1 = max(min_row_height, height_1)
                height_2 = total_height - height_1

                height_2 = max(min_row_height, height_2)
                height_1 = total_height - height_2

                # assume the sum of ratios didn't change
                row_ratios = self.row_ratios[:]
                row_ratios[row] = sum_row_ratios * height_1 / height
                row_ratios[row + 1] = sum_row_ratios * height_2 / height
                self.row_ratios = row_ratios
            result = True

        if result:
            return True

        return super(SplitterGrid, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super(SplitterGrid, self).on_touch_up(touch)

        col = touch.ud.get('{}_col'.format(id(self)))
        row = touch.ud.get('{}_row'.format(id(self)))
        if col is not None or row is not None:
            touch.ungrab(self)
            return True
        return super(SplitterGrid, self).on_touch_up(touch)

    @property
    def internal_width(self):
        rows, cols = self.get_rows_cols()
        sum_cols = sum(self.col_ratios)
        sum_margins_cols = self.margin * (cols - 1)
        return self.width - sum_margins_cols

    @property
    def internal_height(self):
        rows, cols = self.get_rows_cols()
        sum_rows = sum(self.row_ratios)
        sum_margins_rows = self.margin * (rows - 1)
        return self.height - sum_margins_rows

    def do_layout(self, *args):
        i = 0
        children = self.children

        sum_col_ratios = sum(self.col_ratios)
        sum_row_ratios = sum(self.row_ratios)

        y = self.y
        width = self.internal_width
        height = self.internal_height

        margin = self.margin

        for rr in self.row_ratios:
            x = self.x
            if not self.col_ratios:
                continue
            for cr in self.col_ratios:
                w = children[i]
                i += 1
                w.width = width * cr / sum_col_ratios
                w.height = height * rr / sum_row_ratios
                w.pos = x, y
                x += w.width + margin
                if i >= len(children):
                    return
            y += w.height + margin


if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.factory import Factory as F

    root = SplitterGrid(cols=5)
    for i in range(3):
        for j in range(12):
            root.add_widget(F.Button(text='{}-{}'.format(i, j)))

    runTouchApp(root)
