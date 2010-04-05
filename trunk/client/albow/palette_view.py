from pygame import Rect, draw
from grid_view import GridView
from utils import frame_rect
from theme import ThemeProperty

class PaletteView(GridView):
	#  nrows   int   No. of displayed rows
	#  ncols   int   No. of displayed columns
	#
	#  Abstract methods:
	#
	#    num_items()  -->  no. of items
	#    draw_item(surface, item_no, rect)
	#    click_item(item_no, event)
	#    item_is_selected(item_no)  -->  bool

#	sel_color = (0, 128, 255)
#	sel_width = 2
#	scroll_button_size = 16
#	scroll_button_color = (0, 128, 255)

	sel_color = ThemeProperty('sel_color')
	sel_width = ThemeProperty('sel_width')
	scroll_button_size = ThemeProperty('scroll_button_size')
	scroll_button_color = ThemeProperty('scroll_button_color')

	highlight_style = 'frame' # or 'fill'

	def __init__(self, cell_size, nrows, ncols, scrolling = False):
		GridView.__init__(self, cell_size, nrows, ncols)
		self.nrows = nrows
		self.ncols = ncols
		self.scrolling = scrolling
		if scrolling:
			d = self.scroll_button_size
			l = self.rect.width
			b = self.rect.height
			self.rect.width += d
			self.scroll_up_rect = Rect(l, 0, d, d).inflate(-4, -4)
			self.scroll_down_rect = Rect(l, b - d, d, d).inflate(-4, -4)
		self.scroll = 0
	
	def draw(self, surface):
		GridView.draw(self, surface)
		if self.can_scroll_up():
			self.draw_scroll_up_button(surface)
		if self.can_scroll_down():
			self.draw_scroll_down_button(surface)
	
	def draw_scroll_up_button(self, surface):
		r = self.scroll_up_rect
		c = self.scroll_button_color
		draw.polygon(surface, c, [r.bottomleft, r.midtop, r.bottomright])
	
	def draw_scroll_down_button(self, surface):
		r = self.scroll_down_rect
		c = self.scroll_button_color
		draw.polygon(surface, c, [r.topleft, r.midbottom, r.topright])
	
	def draw_cell(self, surface, row, col, rect):
		i = self.cell_to_item_no(row, col)
		if i is not None:
			highlight = self.item_is_selected(i)
			self.draw_item_and_highlight(surface, i, rect, highlight)
	
	def draw_item_and_highlight(self, surface, i, rect, highlight):
		if highlight:
			self.draw_prehighlight(surface, i, rect)
		self.draw_item(surface, i, rect)
		if highlight:
			self.draw_posthighlight(surface, i, rect)
	
	def draw_prehighlight(self, surface, i, rect):
		if self.highlight_style == 'frame':
			frame_rect(surface, self.sel_color, rect, self.sel_width)
		else:
			surface.fill(self.sel_color, rect)
	
	def draw_posthighlight(self, surface, i, rect):
		pass
	
	def mouse_down(self, event):
		if self.scrolling:
			p = event.local
			if self.scroll_up_rect.collidepoint(p):
				self.scroll_up()
				return
			elif self.scroll_down_rect.collidepoint(p):
				self.scroll_down()
				return
		GridView.mouse_down(self, event)
	
	def scroll_up(self):
		if self.can_scroll_up():
			self.scroll -= self.page_size()
	
	def scroll_down(self):
		if self.can_scroll_down():
			self.scroll += self.page_size()
	
	def can_scroll_up(self):
		return self.scrolling and self.scroll > 0
	
	def can_scroll_down(self):
		return self.scrolling and self.scroll + self.page_size() < self.num_items()
	
	def page_size(self):
		return self.nrows * self.ncols
				
	def click_cell(self, row, col, event):
		i = self.cell_to_item_no(row, col)
		if i is not None:
			self.click_item(i, event)
	
	def cell_to_item_no(self, row, col):
		i = self.scroll + row * self.num_cols() + col
		if 0 <= i < self.num_items():
			return i
		else:
			return None
	
	def num_rows(self):
		return self.nrows
	
	def num_cols(self):
		return self.ncols


