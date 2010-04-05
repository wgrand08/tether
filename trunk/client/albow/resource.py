import os, sys
import pygame
from pygame.locals import RLEACCEL

#default_font_name = "Vera.ttf"
optimize_images = True
run_length_encode = False

def find_resource_dir():
	dir = sys.path[0]
	while 1:
		path = os.path.join(dir, "Resources")
		if os.path.exists(path):
			return path
		parent = os.path.dirname(dir)
		if parent == dir:
			raise SystemError("albow: Unable to find Resources directory")
		dir = parent
	
resource_dir = find_resource_dir()

image_cache = {}
font_cache = {}
sound_cache = {}
text_cache = {}
cursor_cache = {}

def resource_path(*names):
	return os.path.join(resource_dir, *names)

def get_image(name, border = 0, optimize = optimize_images, noalpha = False,
		rle = run_length_encode):
	image = image_cache.get(name)
	if not image:
		image = pygame.image.load(resource_path("images", name))
		if noalpha:
			image = image.convert(24)
		elif optimize:
			image = image.convert_alpha()
		if rle:
			image.set_alpha(255, RLEACCEL)
		if border:
			w, h = image.get_size()
			b = border
			d = 2 * border
			image = image.subsurface(b, b, w - d, h - d)
		image_cache[name] = image
	return image

def get_font(size, name):
	key = (name, size)
	font = font_cache.get(key)
	if not font:
		path = resource_path("fonts", name)
		font = pygame.font.Font(path, size)
		font_cache[key] = font
	return font

class DummySound(object):
	def fadeout(self, x): pass
	def get_length(self): return 0.0
	def get_num_channels(self): return 0
	def get_volume(self): return 0.0
	def play(self, *args): pass
	def set_volume(self, x): pass
	def stop(self): pass

dummy_sound = DummySound()

def get_sound(name):
	if sound_cache is None:
		return dummy_sound
	sound = sound_cache.get(name)
	if not sound:
		try:
			from pygame.mixer import Sound
		except ImportError, e:
			no_sound(e)
			return dummy_sound
		path = resource_path("sounds", name)
		try:
			sound = Sound(path)
		except pygame.error, e:
			missing_sound(e, name)
			return dummy_sound
		sound_cache[name] = sound
	return sound

def no_sound(e):
	global sound_cache
	print "albow.resource.get_sound: %s" % e
	print "albow.resource.get_sound: Sound not available, continuing without it"
	sound_cache = None

def missing_sound(e, name):
	print "albow.resource.get_sound: %s: %s" % (name, e)

def get_text(name):
	text = text_cache.get(name)
	if text is None:
		path = resource_path("text", name)
		text = open(path, "rU").read()
		text_cache[name] = text
	return text

#def get_default_font():
#	return get_font(12)

def load_cursor(name):
	image = get_image(name)
	width, height = image.get_size()
	hot = (0, 0)
	data = []
	mask = []
	db = mb = 0
	bit = 0x80
	xr = xrange(width)
	for y in xrange(height):
		for x in xr:
			r, g, b, a = image.get_at((x, y))
			if a >= 128:
				mb |= bit
				if r + g + b < 383:
					db |= bit
			if r == 0 and b == 255:
				hot = (x, y)
			bit >>= 1
			if not bit:
				data.append(db)
				mask.append(mb)
				db = mb = 0
				bit = 0x80
	return ((width, height), hot, data, mask)

def get_cursor(name):
	cursor = cursor_cache.get(name)
	if cursor is None:
		cursor = load_cursor(name)
		cursor_cache[name] = cursor
	return cursor
