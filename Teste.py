from kivy.app import App

import itertools
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.factory import Factory as F
from typing import Tuple, Iterable
from kivy.clock import Clock

from kivy_garden.draggable import KXDraggableBehavior, KXReorderableBehavior
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

class Cell(KXReorderableBehavior, BoxLayout):
	pass

class Gate(KXDraggableBehavior, Label):
    pass

class Deck(Label):
    board = ObjectProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.opos):
        	card = Gate(text=self.text, size=(50,50))
        	card.start_dragging_from_others_touch(self, touch)
        	return True

class ScrollCircuitX(ScrollView):
	def on_scroll_move(self, touch):
		super().on_scroll_move(touch)
		touch.ud['sv.handled']['y'] = False

class ScrollCircuitY(ScrollView):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	def on_scroll_stop(self, touch, check_children=True):
		super().on_scroll_stop(touch, check_children=False)

class RootWidget(BoxLayout):
	def __init__(self, **kwargs):
		super(RootWidget, self).__init__(**kwargs)
		self.count = 1
	def buttonClicked(self):
		self.ids.circuit_layout.add_widget(Cell())

class EquitableBoxLayout(F.BoxLayout):
    def on_touch_down(self, touch):
        return any([c.dispatch('on_touch_down', touch) for c in self.children])
    def on_touch_move(self, touch):
        return any([c.dispatch('on_touch_move', touch) for c in self.children])
    def on_touch_up(self, touch):
        return any([c.dispatch('on_touch_up', touch) for c in self.children])

class Projeto(App):
	def __init__(self, *args, **kwargs):
		super(Projeto, self).__init__(*args, **kwargs)
		self.window = Window
		self.window.size=(1000,600)
		self.window.clearcolor = (0.17,0.15,0.16,1)

	def build(self):
		return RootWidget()

class RVLikeBehavior:
    viewclass = ObjectProperty()

    def __init__(self, **kwargs):
        self._rv_refresh_params = {}
        self._rv_trigger_refresh = Clock.create_trigger(self._rv_refresh, -1)
        super().__init__(**kwargs)

    def on_viewclass(self, *args):
        self._rv_refresh_params['viewclass'] = None
        self._rv_trigger_refresh()

    def _get_data(self) -> Iterable:
        data = self._rv_refresh_params.get('data')
        return [c.datum for c in reversed(self.children)] if data is None else data

    def _set_data(self, new_data: Iterable):
        self._rv_refresh_params['data'] = new_data
        self._rv_trigger_refresh()

    data = property(_get_data, _set_data)

    def _rv_refresh(self, *args):
        viewclass = self.viewclass
        if not viewclass:
            self.clear_widgets()
            return
        data = self.data
        params = self._rv_refresh_params
        reusable_widgets = '' if 'viewclass' in params else self.children[::-1]
        self.clear_widgets()
        if isinstance(viewclass, str):
            viewclass = F.get(viewclass)
        for datum, w in zip(data, itertools.chain(reusable_widgets, iter(viewclass, None))):
            w.datum = datum
            self.add_widget(w)
        params.clear()
F.register('RVLikeBehavior', cls=RVLikeBehavior)

if __name__ == "__main__":
	Projeto().run()