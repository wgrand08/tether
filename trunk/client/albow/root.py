import sys
import pygame
from pygame.locals import *
from pygame.time import get_ticks
import widget
from widget import Widget

mod_cmd = KMOD_LCTRL | KMOD_RCTRL | KMOD_LMETA | KMOD_RMETA
double_click_time = 300 # milliseconds

modifiers = dict(
	shift = False,
	ctrl = False,
	alt = False,
	meta = False,
)

modkeys = {
	K_LSHIFT: 'shift',  K_RSHIFT: 'shift',
	K_LCTRL:  'ctrl',   K_RCTRL:  'ctrl',
	K_LALT:   'alt',    K_RALT:   'alt',
	K_LMETA:  'meta',   K_RMETA:  'meta',
}

def set_modifier(key, value):
	attr = modkeys.get(key)
	if attr:
		modifiers[attr] = value

def add_modifiers(event):
	d = event.dict
	d.update(modifiers)
	d['cmd'] = event.ctrl or event.meta

class RootWidget(Widget):

	#shift = False
	redraw_every_frame = False
	do_draw = False

	def __init__(self, surface):
		Widget.__init__(self, surface.get_rect())
		self.surface = surface
		widget.root_widget = self
	
	def set_timer(self, ms):
		pygame.time.set_timer(USEREVENT, ms)

	def run(self, modal_widget = None):
		modal_widget = modal_widget or self
		was_modal = modal_widget.is_modal
		modal_widget.is_modal = True
		modal_widget.modal_result = None
		mouse_widget = None
		clicked_widget = None
		num_clicks = 0
		last_click_time = 0
		self.do_draw = True
		last_mouse_event = None
		last_mouse_event_handler = None
		while modal_widget.modal_result is None:
			if self.do_draw:
				self.draw_all(self.surface)
				self.do_draw = False
				pygame.display.flip()
			events = [pygame.event.wait()]
			events.extend(pygame.event.get())
			for event in events:
				type = event.type
				if type == QUIT:
					self.quit()
				elif type == MOUSEBUTTONDOWN:
					mouse_widget = self.find_widget(event.pos)
					self.do_draw = True
					t = get_ticks()
					if t - last_click_time <= double_click_time:
						num_clicks += 1
					else:
						num_clicks = 1
					last_click_time = t
					event.dict['num_clicks'] = num_clicks
					#event.dict['shift'] = self.shift
					add_modifiers(event)
					if mouse_widget.is_inside(modal_widget):
						clicked_widget = mouse_widget
						mouse_widget.handle_mouse('mouse_down', event)
						last_mouse_event_handler = mouse_widget
						last_mouse_event = event
				elif type == MOUSEMOTION:
					mouse_widget = self.find_widget(event.pos)
					add_modifiers(event)
					if clicked_widget:
						clicked_widget.handle_mouse('mouse_drag', event)
						last_mouse_event_handler = mouse_widget
					else:
						#event_widget = self.find_widget(event.pos)
						if not mouse_widget.is_inside(modal_widget):
							mouse_widget = modal_widget
						mouse_widget.handle_mouse('mouse_move', event)
						last_mouse_event_handler = mouse_widget
					last_mouse_event = event
				elif type == MOUSEBUTTONUP:
					mouse_widget = self.find_widget(event.pos)
					add_modifiers(event)
					self.do_draw = True
					if clicked_widget:
						clicked_widget.handle_mouse('mouse_up', event)
						last_mouse_event_handler = clicked_widget
						last_mouse_event = event
						clicked_widget = None
				elif type == KEYDOWN:
					key = event.key
					set_modifier(key, True)
					self.do_draw = True
					self.send_key(modal_widget, 'key_down', event)
					if last_mouse_event:
						last_mouse_event_handler.setup_cursor(last_mouse_event)
				elif type == KEYUP:
					key = event.key
					set_modifier(key, False)
					self.do_draw = True
					self.send_key(modal_widget, 'key_up', event)
					if last_mouse_event:
						last_mouse_event_handler.setup_cursor(last_mouse_event)
				elif type == USEREVENT:
					self.do_draw = self.redraw_every_frame
					self.begin_frame()
					if last_mouse_event:
						last_mouse_event_handler.setup_cursor(last_mouse_event)
		modal_widget.is_modal = was_modal
	
	def send_key(self, widget, name, event):
		add_modifiers(event)
		widget.dispatch_key(name, event)
	
	def begin_frame(self):
		pass

	def get_root(self):
		return self

	def has_focus(self):
		return True

	def quit(self):
		sys.exit(0)
