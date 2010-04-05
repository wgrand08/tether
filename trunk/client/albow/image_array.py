from albow.resource import get_image

class ImageArray(object):

	def __init__(self, image, shape):
		self.image = image
		if isinstance(shape, tuple):
			self.nrows, self.ncols = shape
		else:
			self.nrows = 1
			self.ncols = shape

	def __getitem__(self, index):
		image = self.image
		nrows = self.nrows
		ncols = self.ncols
		if nrows == 1:
			row = 0
			col = index
		else:
			row, col = index
		iwidth, iheight = image.get_size()
		left = iwidth * col // ncols
		top = iheight * row // nrows
		width = iwidth // ncols
		height = iheight // nrows
		return image.subsurface(left, top, width, height)

image_array_cache = {}

def get_image_array(name, shape, **kwds):
	result = image_array_cache.get(name)
	if not result:
		result = ImageArray(get_image(name, **kwds), shape)
		image_array_cache[name] = result
	return result
