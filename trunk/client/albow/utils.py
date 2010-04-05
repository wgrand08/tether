from pygame import draw, Surface
from pygame.locals import SRCALPHA

def frame_rect(surface, color, rect, thick = 1):
	surface.fill(color, (rect.left, rect.top, rect.width, thick))
	surface.fill(color, (rect.left, rect.bottom - thick, rect.width, thick))
	surface.fill(color, (rect.left, rect.top, thick, rect.height))
	surface.fill(color, (rect.right - thick, rect.top, thick, rect.height))

def blit_tinted(surface, image, pos, tint, src_rect = None):
	from Numeric import array, add, minimum
	from pygame.surfarray import array3d, pixels3d
	if src_rect:
		image = image.subsurface(src_rect)
	buf = Surface(image.get_size(), SRCALPHA, 32)
	buf.blit(image, (0, 0))
	src_rgb = array3d(image)
	buf_rgb = pixels3d(buf)
	buf_rgb[...] = minimum(255, add(tint, src_rgb)).astype('b')
	buf_rgb = None
	surface.blit(buf, pos)
