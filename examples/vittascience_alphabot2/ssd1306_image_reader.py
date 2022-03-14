"""
Image reader for ssd1306-like Oled panel
https://github.com/coolcornucopia/convert-animated-gif-for-ssd1306-panel

MIT License

Copyright (c) 2022 coolcornucopia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/coolcornucopia/convert-animated-gif-for-ssd1306-panel"

import sys
import zlib


# By default the zlib window size is set to its maximum for better compression results
# but it is possible to use -12 (4k) to preserve the micropython memory.
# Note: MicroPython: MAX_WBITS is not defined in zlib
if hasattr(zlib, "MAX_WBITS"):
    DEFAULT_ZLIB_WINDOW_SIZE = -zlib.MAX_WBITS
else:
    DEFAULT_ZLIB_WINDOW_SIZE = -15 # -zlib.MAX_WBITS is not available in micropython


# By default the compressed data are read with this chunk size. You may adapt it according
# to your filesystem and system memory usage...
COMPRESSED_CHUNK_SIZE = 512


class SSD1306_ImageReader:

    def __init__(self, filename):

        # We need to handle the MicroPython case unfortunately
        self.micropython = True
        if sys.implementation.name == 'cpython':
            self.micropython = False

        # Check if input file exits (not available in micropython)
        if not self.micropython:
            import os.path
            if not os.path.isfile(filename):
                print("Error: file {} does not exit!".format(filename), file=sys.stderr)
                exit(1) # exit with error

        self.filename = filename

        # Get information from the filename
        (self.width, self.height, self.frames, self.compression) = self.get_config_from_filename(self.filename)
        #print("debug:", str(self))

        self.buf_size_in_bytes = (self.width * self.height) // 8 # 1-bit per pixel

        # If the file is compressed, we read small chunks else we read the entire image

        if self.compression:
            if self.micropython:
                import io
                self.f = io.open(self.filename, "rb") # TODO manage errors
                self.z_obj = zlib.DecompIO(self.f, DEFAULT_ZLIB_WINDOW_SIZE)
            else:
                self.f = open(self.filename, "rb") # TODO manage errors
                self.z_obj = zlib.decompressobj(DEFAULT_ZLIB_WINDOW_SIZE)

            self.buf = bytearray(0) # empty buffer
            self.f_read_size = COMPRESSED_CHUNK_SIZE

        else:
            # No compression, we can read the entire image directly
            self.f = open(self.filename, "rb") # TODO manage errors
            self.f_read_size = self.buf_size_in_bytes

    def get_config_from_filename(self, filename):
        """Get information from the input filename ("filename.widthxheight.nimg.z" or ".raw")."""
        tmp = filename.split(".")
        width = int(tmp[-3].split("x")[0])
        height = int(tmp[-3].split("x")[1])
        frames = int(tmp[-2].split("img")[0])
        compression = False
        if tmp[-1] == "z":
            compression = True
        # TODO add various checks on parameters
        return (width, height, frames, compression)

    def __str__(self):
       return f"{self.width}x{self.height}, {self.frames} frame{'s' if self.frames > 1 else ''}, compression {self.compression}, {self.filename}"

    def __read_file_chunks_and_loop(self, size):
        buf = self.f.read(size)
        # loop the file if necessary
        if not buf:
            self.f.seek(0)
            buf = self.f.read(size)

        return buf

    def next_frame(self):
        if self.compression:
            if self.micropython:
                # MicroPython specific implementation
                while len(self.buf) < self.buf_size_in_bytes:
                    self.buf += self.z_obj.read(self.buf_size_in_bytes)
                    # Looping the animation
                    if not self.buf:
                        # Close then re-create the stream... as seek is not enough...
                        self.f.close()
                        import io # TODO why... but it looks necessary...
                        self.f = io.open(self.filename, "rb") # TODO manage errors
                        self.z_obj = zlib.DecompIO(self.f, DEFAULT_ZLIB_WINDOW_SIZE)
                        self.buf += self.z_obj.read(self.buf_size_in_bytes)
                    #print("1", "len(self.buf)", len(self.buf))

            else:
                # Standard Python implementation
                while len(self.buf) < self.buf_size_in_bytes:
                    data = self.z_obj.unconsumed_tail
                    if not data:
                        data = self.__read_file_chunks_and_loop(self.f_read_size)
                    else:
                        print("DEBUG ME: never happened? may depends on zlib version...")
                        pass
                    self.buf += self.z_obj.decompress(data)
                    #print("1", "len(b)", len(b), "len(self.buf)", len(self.buf))

            current_frame_buf = self.buf[:self.buf_size_in_bytes]
            self.buf = self.buf[self.buf_size_in_bytes : len(self.buf)]
            #print("2", "len(current_frame_buf)", len(current_frame_buf), "len(self.buf)", len(self.buf))

        else:
            # No compression: easy case, simply read image by image
            current_frame_buf = self.__read_file_chunks_and_loop(self.f_read_size)

        return current_frame_buf
