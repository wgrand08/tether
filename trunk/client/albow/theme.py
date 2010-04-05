#
#    Albow - Themes
#

import resource

debug_theme = False

class ThemeProperty(object):

	def __init__(self, name):
		self.name = name
		self.cache_name = intern("_" + name)
	
	def __get__(self, obj, owner):
		if debug_theme:
			print "%s(%r).__get__(%r)" % (self.__class__.__name__, self.name, obj)
		try: ###
			cache_name = self.cache_name
			try:
				return getattr(obj, cache_name)
			except AttributeError, e:
				if debug_theme:
					print e
				value = self.get_from_theme(obj.__class__, self.name)
				obj.__dict__[cache_name] = value
				return value
		except: ###
			if debug_theme:
				import traceback
				traceback.print_exc()
				print "-------------------------------------------------------"
			raise ###

	def __set__(self, obj, value):
		if debug_theme:
			print "Setting %r.%s = %r" % (obj, self.cache_name, value) ###
		obj.__dict__[self.cache_name] = value

	def get_from_theme(self, cls, name):
		return root.get(cls, name)


class FontProperty(ThemeProperty):

	def get_from_theme(self, cls, name):
		return root.get_font(cls, name)


class Theme(object):
	#  base   Theme or None   Theme on which this theme is based

	def __init__(self, name, base = None):
		self.name = name
		self.base = base

	def get(self, cls, name):
		if debug_theme:
			print "Theme(%r).get(%r, %r)" % (self.name, cls, name)
		for base_class in cls.__mro__:
			class_theme = getattr(self, base_class.__name__, None)
			if class_theme:
				try:
					return class_theme.get(cls, name)
				except AttributeError:
					pass
		try:
			return getattr(self, name)
		except AttributeError:
			base_theme = self.base
			if base_theme:
				return base_theme.get(cls, name)
		raise AttributeError("No value found in theme for '%s'" % name)
	
	def get_font(self, cls, name):
		if debug_theme:
			print "Theme.get_font(%r, %r)" % (cls, name)
		spec = self.get(cls, name)
		if spec:
			if debug_theme:
				print "font spec =", spec
			return resource.get_font(*spec)


root = Theme('root')
root.font = (15, "Vera.ttf")
root.fg_color = (255, 255, 255)
root.bg_color = None
root.border_width = 0
root.border_color = None
root.margin = 0

root.RootWidget = Theme('RootWidget')
root.RootWidget.bg_color = (0, 0, 0)

root.Button = Theme('Button')
root.Button.font = (18, "VeraBd.ttf")
root.Button.fg_color = (255, 255, 0)
root.Button.highlight_color = (255, 0, 0)
root.Button.disabled_color = (64, 64, 64)

root.ImageButton = Theme('ImageButton')
root.ImageButton.highlight_color = (0, 128, 255)

framed = Theme('framed')
framed.border_width = 1
framed.margin = 3

root.TextField = Theme('TextField', base = framed)

root.Dialog = Theme('Dialog')
root.Dialog.bg_color = (128, 128, 128)
root.Dialog.border_width = 2
root.Dialog.margin = 15

root.DirPathView = Theme('DirPathView', base = framed)

root.FileListView = Theme('FileListView', base = framed)

root.PaletteView = Theme('PaletteView')
root.PaletteView.sel_color = (0, 128, 255)
root.PaletteView.sel_width = 2
root.PaletteView.scroll_button_size = 16
root.PaletteView.scroll_button_color = (0, 128, 255)

root.TextScreen = Theme('TextScreen')
root.TextScreen.heading_font = (24, "VeraBd.ttf")
root.TextScreen.button_font = (18, "VeraBd.ttf")
root.TextScreen.margin = 20
