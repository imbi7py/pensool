#!/usr/bin/env python

import gui.itemcontrol
import morph.glyph
from gtk import gdk
from decorators import *
import config
import base.vector as vector


class MenuItem(gui.itemcontrol.ItemControl):
  '''
  A classic menu item control:
    -appears anywhere (locatable)
    -fixed location after appears
    -doesn't dissappear on mouseexit
  
  For use in menus:
  
  Context menus:
  -click appearance
  -mouseout dissappearance
  -clickable
  -is managed
  '''
  
  '''
  Button release: choose menu item.
    
  '''
  @dump_event
  def button_release_left(self, event):
    # TODO
    pass
  
  @dump_event
  def button_release_right(self, event):
    ''' RMB Release: execute, close menu '''
    self.command(self.controlee, event)
    self.group_manager.close(event)
    gui.manager.control.control_manager.activate_root_control()
  
  @dump_event
  def start_drag(self, event):
    '''
    Filtered event from GuiControl.
    Overrides GuiControl.start_drag()
    This defines that can't drag an ordinary menu item.
    But GuiControl already changed drag state?
    cancel drag on mouse_exit?
    '''
    #TODO 
    gdk.beep()
    print "?????????????????Dragging a menu item"
    pass
  
  @dump_event
  def mouse_exit(self, event):
    '''
    Handler for filtered mouse_exit event.
    Tell my group manager which direction to go,
    depending on the side exited.
    For traditional, square menu items.
    
    !!! Note that control.py may use a different method to determine exit.
    Specifically, it may use in_fill() which is slightly different from bounds
    (because of inked strokes.)
    So it is not an error to get here and still be in bounds.
    '''
    # Note both bounds and event in DCS
    if event.y < self.bounds.y:  # above
      self.group_manager.previous(event)
    elif event.y > self.bounds.y + self.bounds.height:  # below
      self.group_manager.next(event)
    elif event.x < self.bounds.x : # left
      # Exit left means close the menu and put root control in charge
      print "Exit left"
      self.group_manager.close(event)
      gui.manager.control.control_manager.activate_root_control()
    elif event.x > self.bounds.x + self.bounds.width: # right
      # For now, close menu.
      # TODO traditional cascading
      self.group_manager.close(event)
      gui.manager.control.control_manager.activate_root_control()
    else:
      # control.py determined pointer is outside fill.
      # If control.py
      print "Exited item but not out of bounds."
   
  # @dump_event
  def mouse_move(self, event):
    ''' Pass because classic menu items do not move i.e. track the pointer. '''
    pass
    
    
class IconMenuItem(MenuItem):
  # For now a rect
  def __init__(self, command):
    super(MenuItem, self).__init__(command)
    
    self.append(morph.glyph.RectGlyph())
    self.relative_scale(config.ITEM_SIZE*2, config.ITEM_SIZE) # size


class TextMenuItem(MenuItem):
  
  def __init__(self, text, command):
    super(MenuItem, self).__init__(command)
    
    text_morph = morph.textmorph.TextMorph(text)
    self.append(text_morph)
    # !!! Must scale my morph the parent of the textglyph, not self
    text_morph.relative_scale(config.ITEM_SIZE*2, config.ITEM_SIZE) # size
    
  def __repr__(self):
    ''' For debugging, represent self by my text. '''
    return "TextMenuItem" + str(id(self)) + self[0].__repr__()
    

    
