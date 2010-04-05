from pygame import Rect, draw
from pygame.mouse import set_cursor
from pygame.cursors import arrow as arrow_cursor
from vectors import add, subtract
from utils import frame_rect
import theme
from theme import ThemeProperty, FontProperty

debug_rect = False

root_widget = None
current_cursor = None

class Widget(object):
	#  rect            Rect       bounds in parent's coordinates
	#  parent          Widget     containing widget
	#  subwidgets      [Widget]   contained widgets
	#  focus_switch    Widget     subwidget to receive key events
	#  fg_color        color      or None to inherit from parent
	#  bg_color        color      to fill background, or None
	#  visible         boolean
	#  border_width    int        width of border to draw around widget, or None
	#  border_color    color      or None to use widget foreground color

	font = FontProperty('font')
	fg_color = ThemeProperty('fg_color')
	bg_color = ThemeProperty('bg_color')
	border_width = ThemeProperty('border_width')
	border_color = ThemeProperty('border_color')
	margin = ThemeProperty('margin')

	visible = True

	def __init__(self, rect = None, **kwds):
		self.rect = rect or Rect(0, 0, 100, 100)
		self.parent = None
		self.subwidgets = []
		self.focus_switch = None
		self.is_modal = False
		self.set(**kwds)
	
	def set(self, **kwds):
		for name, value in kwds.iteritems():
			if not hasattr(self, name):
				raise TypeError("Unexpected keyword argument '%s'" % name)
			setattr(self, name, value)
	
	def add(self, widget):
		widget.set_parent(self)
	
	def remove(self, widget):
		if widget in self.subwidgets:
			widget.set_parent(None)
	
	def set_parent(self, parent):
		if parent is not self.parent:
			if self.parent:
				self.parent._remove(self)
			self.parent = parent
			if parent:
				parent._add(self)
	
	def _add(self, widget):
		self.subwidgets.append(widget)
	
	def _remove(self, widget):
		self.subwidgets.remove(widget)
		if self.focus_switch is widget:
			self.focus_switch = None
	
	def draw_all(self, surface):
		if self.visible:
			bg = self.bg_color
			if bg:
				surface.fill(bg)
			self.draw(surface)
			bw = self.border_width
			if bw:
				bc = self.border_color or self.fg_color
				r = surface.get_rect()
				#r.inflate_ip(1 - bw, 1 - bw)
				#draw.rect(surface, bc, r, bw)
				frame_rect(surface, bc, r, bw)
			for widget in self.subwidgets:
				if debug_rect:
					print "Widget: Drawing subwidget %s of %s with rect %s" % (
						widget, self, widget.rect)
				try:
					sub = surface.subsurface(widget.rect)
				except ValueError:
					raise ValueError("Widget %s %s outside parent %s %s" % (
						widget, widget.rect, self, self.rect))
				widget.draw_all(sub)
			self.draw_over(surface)
	
	def draw(self, surface):
		pass
	
	def draw_over(self, surface):
		pass

	def find_widget(self, pos):
		for widget in self.subwidgets[::-1]:
			if widget.visible:
				r = widget.rect
				if r.collidepoint(pos):
					return widget.find_widget(subtract(pos, r.topleft))
		return self
	
	def handle_mouse(self, name, event):
		event.dict['local'] = self.global_to_local(event.pos)
		self.call_handler(name, event)
		self.setup_cursor(event)
	
	def setup_cursor(self, event):
		global current_cursor
		cursor = self.get_cursor(event) or arrow_cursor
		if cursor is not current_cursor:
			set_cursor(*cursor)
			current_cursor = cursor
	
	def dispatch_key(self, name, event):
		if self.visible:
			widget = self.focus_switch
			if widget:
				widget.dispatch_key(name, event)
			else:
				self.call_handler(name, event)
		else:
			self.call_parent_handler(name, event)

	def call_handler(self, name, *args):
		method = getattr(self, name, None)
		if method:
			method(*args)
			return True
		else:
			return False
	
	def call_parent_handler(self, name, *args):
		if not self.is_modal:
			parent = self.parent
			if parent:
				parent.call_handler(name, *args)
	
	def global_to_local(self, p):
		return subtract(p, self.local_to_global_offset())
	
	def local_to_global_offset(self):
		d = self.rect.topleft
		parent = self.parent
		if parent:
			d = add(d, parent.local_to_global_offset())
		return d

	def key_down(self, event):
		self.call_parent_handler('key_down', event)

	def key_up(self, event):
		self.call_parent_handler('key_up', event)

	def is_inside(self, container):
		widget = self
		while widget:
			if widget is container:
				return True
			widget = widget.parent
		return False

	def present(self):
		#print "Widget: presenting with rect", self.rect
		root = self.get_root()
		self.rect.center = root.rect.center
		root.add(self)
		root.run(modal_widget = self)
		root.remove(self)
		#print "Widget.present: returning", self.modal_result
		return self.modal_result
	
	def dismiss(self, value):
		self.modal_result = value

	def get_root(self):
		return root_widget

	def focus(self):
		if not self.is_modal:
			parent = self.parent
			if parent:
				parent.focus_on(self)
	
	def focus_on(self, subwidget):
		self.focus_switch = subwidget
		self.focus()

	def has_focus(self):
		return self.is_modal or (self.parent and self.parent.focused_on(self))
	
	def focused_on(self, widget):
		return self.focus_switch is widget and self.has_focus()
	
#	def get_inherited(self, attr, default = None):
#		x = getattr(self, attr, None)
#		if x is None:
#			parent = self.parent
#			if parent is not None:
#				x = parent.get_inherited(attr, default)
#			else:
#				x = default
#		return x
#	
#	def get_fg_color(self):
#		return self.get_inherited('fg_color') or self.default_fg_color
#
#	def get_font(self):
#		return self.get_inherited('font')

	def shrink_wrap(self):
		contents = self.subwidgets
		if contents:
			rects = [widget.rect for widget in contents]
			#rmax = Rect.unionall(rects) # broken in PyGame 1.7.1
			rmax = rects.pop()
			for r in rects:
				rmax = rmax.union(r)
			self.rect.size = add(rmax.topleft, rmax.bottomright)

	def invalidate(self):
		root = self.get_root()
		if root:
			root.do_draw = True

	def get_cursor(self, event):
		return arrow_cursor
	
	def predict(self, kwds, name):
		try:
			return kwds[name]
		except KeyError:
			return theme.root.get(self.__class__, name)

	def predict_font(self, kwds, name = 'font'):
		return kwds.get(name) or theme.root.get_font(self.__class__, name)

	def get_margin_rect(self):
		r = Rect((0, 0), self.rect.size)
		d = -2 * self.margin
		r.inflate_ip(d, d)
		return r

	def set_size_for_text(self, width, nlines = 1):
		if width is not None:
			font = self.font
			d = 2 * self.margin
			if isinstance(width, basestring):
				width, height = font.size(width)
				width += d
			else:
				height = font.size("X")[1]
			self.rect.size = (width, height * nlines + d)
