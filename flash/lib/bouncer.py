from machine import Pin, SPI
import machine
import time
import random

import display
import splash
import framebuf
from image import Image

import math

class Vector2:
  RECT = True
  POLAR = False
  def __init__(self, a, b, kind=RECT):
    if kind == self.RECT: 
      self.rect(a, b)
    if kind == self.POLAR: 
      self.polar(a, b)
  def polar( self, mag=None, ang=None, ):
    if mag is None and ang is None:
      return (self.mag, self.ang)
    if mag is not None and ang is not None:
      self.mag = mag
      if ang > 180:    self.ang = ang - 360
      elif ang < -180: self.ang = ang + 360
      else:            self.ang = ang
      self.polar2rect()
  def rect( self, x=None, y=None, ):
    if x is None and y is None:
      return (self.x, self.y)
    if x is not None and y is not None:
      self.x = x
      self.y = y
      self.rect2polar()
  def rect2polar( self ):
    self.mag = math.sqrt(self.x*self.x + self.y*self.y)
    self.ang = math.atan2( self.y, self.x ) * 180.0 / math.pi
  def polar2rect( self ):
    rad = self.ang * math.pi / 180.0
    self.x = self.mag * math.cos(rad)
    self.y = self.mag * math.sin(rad)
  def __repr__(self):
    out = []
    out.append( f' RECT (x,y) = ({self.x:12.3f}, {self.y:12.3f})' )
    out.append( f'POLAR (r,a) = ({self.mag:12.3f}, {self.ang:12.3f})' )
    return  '\n'.join( out )
  def __str__(self):
    return self.__repr__()

#from dplogo import icon
#from wrencher import icon
from buslogo import icon
class Bouncer:
  def __init__(self, disp, lamps, sw2):
    self.disp = disp
    self.tft = disp.tft
    self.lamps = lamps
    self.sw2 = sw2
    self.tft.fill(0)
    self.W = self.disp.width
    self.H = self.disp.height
    self.diag = math.sqrt( self.H*self.H + self.W*self.W )
    self.vppms = self.diag / 2.0 / 1000.0 # pixels / msec
    self.v = Vector2( self.vppms, 45, False )
    self.x = 0
    self.y = 0
    self.xold = self.x
    self.yold = self.y
    # self.icon = dplogo.dplogo
    self.icon = icon
    self.w = self.icon.wid
    self.h = self.icon.hgt
    self.fb_icon = framebuf.FrameBuffer(self.icon.buf, 
                   self.icon.wid, self.icon.hgt, 
                   self.icon.packing )
                   #framebuf.GS4_HMSB ) 
                   # self.wid, self.hgt, framebuf.RGB565) 
    # make paletter for monochrome blit
    # self.bg = 0
    # self.fg = 15
    # self.palette = FrameBuffer(bytearray(1), 2, 1, GS4_HMSB)
    # self.palette.pixel(1, 0, self.fg)
    # self.palette.pixel(0, 0, self.bg)
    #target.blit(source, 0, 0, -1, palette)

    self.dt = 25
    self.spin_angle = 2 # degress of angle randomness
    self.spin_speed = 2 # percent speed randomness


  def spin(self):
    speed, angle = self.v.polar()
    speed = speed + (self.spin_speed/100.0) * speed * random.random()
    angle = angle + self.spin_angle * random.random()
    self.v.polar( speed, angle )

  def move(self, dt):
    self.x = self.x + self.v.x * dt
    self.y = self.y + self.v.y * dt

  def go(self):
    self.disp.cls()
    while True:
      #print(f'{self.x}, {self.y}')
      self.tft.fill_rect(
        round(self.xold), round(self.yold),
        self.icon.wid, self.icon.hgt, 0
      )
      time.sleep_us(100)
      self.tft.blit_buffer( self.fb_icon, 
        round(self.x), round(self.y),
        self.icon.wid, self.icon.hgt
      )

      self.xold = self.x
      self.yold = self.y
      self.move(self.dt)
      bounced = self.rebound()
      if not bounced: time.sleep_ms(self.dt)
      if self.sw2(): break

    self.disp.cls()

  def rebound(self):
    top =    self.y < (   0.0 - 0.10*self.h)
    bottom = self.y > (self.H - 0.90*self.h)
    left =   self.x < (   0.0 - 0.10*self.w)
    right =  self.x > (self.W - 0.90*self.w)
    if top or bottom:
      self.v.polar( self.v.mag, -self.v.ang )
      self.spin()
      if top: self.lamps.on_group( self.lamps.north.both, dwell=self.dt )
      elif bottom: self.lamps.on_group( self.lamps.south.both, dwell=self.dt )
      return True
    elif left or right:
      self.v.polar( self.v.mag, 180.0 - self.v.ang )
      self.spin()
      if left: self.lamps.on_group( self.lamps.west.both, dwell=self.dt )
      elif right: self.lamps.on_group( self.lamps.east.both, dwell=self.dt )
      return True
    return False   

