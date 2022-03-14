class PCF8574:
  def __init__(self, i2c, addr=0x20):
    self._i2c = i2c
    i2cModules = self._i2c.scan()
    if addr not in i2cModules:
      error = "Unable to find module 'PCF8574' at address " + str(hex(addr)) + ". Please check connections with the board.\n"
      error += "[Info] I2C address.es detected: " + str([hex(a) for a in i2cModules])
      raise ValueError(error)
    self._addr = addr
    self._port = bytearray(1)

  @property
  def port(self):
    self._read()
    return self._port[0]

  @port.setter
  def port(self, value):
    self._port[0] = value & 0xff
    self._write()

  def pin(self, pin, value=None):
    pin = self.validate_pin(pin)
    if value is None:
        self._read()
        return (self._port[0] >> pin) & 1
    else:
      if value:
        self._port[0] |= (1 << (pin))
      else:
        self._port[0] &= ~(1 << (pin))
      self._write()

  def toggle(self, pin):
    pin = self.validate_pin(pin)
    self._port[0] ^= (1 << (pin))
    self._write()

  def validate_pin(self, pin):
    # pin valid range 0..7
    if not 0 <= pin <= 7:
      raise ValueError('Invalid pin {}. Use 0-7.'.format(pin))
    return pin

  def _read(self):
    self._i2c.readfrom_into(self._addr, self._port)

  def _write(self):
    self._i2c.writeto(self._addr, self._port)
