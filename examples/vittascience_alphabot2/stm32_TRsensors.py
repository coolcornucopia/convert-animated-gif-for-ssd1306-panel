"""
QTRSensors.h - Originally Arduino Library for using Pololu QTR reflectance sensors and reflectance sensor arrays

MIT Licence
Copyright (c) 2008-2012 waveshare Corporation. For more information, see
https://www.waveshare.com/wiki/AlphaBot2-Ar

Copyright (c) 2021 leomlr (Léo Meillier). For more information, see
https://github.com/vittascience/stm32-libraries
https://vittascience.com/stm32/

You may freely modify and share this code, as long as you keep this notice intact.  

Disclaimer: To the extent permitted by law, waveshare provides this work
without any warranty.  It might be defective, in which case you agree
to be responsible for all resulting costs and damages.

Author: Léo Meillier (leomlr)
Date: 07/2021
Note: library adapted in micropython for using 5 QTR sensors on Alphabot v2 robot controlled by STM32 board.
"""

import pyb
from micropython import const
import utime

PIN_CS = 'D10'
PIN_DOUT = 'D11'
PIN_ADDR = 'D12'
PIN_CLK = 'D13'

NUMSENSORS = const(5)

QTR_EMITTERS_OFF = const(0x00)
QTR_EMITTERS_ON = const(0x01)
QTR_EMITTERS_ON_AND_OFF = const(0x02)

QTR_NO_EMITTER_PIN = const(0xff)

QTR_MAX_SENSORS = const(16)

class TRSensors(object):

  """ Base class data member initialization (called by derived class init()). """
  def __init__(self, cs=PIN_CS, dout=PIN_DOUT, addr=PIN_ADDR, clk=PIN_CLK):

    self._cs = pyb.Pin(cs, pyb.Pin.OUT)
    self._dout = pyb.Pin(dout, pyb.Pin.IN)
    self._addr = pyb.Pin(addr, pyb.Pin.OUT)
    self._clk = pyb.Pin(clk, pyb.Pin.OUT)

    self._numSensors = NUMSENSORS

    self.calibratedMin = [0] * self._numSensors
    self.calibratedMax = [1023] * self._numSensors
    self.last_value = 0

  """ Reads the sensor values using TLC1543 ADC chip into an array. 
  The values returned are a measure of the reflectance in abstract units,
  with higher values corresponding to lower reflectance (e.g. a black
  surface or a void). """

  def analogRead(self):
    value = [0]* (self._numSensors+1)
    #Read Channel0~channel4 AD value
    for j in range(0, self._numSensors+1):
      self._cs.off()
      for i in range(0,4):
        #sent 4-bit Address
        if (j >> (3 - i)) & 0x01:
          self._addr.on()
        else:
          self._addr.off()
        #read MSB 4-bit data
        value[j] <<= 1
        if self._dout.value():
          value[j] |= 0x01
        self._clk.on()
        self._clk.off()
      for i in range(0, self._numSensors+1):
        #read LSB 8-bit data
        value[j] <<= 1
        if self._dout.value():
          value[j] |= 0x01
        self._clk.on()
        self._clk.off()
      #no mean ,just delay
      #for i in range(0,6):
      #  self._clk.on()
      #  self._clk.off()
      utime.sleep_us(100)
      self._cs.on()
    return value[1:]

  """ Reads the sensors 10 times and uses the results for
  calibration.  The sensor values are not returned instead, the
  maximum and minimum values found over time are stored internally
  and used for the readCalibrated() method. """

  def calibrate(self):
    sensor_values = []
    max_sensor_values = [0]*self._numSensors
    min_sensor_values = [0]*self._numSensors

    for j in range(0, 10):
      sensor_values = self.analogRead()
      for i in range(0, self._numSensors):
        # set the max we found THIS time
        if j == 0 or max_sensor_values[i] < sensor_values[i]:
          max_sensor_values[i] = sensor_values[i]
        # set the min we found THIS time
        if j == 0 or min_sensor_values[i] > sensor_values[i]:
          min_sensor_values[i] = sensor_values[i]

    # record the min and max calibration values
    for i in range(0, self._numSensors):
      if min_sensor_values[i] > self.calibratedMax[i]:
        self.calibratedMax[i] = min_sensor_values[i]
      if max_sensor_values[i] < self.calibratedMin[i]:
        self.calibratedMin[i] = max_sensor_values[i]

  """ Returns values calibrated to a value between 0 and 1000, where
  0 corresponds to the minimum value read by calibrate() and 1000
  corresponds to the maximum value.  Calibration values are
  stored separately for each sensor, so that differences in the
  sensors are accounted for automatically. """

  def readCalibrated(self):

    # read the needed values
    sensor_values = self.analogRead()

    for i in range(self._numSensors):
      denominator = self.calibratedMax[i] - self.calibratedMin[i]
      value = 0
      if denominator is not 0:
        value = (sensor_values[i] - self.calibratedMin[i]) * 1000 / denominator
      if value < 0:
        value = 0
      elif value > 1000:
        value = 1000
      sensor_values[i] = value

    return sensor_values

  """ Operates the same as read calibrated, but also returns an
  estimated position of the robot with respect to a line. The
  estimate is made using a weighted average of the sensor indices
  multiplied by 1000, so that a return value of 0 indicates that
  the line is directly below sensor 0, a return value of 1000
  indicates that the line is directly below sensor 1, 2000
  indicates that it's below sensor 2000, etc.  Intermediate
  values indicate that the line is between two sensors.  The
  formula is:

      0*value0 + 1000*value1 + 2000*value2 + ...
     --------------------------------------------
         value0  +  value1  +  value2 + ...

  By default, this function assumes a dark line (high values)
  surrounded by white (low values).  If your line is light on
  black, set the optional second argument white_line to true.  In
  this case, each sensor value will be replaced by (1000-value)
  before the averaging. """

  def readLine(self, white_line = 0):

    sensor_values = self.readCalibrated()
    avg = 0
    sum = 0
    on_line = 0
    for i in range(0, self._numSensors):
      value = sensor_values[i]
      if white_line:
        value = 1000-value
      # keep track of whether we see the line at all
      if value > 200:
        on_line = 1
        
      # only average in values that are above a noise threshold
      if value > 50:
        avg += value * (i * 1000)  # this is for the weighted total,
        sum += value               # this is for the denominator 

    if on_line != 1:
      # If it last read to the left of center, return 0.
      if self.last_value < (self._numSensors - 1)*1000/2:
        #print("left")
        self.last_value = 0
  
      # If it last read to the right of center, return the max.
      else:
        #print("right")
        self.last_value = (self._numSensors - 1)*1000

    else:
      self.last_value = avg/sum
    
    return self.last_value,sensor_values;
