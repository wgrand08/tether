import textwrap
from pygame import Rect
from pygame.locals import *
from widget import Widget
from controls import Label, TextField, Button, Row, Column

class Dialog(Widget):

	enter_response = True
	cancel_response = False

	def key_down(self, event):
		k = event.key
		if k == K_RETURN or k == K_KP_ENTER:
			if self.enter_response is not None:
				self.dismiss(self.enter_response)
		elif k == K_ESCAPE:
			if self.cancel_response is not None:
				self.dismiss(self.cancel_response)

def wrapped_label(text, wrap_width, **kwds):
	paras = text.split("\n\n")
	text = "\n".join([textwrap.fill(para, wrap_width) for para in paras])
	return Label(text, **kwds)

def alert(mess, wrap_width = 60, **kwds):
	box = Dialog(**kwds)
	d = box.margin
	lb = wrapped_label(mess, wrap_width)
	lb.rect.topleft = (d, d)
	box.add(lb)
	box.shrink_wrap()
	return box.present()

def ask(mess, responses = ["OK", "Cancel"], default = 0, cancel = -1,
		wrap_width = 60, **kwds):
	box = Dialog(**kwds)
	d = box.margin
	lb = wrapped_label(mess, wrap_width)
	lb.rect.topleft = (d, d)
	buts = []
	for caption in responses:
		but = Button(caption, action = lambda x = caption: box.dismiss(x))
		buts.append(but)
	brow = Row(buts, spacing = d)
	col = Column([lb, brow], spacing = d, align ='r')
	col.rect.topleft = (d, d)
	if default is not None:
		box.enter_response = responses[default]
	else:
		box.enter_response = None
	if cancel is not None:
		box.cancel_response = responses[cancel]
	else:
		box.cancel_response = None
	box.add(col)
	box.shrink_wrap()
	return box.present()

def input_text(prompt, width, initial = None, **kwds):
	box = Dialog(**kwds)
	d = box.margin
	def ok():
		box.dismiss(True)
	def cancel():
		box.dismiss(False)
	lb = Label(prompt)
	lb.rect.topleft = (d, d)
	tf = TextField(width)
	if initial:
		tf.set_text(initial)
	tf.enter_action = ok
	tf.escape_action = cancel
	tf.rect.top = lb.rect.top
	tf.rect.left = lb.rect.right + 5
	box.add(lb)
	box.add(tf)
	tf.focus()
	box.shrink_wrap()
	if box.present():
		return tf.get_text()
	else:
		return None
