#!/usr/bin/env python

'''
Pointer manager: state machine for pointer movement.
The pointer must remain within a few pixels
for a short time
before mouseover (picking) is done.

Alternatively, we could pick at every mouse move, and delay the result
of the pick until it was confirmed a short time later.
But that requires efficient picking so as not to be jerky.

Here we use the mouse speed in pixel distance per second (?).
Using absolute mouse move distances is subject to jitter
and system busy problems.

We might be able to reconstruct a more accurate mouse position (float)
by averaging with previous mouse position.
The drawing library is in floating point, why not use mouse position in float?

!!! Note that the callback is asynchronous.
In general, it must be prepared for a race condition.
For example, the user may have just opened a menu using for example a control key,
and the callback must not interfere.
'''

import base.vector as vector
import base.timer as timer
import config
from decorators import *

# globals
state = None
previous_point = vector.Vector(0,0)
previous_time = 0
pointer_timer = timer.Timer()
stopped_callback = None


def register_callback(func):
  '''
  Register a function to callback when pointer is stopped.
  Typically a pick for mouseover.
  '''
  global stopped_callback
  stopped_callback = func

def cancel_timer():
  ''' 
  Cancel my timer. Usually means pointer manager is not being used.
  See below: decide_stopped() may later be called and can restart timer.
  '''
  pointer_timer.cancel()

# @dump_return
def decide_stopped(event):
  '''
  Decide whether pointer is more or less stationary,
  given pointer movement event.
  A state machine.
  '''
  global state, previous_point, previous_time, pointer_timer
  
  move = vector.Vector(event.x, event.y)
  motion_vector = move - previous_point
  previous_point = move
  distance = motion_vector.length()
  elapsed = event.time - previous_time
  previous_time = event.time
  if elapsed <= 0:
    # event.time rolled over, wait for another mouse move.
    # Or, mouse moving so fast the event.time is the same,
    # avoid division by zero.
    return  
  speed = distance/elapsed
  # print distance, elapsed, speed
  
  if state is "moving":
    if speed <= config.GUI_MOVING_SLOWING_THRESHOLD:
      state = "slowed"
      pointer_timer.start(config.GUI_MOVING_POPUP_TIME, timeout_cb) # after a delay, go to stopped state
    # else moved fast
  elif state is "slowed":
    if speed > config.GUI_MOVING_SLOWING_THRESHOLD:
      state = "moving"
      pointer_timer.cancel()
    # else same state  still slow motion
  elif state is "stopped":
    if speed <= config.GUI_MOVING_SLOWING_THRESHOLD:
      # slow motion from stopped, try pick if user is making small adjustment
      # if it is acceleration, hope nothing to pick
      if stopped_callback(move):
        state = None
      # else, probably acceleration but don't change state
    else: # fast motion again
      state = "moving"
  else:  # Null state, the starting state.
    state = "moving"
  return state

    
# @dump_event
def timeout_cb():
  '''
  Timer went off.
  Enter stopped state and attempt a pick
  '''
  global state, pointer_timer
  
  if not pointer_timer.was_canceled():
    if state is "slowed" or state is "stopped":
      state = "stopped"
      # callback now, if pointer is not moving won't be move events
      if stopped_callback(previous_point):
        # Return False so timer quits.  Otherwise it continues.
        return False
      else:
        # pick failed, let timer run in stopped state to keep trying
        return True
  

