#!/usr/bin/env python



class Style(object):
  
  def __init__(self):
    self.stroke_width = 1
    self.color = (0, 0, 0)
    self.previous_color = None
    
  def put_to(self, context):
    context.set_source_rgba(self.color[0], self.color[1], self.color[2], 0.5) # black pen, 50% opacity
    # Line width is subject to transform CTM.
    # The spec in a style is in device coords (pixels.)
    # Convert to user coords.
    ux, uy = context.device_to_user_distance (self.stroke_width, self.stroke_width)
    if ux < uy :
      ux = uy
    context.set_line_width(ux)
    
  def highlight(self, direction):
    if direction:
      self.previous_color = self.color
      self.color = (50, 0, 0)
    else:
      # If unhilight without a prior highlight.
      # EG when you add a morph to a highlighted group.
      if self.previous_color is not None:
        self.color = self.previous_color
