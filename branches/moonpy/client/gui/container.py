"""
"""
import pygame

from const import *
import widget, surface

class Container(widget.Widget):
    """The base container widget, can be used as a template as well as stand alone.
    
    <pre>Container()</pre>
    """
    def __init__(self,**params):
        widget.Widget.__init__(self,**params)
        self.myfocus = None
        self.mywindow = None
        self.myhover = None
        #self.background = 0
        self.widgets = []
        self.windows = []
        self.toupdate = {}
        self.topaint = {}
    
    def update(self,s):
        updates = []
        
        if self.myfocus: self.toupdate[self.myfocus] = self.myfocus
        
        for w in self.topaint:
            if w is self.mywindow:
                continue
            else:
                w.paint(surface.subsurface(s,w.rect))
                updates.append(pygame.rect.Rect(w.rect))
        
        for w in self.toupdate:
            if w is self.mywindow:
                continue
            else:            
                us = w.update(surface.subsurface(s,w.rect))
            if us:
                for u in us:
                    updates.append(pygame.rect.Rect(u.x + w.rect.x,u.y+w.rect.y,u.w,u.h))
        
        for w in self.topaint:
            if w is self.mywindow:
                w.paint(self.top_surface(s,w))
                updates.append(pygame.rect.Rect(w.rect))
            else:
                continue 
        
        for w in self.toupdate:
            if w is self.mywindow:
                us = w.update(self.top_surface(s,w))
            else:            
                continue 
            if us:
                for u in us:
                    updates.append(pygame.rect.Rect(u.x + w.rect.x,u.y+w.rect.y,u.w,u.h))
        
        self.topaint = {}
        self.toupdate = {}
        
        return updates
    
    def repaint(self,w=None):
        if not w:
            return widget.Widget.repaint(self)
        self.topaint[w] = w
        self.reupdate()
    
    def reupdate(self,w=None):
        if not w:
            return widget.Widget.reupdate(self)
        self.toupdate[w] = w
        self.reupdate()
    
    def paint(self,s):
        self.toupdate = {}
        self.topaint = {}
        
        for w in self.widgets:
            ok = False
            try:
                sub = surface.subsurface(s,w.rect)
                ok = True
            except: 
                print 'container.paint(): %s not in %s'%(w.__class__.__name__,self.__class__.__name__)
                print s.get_width(),s.get_height(),w.rect
                ok = False
            if ok: w.paint(sub)
        
        for w in self.windows:
            w.paint(self.top_surface(s,w))
    
    def top_surface(self,s,w):
        x,y = s.get_abs_offset()
        s = s.get_abs_parent()
        return surface.subsurface(s,(x+w.rect.x,y+w.rect.y,w.rect.w,w.rect.h))
    
    def event(self,e):
        if self.mywindow and e.type == MOUSEBUTTONDOWN:
            w = self.mywindow
            if self.myfocus is w:
                if not w.rect.collidepoint(e.pos): self.blur(w)
            if not self.myfocus:
                if w.rect.collidepoint(e.pos): self.focus(w)
        
        if not self.mywindow:
            #### by Gal Koren
            ##
            ## if e.type == FOCUS:
            if e.type == FOCUS and not self.myfocus:
                #self.first()
                pass
            elif e.type == EXIT:
                if self.myhover: self.exit(self.myhover)
            elif e.type == BLUR:
                if self.myfocus: self.blur(self.myfocus)
            elif e.type == MOUSEBUTTONDOWN:
                h = None
                for w in self.widgets:
                    if w.rect.collidepoint(e.pos):
                        h = w
                        if self.myfocus is not w: self.focus(w)
                if not h and self.myfocus:
                    self.blur(self.myfocus)
            elif e.type == MOUSEMOTION:
                if 1 in e.buttons:
                    if self.myfocus: ws = [self.myfocus]
                    else: ws = []
                else: ws = self.widgets
                
                h = None
                for w in ws:
                    if w.rect.collidepoint(e.pos):
                        h = w
                        if self.myhover is not w: self.enter(w)
                if not h and self.myhover:
                    self.exit(self.myhover)
                w = self.myhover
                
                if w and w is not self.myfocus:
                    sub = pygame.event.Event(e.type,{
                        'buttons':e.buttons,
                        'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
                        'rel':e.rel})
                    w._event(sub)
        
        w = self.myfocus
        if w:
            sub = e
            
            if e.type == MOUSEBUTTONUP or e.type == MOUSEBUTTONDOWN:
                sub = pygame.event.Event(e.type,{
                    'button':e.button,
                    'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
                w._event(sub)
            elif e.type == CLICK and self.myhover is w:
                sub = pygame.event.Event(e.type,{
                    'button':e.button,
                    'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y)})
                w._event(sub)
            elif e.type == CLICK: #a dead click
                pass
            elif e.type == MOUSEMOTION:
                sub = pygame.event.Event(e.type,{
                    'buttons':e.buttons,
                    'pos':(e.pos[0]-w.rect.x,e.pos[1]-w.rect.y),
                    'rel':e.rel})
                w._event(sub)
            else:
                w._event(sub)
    
    def remove(self,w):
        """Remove a widget from the container.
        
        <pre>Container.remove(w)</pre>
        """
        self.blur(w)
        self.widgets.remove(w)
        #self.repaint()
        self.chsize()
    
    def add(self,w,x,y):
        """Add a widget to the container.
        
        <pre>Container.add(w,x,y)</pre>
        
        <dl>
        <dt>x, y<dd>position of the widget
        </dl>
        """
        w.style.x = x
        w.style.y = y 
        w.container = self
        #NOTE: this might fix it, sort of...
        #but the thing is, we don't really want to resize
        #something if it is going to get resized again later
        #for no reason...
        #w.rect.x,w.rect.y = w.style.x,w.style.y
        #w.rect.w, w.rect.h = w.resize()
        self.widgets.append(w)
        self.chsize()
    
    def open(self,w=None,x=None,y=None):
        from app import App #HACK: I import it here to prevent circular importing
        if not w:
            if (not hasattr(self,'container') or not self.container) and self is not App.app:
                self.container = App.app
            #print 'top level open'
            return widget.Widget.open(self)
        
        if self.container:
            if x != None: return self.container.open(w,self.rect.x+x,self.rect.y+y)
            return self.container.open(w)
        
        w.container = self
        
        if w.rect.w == 0 or w.rect.h == 0: #this might be okay, not sure if needed.
            w.rect.w,w.rect.h = w.resize()
        
        if x == None or y == None: #auto center the window
            #w.style.x,w.style.y = 0,0
            w.rect.x = (self.rect.w-w.rect.w)/2
            w.rect.y = (self.rect.h-w.rect.h)/2
            #w.resize()
            #w._resize(self.rect.w,self.rect.h)
        else: #show it where we want it
            w.rect.x = x
            w.rect.y = y
            #w._resize()
        
        
        self.windows.append(w)
        self.mywindow = w
        self.focus(w)
        self.repaint(w)
        w.send(OPEN)
    
    def close(self,w=None):
        if not w:
            return widget.Widget.close(self)
            
        if self.container: #make sure we're in the App
            return self.container.close(w)
        
        if self.myfocus is w: self.blur(w)
        
        if w not in self.windows: return #no need to remove it twice! happens.
        
        self.windows.remove(w)
        
        self.mywindow = None
        if self.windows:
            self.mywindow = self.windows[-1]
            self.focus(self.mywindow)
        
        if not self.mywindow:
            self.myfocus = self.widget #HACK: should be done fancier, i think..
            if not self.myhover:
                self.enter(self.widget)
            
        self.repaintall()
        w.send(CLOSE)
    
    def focus(self,w=None):
        widget.Widget.focus(self) ### by Gal koren
#        if not w:
#            return widget.Widget.focus(self)
        if not w: return
        if self.myfocus: self.blur(self.myfocus)
        if self.myhover is not w: self.enter(w)
        self.myfocus = w
        w._event(pygame.event.Event(FOCUS))
    
    def blur(self,w=None):
        if not w:
            return widget.Widget.blur(self)
        if self.myfocus is w:
            if self.myhover is w: self.exit(w)
            self.myfocus = None
            w._event(pygame.event.Event(BLUR))
    
    def enter(self,w):
        if self.myhover: self.exit(self.myhover)
        self.myhover = w
        w._event(pygame.event.Event(ENTER))
    
    def exit(self,w):
        if self.myhover and self.myhover is w:
            self.myhover = None
            w._event(pygame.event.Event(EXIT))    
    
    
#     def first(self):
#         for w in self.widgets:
#             if w.focusable:
#                 self.focus(w)
#                 return
#         if self.container: self.container.next(self)
    
#     def next(self,w):
#         if w not in self.widgets: return #HACK: maybe.  this happens in windows for some reason...
#         
#         for w in self.widgets[self.widgets.index(w)+1:]:
#             if w.focusable:
#                 self.focus(w)
#                 return
#         if self.container: return self.container.next(self)
    
    
    def _next(self,orig=None):
        start = 0
        if orig in self.widgets: start = self.widgets.index(orig)+1
        for w in self.widgets[start:]:
            if not w.disabled and w.focusable:
                if isinstance(w,Container):
                    if w._next():
                        return True
                else:
                    self.focus(w)
                    return True
        return False
                
    def next(self,w):
        if w not in self.widgets: return #HACK: maybe.  this happens in windows for some reason...
        
        if self._next(w): return True
        if self.container: return self.container.next(self)
    
    
    def previous(self,w):
        print 'Container.previous: n/a'
    
    def resize(self,width=None,height=None):
        #r = self.rect
        #r.w,r.h = 0,0
        ww,hh = 0,0
        if self.style.width: ww = self.style.width
        if self.style.height: hh = self.style.height
        
        for w in self.widgets:
            #w.rect.w,w.rect.h = 0,0
            w.rect.x,w.rect.y = w.style.x,w.style.y
            w.rect.w, w.rect.h = w.resize()
            #w._resize()
            
            ww = max(ww,w.rect.right)
            hh = max(hh,w.rect.bottom)
        return ww,hh
