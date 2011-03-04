#!/usr/bin/env python

from decorators import *
import scheme
import port

class ControlsManager():
  '''
  Manages active-ness in a set of controls on a view or window (gtk object that generates events)
  Only one is active at a time.
  Here active means: receiving events, callbacks connected. Also called focus.
  Controls are anonymous here: not keeping references to them.
  Other aspects of controls are also managed by group managers such as menus.
  '''
  
  def __init__(self):
    self.current_control = None
    self.root_control = None


  def is_root_control_active(self):
    ''' 
    Is root control already active?
    Used in race conditions.
    '''
    return self.current_control is self.root_control
    
    
  def set_root_control(self, control):
    '''
    Set root control which takes events when no other control does.
    The events below always go to the root control, not to the active control.
    '''
    self.root_control = control
    port.view.da.connect('configure-event', control.configure_event_cb)
    port.view.da.connect('focus-in-event', control.focus_in_event_cb)

  
  #@dump_event
  def _disconnect_callbacks(self):
    if self.current_control is not None:
      port.view.da.disconnect(self.current_motion_handler)
      port.view.da.disconnect(self.current_press_handler)
      port.view.da.disconnect(self.current_release_handler)
      port.view.da.disconnect(self.current_scroll_handler)
      port.view.da.disconnect(self.current_key_handler)
    
    
  @dump_event
  def activate_control(self, control, controlee):
    '''
    Activate control.
    Also change focus???
    '''
    # Must be preceded by deactivate or have just started app
    assert self.current_control is None
    
    # Reconnect events.   Mouse and keyboard.
    self.current_press_handler = port.view.da.connect('button-press-event', control.button_press_event_cb)
    self.current_motion_handler = port.view.da.connect('motion-notify-event', control.motion_notify_event_cb)
    self.current_release_handler = port.view.da.connect('button-release-event', control.button_release_event_cb)
    self.current_scroll_handler = port.view.da.connect('scroll-event', control.scroll_event_cb)
    self.current_key_handler = port.view.da.connect_after('key-release-event', control.key_release_event_cb)
    
    # change focus (invalidates?)
    # FIXME current_control should be None already
    if self.current_control is not None:
      self.current_control.take_focus(False)
      
    control.take_focus(True)
      
    self.current_control = control
    control.controlee = controlee
    
    
  def draw_active_control(self, context):
    self.current_control.draw(context)
  
  def deactivate_current_control(self):
    '''
    Caller must soon reactivate some control or the app will be dead.
    ## OLD Only call this if no controls will be active (except the root)
    '''
    ## OLD The background manager should not deactivate itself
    ## OLD assert(control is not self.root_control)
    self.current_control.deactivate()   # Control's own, special deactivation
    self._disconnect_callbacks()
    self.current_control = None
  
  def activate_root_control(self):
    '''
    Activate the background manager
    More generally, the root control.
    This is the second place where defined that background manager controls itself.
    '''
    assert self.current_control is None
    self.activate_control(self.root_control, self.root_control)

  
  '''
  The drawing portion of control management: only one control is drawn at a time.
  Just like only one control is receiving events at a  time.
  Note that the same control being drawn (e.g. a menu)
  might not be the control receiving events (e.g. an item of the menu.)
  '''
  
  def add_to_drawlist(self, drawable):
    '''
    '''
    print ">>>>>>>>>>>>>>>Adding control", drawable
    # Only one control can be open at a time
    assert len(scheme.widgets) == 0
    scheme.widgets.append(drawable)
  
  @dump_event
  def remove_from_drawlist(self, drawable):
    try:
      scheme.widgets.remove(drawable) # hide
    except ValueError:
      print "Failed to remove", drawable
      print "Scheme.widgets", scheme.widgets
      raise


  def get_active_control(self):
    ''' Return the active control '''
    return self.current_control
    
    
# singleton instance, initialized when port is known
control_manager = None



