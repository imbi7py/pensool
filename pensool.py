#!/usr/bin/env python

'''
Main of drawing app
'''

import gtk
from gtk import gdk

import port
import drawable
import morph.morph
import morph.textmorph
import controlinstances
import gui.manager.control
import gui.backgroundcontrol
import scheme
from config import *

# FIXME little used
import collections
Rectangle = collections.namedtuple('Rectangle', 'x y width height')


'''
TODO
file input using rsvg
'''

'''
def draw_background(self, acv, dw, x, y, ww, hh, pb):
   gc = dw.new_gc()
   pw = pb.get_width()
   ph = pb.get_height()
   offset_x = x % pw
   offset_y = y % ph
   dw_y = -offset_y
   while dw_y < hh:
       dw_x = -offset_x
       while dw_x < ww:
           dw.draw_pixbuf(gc, pb, 0, 0, dw_x, dw_y)
           dw_x += pw
       dw_y += ph
 '''

def foo(accel_group, acceleratable, keyval, modifier):
  print "Accelerator", keyval, modifier
  return True


# window 
window = gtk.Window()
window.resize(400, 400) # TODO this resizes the surface and view?
window.move(400, 600)
window.connect('destroy', gtk.main_quit)
window.realize()

# load graphic
# pb = gdk.pixbuf_new_from_file('ufo-input.png')
#w, h = pb.get_width(), pb.get_height()

da = gtk.DrawingArea()

'''
This must precede realization of view? or use add_events().
First three are mouse events.
STRUCTURE is configure-event (resizing the window)
Last are focus and keyboard events.
'''
da.set_events( \
  gdk.BUTTON_PRESS_MASK \
  | gdk.POINTER_MOTION_MASK \
  | gdk.BUTTON_RELEASE_MASK \
  | gdk.STRUCTURE_MASK \
  | gdk.FOCUS_CHANGE_MASK\
  | gdk.KEY_RELEASE_MASK \
  | gdk.KEY_PRESS_MASK )
 
'''
Without this, the drawing area widget does not receive keyboard events:
focus_in, key_release, etc.
We are implementing our own widgets (controls) including text controls
that will receive keyboard.
Also, we implement our own *traversal* (via the tab key per convention)
among our controls that get the keyboard focus.
'''
da.set_flags( da.flags() | gtk.CAN_FOCUS )
  
window.add(da)

accelerators = gtk.AccelGroup()
window.add_accel_group(accelerators)
accelerators.connect_group(122, gdk.CONTROL_MASK, accel_flags=gtk.ACCEL_VISIBLE, callback=foo)
# gdk.GDK_Left

# Can draw to several ports.
a_view = port.ViewPort(da)
a_printerport = port.PrinterPort()
a_fileport = port.FilePort()
port.view = a_view  # Make view global singleton
# FIXME

scheme.initialize()

# Show so allocation becomes valid
window.show_all()


# The document, IE model.
'''
Initial model load from file.
TODO
'''


"""
"""
# Make separate morphs
arect = morph.morph.RectMorph()
acirc = morph.morph.CircleMorph()
apoint = morph.morph.PointMorph()
aline = morph.morph.LineMorph()

scheme.model.append(arect)
scheme.model.append(acirc)
scheme.model.append(apoint)
scheme.model.append(aline)
for item in scheme.model:
  item.set_dimensions(Rectangle(150.0/PENSOOL_UNIT, 150.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT))
apoint.set_dimensions(Rectangle(10.0/PENSOOL_UNIT, 50.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT))
aline.set_dimensions(Rectangle(20.0/PENSOOL_UNIT, 50.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT, 100.0/PENSOOL_UNIT))
  

# !!! Width, height of text are computed??
# atext.set_origin(Rectangle(150.0/PENSOOL_UNIT, 30.0/PENSOOL_UNIT, 0,0))
# TextEditMorph creates it's own selection
atext = morph.textmorph.TextEditMorph("Most relationships seem so transitory")
atext.set_dimensions(Rectangle(150.0/PENSOOL_UNIT, 30.0/PENSOOL_UNIT, 200.0/PENSOOL_UNIT, 200.0/PENSOOL_UNIT))
scheme.model.append(atext)

"""
# Make a group
arect = morph.morph.RectMorph()
arect.set_dimensions(Rectangle(50.0/PENSOOL_UNIT, 50, 50, 50))
acirc = morph.morph.CircleMorph()
acirc.set_dimensions(Rectangle(0, 0, 50, 50))

agroup = morph.morph.Morph()
agroup.append(arect)
agroup.append(acirc)
# Group at 30,30, scale 1
agroup.set_dimensions(Rectangle(30,30,1,1))
# agroup.append(atext)

scheme.model.append(agroup)
"""


''' 
Controls.
Build singletons (one instance) for each control type.
Exactly one control instance is active (has focus) at a time.
'''

# Enforces one control active
gui.manager.control.control_manager = gui.manager.control.ControlsManager()
controlinstances.build_all(a_printerport, a_fileport)
gui.manager.control.control_manager.set_root_control(controlinstances.bkgd_control)

'''
Initial active control is the background manager
None event is activating it.
Controlee is the bkgd_control itself.
'''
gui.manager.control.control_manager.activate_control(controlinstances.bkgd_control, controlinstances.bkgd_control)

a_view.set_model(scheme.model)
a_printerport.set_model(scheme.model)
a_fileport.set_model(scheme.model)

gtk.main()

