from pygame import Rect, draw
from pygame.locals import K_LEFT, K_RIGHT
from widget import Widget
from theme import ThemeProperty
import resource

class Label(Widget):

	def __init__(self, text, width = None, **kwds):
		Widget.__init__(self, **kwds)
		font = self.font
		lines = text.split("\n")
		tw, th = 0, 0
		for line in lines:
			w, h = font.size(line)
			tw = max(tw, w)
			th += h
		if width is not None:
			tw = width
		else:
			tw = max(1, tw)
		d = 2 * self.margin
		self.rect.size = (tw, th)
		self.text = text

	def draw(self, surface):
		self.draw_with(surface, self.fg_color)
	
	def draw_with(self, surface, fg):
		y = 0
		lines = self.text.split("\n")
		font = self.font
		dy = font.get_linesize()
		for line in lines:
			image = font.render(line, True, fg)
			surface.blit(image, (0, y))
			y += dy

#---------------------------------------------------------------------------

class BaseButton(object):

	highlighted = False
	_enabled = True
	
	def __init__(self, action, enable):
		if action:
			self.action = action
		if enable:
			self.get_enabled = enable
	
	def mouse_down(self, event):
		if self.enabled:
			self.highlighted = True
	
	def mouse_up(self, event):
		if self.highlighted:
			self.highlighted = False
			self.call_handler('action')
	
	def action(self):
		pass
	
	def get_enabled(self):
		return self._enabled
	
	def set_enabled(self, x):
		self._enabled = x
	
	enabled = property(
		lambda self: self.get_enabled(),
		lambda self, x: self.set_enabled(x)
	)

#---------------------------------------------------------------------------

class Button(BaseButton, Label):

	highlight_color = ThemeProperty('highlight_color')
	disabled_color = ThemeProperty('disabled_color')

	def __init__(self, text, action = None, enable = None, **kwds):
		BaseButton.__init__(self, action, enable)
		Label.__init__(self, text, **kwds)
	
	def draw(self, surface):
		if self.enabled:
			if self.highlighted:
				color = self.highlight_color
			else:
				color = self.fg_color
		else:
			color = self.disabled_color
		self.draw_with(surface, color)
	

#---------------------------------------------------------------------------

class ImageButton(BaseButton, Widget):

	highlight_color = ThemeProperty('highlight_color')
	
	def __init__(self, image, action = None, enable = None, **kwds):
		if isinstance(image, basestring):
			image = resource.get_image(image)
		if image:
			self.image = image
		BaseButton.__init__(self, action, enable)
		Widget.__init__(self, image.get_rect(), **kwds)

	def draw(self, surf):
		frame = surf.get_rect()
		if self.highlighted:
			surf.fill(self.highlight_color)
		image = self.image
		r = image.get_rect()
		r.center = frame.center
		surf.blit(image, r)

#---------------------------------------------------------------------------

class TextField(Widget):

	#fg_color = (0, 255, 0)
	upper = False

	def __init__(self, width, upper = None, **kwds):
		Widget.__init__(self, **kwds)
		self.set_size_for_text(width)
		if upper is not None:
			self.upper = upper
		self.text = ""
		self.insertion_point = None
	
	def get_text(self):
		return self.text
	
	def set_text(self, text):
		self.text = text
	
	def get_value(self):
		return self.get_text()
	
	def set_value(self, x):
		self.set_text(x)
	
	def draw(self, surface):
		frame = self.get_margin_rect()
		fg = self.fg_color
		font = self.font
		text, i = self.get_text_and_insertion_point()
		image = font.render(text, True, fg)
		surface.blit(image, frame)
		if self.has_focus():
			x, h = font.size(text[:i])
			x += frame.left
			y = frame.top
			draw.line(surface, fg, (x, y), (x, y + h - 1))
	
	def key_down(self, event):
		k = event.key
		if k == K_LEFT:
			self.move_insertion_point(-1)
			return
		if k == K_RIGHT:
			self.move_insertion_point(1)
			return
		try:
			c = event.unicode
		except ValueError:
			c = ""
		if self.insert_char(c) == 'pass':
			self.call_parent_handler('key_down', event)
	
	def get_text_and_insertion_point(self):
		text = self.get_text()
		i = self.insertion_point
		if i is None:
			i = len(text)
		else:
			i = max(0, min(i, len(text)))
		return text, i
	
	def move_insertion_point(self, d):
		text, i = self.get_text_and_insertion_point()
		i = max(0, min(i + d, len(text)))
		self.insertion_point = i
	
	def insert_char(self, c):
		if self.upper:
			c = c.upper()
		if c <= "\x7f":
			if c == "\x08" or c == "\x7f":
				text, i = self.get_text_and_insertion_point()
				self.change_text(text[:i-1] + text[i:])
				self.insertion_point = i - 1
				return
			elif c == "\r" or c == "\x03":
				if self.call_handler('enter_action'):
					return
			elif c == "\x1b":
				if self.call_handler('escape_action'):
					return
			elif c >= "\x20":
				text, i = self.get_text_and_insertion_point()
				self.change_text(text[:i] + c + text[i:])
				self.insertion_point = i + 1
				return
		return 'pass'

	def mouse_down(self, e):
		self.focus()
		x, y = e.local
		text = self.get_text()
		font = self.font
		n = len(text)
		def width(i):
			return font.size(text[:i])[0]
		i1 = 0
		i2 = len(text)
		x1 = 0
		x2 = width(i2)
		while i2 - i1 > 1:
			i3 = (i1 + i2) // 2
			x3 = width(i3)
			if x > x3:
				i1, x1 = i3, x3
			else:
				i2, x2 = i3, x3
		if x - x1 > (x2 - x1) // 2:
			i = i2
		else:
			i = i1
		self.insertion_point = i

	def change_text(self, text):
		self.set_text(text)
		self.call_handler('change_action')

#---------------------------------------------------------------------------

class ValueField(TextField):

	empty = NotImplemented
	format = "%s"

	def __init__(self, width, type = None, format = None, **kwds):
		TextField.__init__(self, width, **kwds)
		if type is not None:
			self.type = type
		if 'empty' in kwds:
			self.empty = kwds.pop('empty')
		if format is not None:
			self.format = format
	
	def get_value(self):
		text = self.get_text()
		if not text:
			empty = self.empty
			if empty is not NotImplemented:
				return empty
			else:
				raise ValueError("Missing value")
		else:
			return self.type(text)

	def set_value(self, x):
		self.set_text(self.format_value(x))
	
	def format_value(self, x):
		return self.format % x

#---------------------------------------------------------------------------

class IntField(ValueField):
	type = int

class FloatField(ValueField):
	type = float

#---------------------------------------------------------------------------

class RowOrColumn(Widget):

	def __init__(self, size, items, kwds):
		align = kwds.pop('align', 'c')
		spacing = kwds.pop('spacing', 10)
		expand = kwds.pop('expand', None)
		#if kwds:
		#	raise TypeError("Unexpected keyword arguments to Row or Column: %s"
		#		% kwds.keys())
		Widget.__init__(self, kwds)
		#print "albow.controls: RowOrColumn: size =", size, "expand =", expand ###
		d = self.d
		longways = self.longways
		crossways = self.crossways
		k, attr2, attr3 = self.align_map[align]
		w = 0
		length = 0
		expand = expand or items[-1]
		for item in items:
			r = item.rect
			w = max(w, getattr(r, crossways))
			if item is not expand:
				length += getattr(r, longways)
		if size is not None:
			n = len(items)
			if n > 1:
				length += spacing * (n - 1)
			#print "albow.controls: expanding size from", length, "to", size ###
			setattr(expand.rect, longways, max(1, size - length))
		h = w * k // 2
		m = self.margin
		px = h * d[1] + m
		py = h * d[0] + m
		sx = spacing * d[0]
		sy = spacing * d[1]
		for item in items:
			setattr(item.rect, attr2, (px, py))
			self.add(item)
			p = getattr(item.rect, attr3)
			px = p[0] + sx
			py = p[1] + sy
		self.shrink_wrap()

class Row(RowOrColumn):

	d = (1, 0)
	longways = 'width'
	crossways = 'height'
	align_map = {
		't': (0, 'topleft', 'topright'),
		'c': (1, 'midleft', 'midright'),
		'b': (2, 'bottomleft', 'bottomright'),
	}

	def __init__(self, items, width = None, **kwds):
		"""
		Row(items, align = alignment, spacing = 10, width = None, expand = None)
		align = 't', 'c' or 'b'
		"""
		RowOrColumn.__init__(self, width, items, kwds)

class Column(RowOrColumn):

	d = (0, 1)
	longways = 'height'
	crossways = 'width'
	align_map = {
		'l': (0, 'topleft', 'bottomleft'),
		'c': (1, 'midtop', 'midbottom'),
		'r': (2, 'topright', 'bottomright'),
	}

	def __init__(self, items, height = None, **kwds):
		"""
		Column(items, align = alignment, spacing = 10, height = None, expand = None)
		align = 'l', 'c' or 'r'
		"""
		RowOrColumn.__init__(self, height, items, kwds)

#---------------------------------------------------------------------------

class Frame(Widget):
	#  border_spacing  int        spacing between border and widget

	border_width = 1
	border_spacing = 2

	def __init__(self, client, border_spacing = 0, **kwds):
		Widget.__init__(self, **kwds)
		self.client = client
		self.margin = d = border_spacing + self.border_width
		w, h = client.rect.size
		self.rect.size = (w + 2 * d, h + 2 * d)
		client.rect.topleft = (d, d)
		self.add(client)

#---------------------------------------------------------------------------

class Image(Widget):
	#  image   Image to display

	def __init__(self, image, **kwds):
		Widget.__init__(self, **kwds)
		w, h = image.get_size()
		d = 2 * self.margin
		self.rect.size = w + d, h + d
		self.image = image
	
	def draw(self, surf):
		frame = self.get_margin_rect()
		surf.blit(self.image, frame)
