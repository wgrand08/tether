""" <title>Base widget</title> """
import pygame
import util
from const import *
import styleset
import effects
import sys

from cellulose import *

class Widget(DependantCell):
    """
    Widget([disabled, [active, [parent, [custom_styles]]]]) -> Widget
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Base widget class.

    Example of use
    --------------
    ::

        mywidget = Widget(x=30, y=100, width=100, height=30)
        mywidget.connect(EVENT, myfunc, [values])

        # One of the cool things about GooeyPy is that you can change any style
        # widget specific options (like 'value' in the input and slider widgets)
        # and the widget will automatically update itself.

        mywidget.value = "GooeyPy is awesome!"

        # One thing to note is that while when initializing a widget you can
        # pass it arguments as custom styles (see below), you can't access those
        # styles directly (i.e. mywidget.width won't give you what you expect,
        # and it will raise an error if you try to assign to it). So if you want
        # to change or read a style option you would have to do something like
        # the following:

        mywidget.stylesets["default"]["width"] = 140

        # You can also do it like this:

        mywidget.style["width"] = 140

        # But be warned, widget.style returns the current styleset that's in
        # use! So if you are hovering over the widget when you change the width,
        # that width will only apply to that widget when you hover over it.
        # So if you want the width to apply to the widget at all times, you
        # can apply it to the "default" styleset (as shown above) in which
        # case it will apply to all stylesets that don't already have a width
        # style set. Or you can loop through mywidget.stylesets and set it for
        # each one, like so:

        for s in mywidget.stylesets.values():
            s["width"] = 140


    Arguments
    ---------
    disabled
        If a widget is disabled, the "disabled" styling will
        apply and it will cease to interact with the user.

    active
        This widget will be ignored all together if it's not active.

    parent
        This is used internally when creating new widget types.

    custom_styles
        When you pass any extra arguments they get passed as a
        custom style; the key being the style option and the
        value passed as the tyle's option.
        Like in our example above, we pass 'x', 'y', 'width',
        and 'height'. Those will automatically get converted
        into styling options specific to that widget. Please
        refer to the documentation on styling for all
        available options and valid values.
    """


    disabled  = util.ReplaceableCellDescriptor()
    hovering  = util.ReplaceableCellDescriptor()
    focused   = util.ReplaceableCellDescriptor()
    stylesets = util.ReplaceableCellDescriptor()
    #parent    = InputCellDescriptor()
    container = util.ReplaceableCellDescriptor()
    pressing  = util.ReplaceableCellDescriptor()
    selected  = util.ReplaceableCellDescriptor()
    active    = util.ReplaceableCellDescriptor()

    def __init__(self, disabled=False, active=True, parent=None, **params):
        DependantCell.__init__(self)

        self.hovering = False
        self.focused = False
        self.active = active

        # There is a subtle difference between parent and container. A widget
        # can have any other widget as a parent while a container must be a
        # Container widget. parent is used for inheriting styles and positioning
        # with padding and aligning. Normally, when a widget has a container,
        # it's parent is the same as it.
        self.parent = parent
        self.container = None

        self.connects = {}

        # Move to widgets that use it?
        self.selected = False

        self._last_blit_rect = None

        self.effect = None

        # Weather or not this widget is being pressed.
        self.pressing = 0

        # This widget is still drawn if disabled is True, it just doesn't work.
        self.disabled = disabled

        def get_style_option(key):
            s = self.style[key]
            if hasattr(s, "values"):
                return s.values
            return s
        self.style_option = ComputedDict(get_style_option)

        # FIXME: Adding one more causes a really wierd bug where sometimes a
        # widget will inherit from Widget styling when not using default style.
        self.stylesets = {"disabled":None, "hover":None, "default":None,
                "focused":None, "down":None}

        # Generate the stylesets.
        surf = None
        style = None
        s = util.app.get_style(self)

        if s:
            #TODO: clear unnecessary spaces.
            for cmd in s.split(";"):
                cmd = cmd.strip()
                t = cmd.split(":")
                if len(t) == 2:
                    option = t[0]
                    values = t[1].split(" ")

                    if option == "event":
                        # A new section!

                        if values[0] != "default" and not self.stylesets["default"]:
                            print "Missing default styling for "+str(self)+" You must have the styling for the default event defined first!"
                            sys.exit()

                        if (self.stylesets.has_key(values[0]) and not\
                                    self.stylesets[values[0]]) or not\
                                    self.stylesets.has_key(values[0]):
                            if values[0] != "default":
                                parent = self.stylesets["default"]
                            else: parent = None
                            style = util.widgets.StyleSet(self, parent)
                            self.stylesets[values[0]] = style
                        else:
                            style = self.stylesets[values[0]]

                    if option != "event":
                        style[option] = values

        # Set any stylesets that are still blank.
        for (e, v) in self.stylesets.items():
            if not v:
                self.stylesets[e] = util.widgets.StyleSet(self, self.stylesets["default"])

        for (option,values) in params.items():
            self.stylesets["default"][option] = values



    def link(self, attr):
        """
        Widget.link(attr) -> cellulose.DependencyCell
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        This is one of those very cool things in GooeyPy where you won't find
        anywhere else. You can have one widget share a value with one or more
        other widgets!
        In the below example, whenever the value of myslider changes, so will
        the fontsize for mylabel and vise-versa (and it automatically redraws
        the stuff too... of course).

        Example of use
        --------------
        ::

            myslider = Slider(value=10, length=20)
            mylabel = Label(value="hi", font_size=myslider.link("value"))

        Linking works with any attribute (that you would want to change) or
        styling option in any widget! Cool eh? Well, actually it's not quite all
        working perfectly, so expect a bug or two with linking certain
        attributes on certain widgets.

        There is one pit-fall with this... if the thing you are trying to link
        isn't an attribute or a Cell (i.e. linkable), it will return None (and
        that could cause rather obscure errors).
        """
        if attr in self._cells:
            return self._cells[attr]
        # Isn't a linkable cell, but perhaps there is a privet attribute that is
        elif attr[0] != "_":
            return self.link("_"+attr)
        else:
            return None



    def connect(self, code, func, *values):
        """
        Widget.connect(code, func, [values]) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Connect an event to a callback function.

        Example of use
        --------------
        ::

            def onclick(value):
                print 'clicked', value

            mybutton = Button("GooeyPy")
            mybutton.connect(CLICK, onclick, "button")



        Arguments
        ---------
        code
            The event code to trigger the callback.

        func
            The callback

        values
            Extra values you may want to send on to your callback when
            it is called.
        """
        self.connects[code] = {'fnc':func,'values':values}



    def _set_dirty(self, v):
        self._dirty = v
    def _get_dirty(self):
        self._verify_possibly_changed_dependencies()
        return self._dirty
    dirty = property(_get_dirty, _set_dirty)

    def possibly_changed(self):
        pass


    def set_x(self,v):
        self.stylesets["default"]["x"] = v
    x = property(lambda self:int(self.stylesets["default"]["x"]), set_x)
    def set_y(self,v):
        self.stylesets["default"]["y"] = v
    y = property(lambda self:int(self.stylesets["default"]["y"]), set_y)

    def pos(self, pos=None):
        """
        Widget.pos -> Tuple
        ^^^^^^^^^^^^^^^^^^^
        Get the actual position that the widget should be drawn to and receive
        events at. """
        if pos:
            x,y = pos
        else:
            x = int(self.style_option["x"])
            y = int(self.style_option["y"])
        if self.style_option["position"] == "relative":
            if self.parent:
                px, py = self.parent.pos

                # Padding.
                x += px #+ int(self.parent.stylesets["default"]["padding-left"])
                y += py #+ int(self.parent.stylesets["default"]["padding-top"])

                # Alignment positioning.
                if self.style_option["align"] == "center":
                    x += (self.parent.width - self.width) / 2
                elif self.style_option["align"] == "right":
                    x += (self.parent.width - self.width)
                else:
                    x += int(self.parent.stylesets["default"]["padding-left"])

                if self.style_option["valign"] == "center":
                    y += (self.parent.height - self.height) / 2
                elif self.style_option["valign"] == "bottom":
                    y += (self.parent.height - self.height)
                else:
                    y += int(self.parent.stylesets["default"]["padding-top"])
            if self.container and self.container.scrollable:
                x -= self.container.offset_x
                y -= self.container.offset_y
        return (x,y)
    pos = ComputedCellDescriptor(pos)


    def width(self, w=None):
        """
        Widget.width -> int
        ^^^^^^^^^^^^^^^^^^^
        This returns the actual width of this widget. It takes into account
        padding (for widgets that contain other widgets), min-width and
        max-width styles.
        """
        if not w or self.style_option["width"]:
            w = self.style_option["width"] + self.style_option["padding-left"]+\
                    self.style_option["padding-right"]
            w = max(w,0)
        width = w
        min_width = self.style_option["min-width"]
        max_width = self.style_option["max-width"]
        if min_width and width < min_width:
            w = min_width
        if max_width and width > max_width:
            w = max_width
        return w
    width = ComputedCellDescriptor(width)


    def height(self, h=None):
        """
        Widget.height -> int
        ^^^^^^^^^^^^^^^^^^^^
        This returns the actual height of this widget. It takes into account
        padding (for widgets that contain other widgets), min-height and
        max-height styles.
        """
        if h is None or self.style_option["height"]:
            h = self.style_option["height"] + self.style_option["padding-top"]+\
                    self.style_option["padding-bottom"]
            h = max(h,0)
        height = h
        min_height = self.style_option["min-height"]
        max_height = self.style_option["max-height"]
        if min_height and height < min_height:
            h = min_height
        if max_height and height > max_height:
            h = max_height
        return h
    height = ComputedCellDescriptor(height)


    def rect(self):
        """
        Widget.rect -> pygame.Rect
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
        Gets the rect of the widget's current surface.
        """
        r = self.surface.get_rect()
        r.x, r.y = self.pos
        return r
    rect = ComputedCellDescriptor(rect)

    def focusable(self):
        return self.style_option["focusable"]
    focusable = ComputedCellDescriptor(focusable)

    def style(self):
        """
        Widget.style -> StyleSet
        ^^^^^^^^^^^^^^^^^^^^^^^^
        Returns the current styleset in use (from Widget.stylesets)
        """
        if self.disabled:
            return self.stylesets["disabled"]
        elif self.pressing:
            return self.stylesets["down"]
        elif self.selected is True and self.stylesets.has_key("selected"):
            return self.stylesets["selected"]
        elif self.hovering:
            return self.stylesets["hover"]
        elif self.focused and self.stylesets["focused"]:
            return self.stylesets["focused"]
        else:
            return self.stylesets["default"]
    style = ComputedCellDescriptor(style)

    def surface(self):
        return self.style.surf
    surface = ComputedCellDescriptor(surface)


    def draw(self, drawbg=True):
        """
        Widget.draw() -> None
        ^^^^^^^^^^^^^^^^^^^^^
        draws the widget if necessary.
        """

        #HACK: Better place to put this? Here because draw is run every frame.
        if self.focused:
            self.repetitive_events()

        if self.dirty or self.effect or self.style_option["effect"] != 'none':
            # We don't want to keep around old dependencies. We gotta clear them
            # before adding the new ones.
            for dep in self.dependencies.values():
                dep.unregister_dependant(self)
            self.dependencies = {}

            self.push()
            try:
                surf = self.style.surf
                if self.effect:
                    # An effect is running.
                    r = self.effect.run(surf)
                    if not r:
                        self.effect = None
                    else:
                        surf = r
                elif self.style_option["effect"][0] == "pulsate":
                    i = int(self.style_option["effect"][1])
                    self.effect = effects.Pulsate(i)
                    surf = self.effect.run(surf)

                #print self.__class__.__name__

                x,y = self.pos
                # FIXME: won't work if widget doesn't have container... but
                # fixes the x=y=0 display bug.
                if drawbg and self._last_blit_rect and self.container:
                    lbrpos =(self._last_blit_rect.x, self._last_blit_rect.y)
                    self._last_blit_rect.x -= self.container.x
                    self._last_blit_rect.y -= self.container.y
                    util.blit(self.container.surface, lbrpos,
                            clip_rect=self._last_blit_rect)

                clip_rect = surf.get_rect()
                if self.container and self.container.scrollable:
                    #y -= self.container.offset_y
                    if self.container.offset_y > self.y+self.height:
                        return
                    if self.container.offset_y+self.container.height < self.y+\
                            self.container.style_option["padding-bottom"]+\
                            self.container.style_option["padding-top"]+\
                            self.height:
                        # Off the  bottom. Need to figure out how to do clipping
                        return
                
                    #clip_rect = surf.get_rect()#self.container.rect
                    clip_rect.x = 0#min(self.x-self.container.offset_x, self.x)
                    clip_rect.y = min(0, self.y-self.container.offset_y)

                    #y = min(y, self.container.height-self.height)

                    #if self.container.offset_y+self.container.height < self.y+\
                            #self.height+\
                            #self.container.style_option["padding-bottom"]+\
                            #self.container.style_option["padding-top"]:
                        #clip_rect.height = self.container.height-\
                                #self.container.style_option["padding-bottom"] - self.y
                        #print self.y
                self.clip_rect = clip_rect

                self._last_blit_rect = util.blit(surf, (x, y), clip_rect)
                self.draw_widget()
                self.dirty = False
            finally:
                self.pop()


    def draw_widget(self):
        """
        When writing your own widgets, you can overwrite this function
        to have custom processes when drawing.
        """
        pass

    def repetitive_events(self):
        pass

    def event(self, e):
        pass


    def click(self):
        """
        When writing your own widgets, you can overwrite this function which is
        called every time the widget is clicked.
        """
        pass

    def next(self):
        if self.container: self.container.next(self)

    def enter(self):
        self.hovering = True

    def exit(self):
        self.hovering = False


    def send(self,code,event=None):
        """
        Widget.send(code, [event]) -> None
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        Sends the event code 'code' and event 'event' (if suplied) to trigger
        any callbacks.
        """
        if code in self.connects:
            con = self.connects[code]

            fnc = con['fnc']
            values = list(con['values'])

            nargs = fnc.func_code.co_argcount
            names = list(fnc.func_code.co_varnames)[:nargs]
            if hasattr(fnc,'im_class'): names.pop(0)

            args = []
            magic = {'_event':event,'_code':code,'_widget':self}
            for name in names:
                if name in magic.keys():
                    args.append(magic[name])
                elif len(values):
                    args.append(values.pop(0))
                else:
                    break
            args.extend(values)
            fnc(*args)

    def _event(self,e):
        #return
        if self.disabled: return

        send = False
        if e.type == KEYDOWN:
            if self.focused:
                send = True
                if e.key == K_ESCAPE:
                    self.focused = False
        #elif e.type == KEYDOWN and e.key == K_TAB:
            #self.next()
        elif e.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(e.pos):
                self.pressing = 1
                self.dirty = True
                self.focused = True
                send = True
            else:
                self.focused = False
        elif e.type == MOUSEBUTTONUP:
            if self.pressing == 1:
                self.pressing = 0
                self.dirty = True
                if self.rect.collidepoint(e.pos):
                    self.send(CLICK)
                    self.click()
                send = True
        elif e.type == MOUSEMOTION:
            # This takes quite a bit of processing.
            if self.rect.collidepoint(e.pos):
                if not self.hovering:
                    self.enter()

                send = True
            else:
                if self.hovering:
                    self.exit()

            if self.focused: send = True

        if send:
            self.send(e.type, e)
            self.event(e)
