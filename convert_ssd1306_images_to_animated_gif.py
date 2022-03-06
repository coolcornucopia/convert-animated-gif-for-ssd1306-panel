#!/usr/bin/env python3

# TODO add a parameter to show the input/output results in windows
# TODO tester avec un nom de fichier complexe comme "th a.n.o.s.128x64.45.raw"
# TODO add a verbose parameter
# TODO tester avec une seule image (sans animation)
# TODO stocker 3 gif: une seule image, une animation simple, une video complexe

import argparse
import os.path
import sys
import zlib

from PIL import Image
from PIL.GifImagePlugin import GifImageFile

import ssd1306_image_converter

# By default, the zlib window size is set to -12 (4k) to preserve the micropython memory
# but it is possible to use -zlib.MAX_WBITS for better performances
default_zlib_window_size = -12


chunk_size = 1024  # TODO could be adjusted, at least to 4096

debug = True

def get_pil_image_info_str(img) -> str:
    str = "{}x{} mode {}".format(img.width, img.height, img.mode)
    if img.format != None:
        str += ", {}".format(img.format)
    if hasattr(img, 'n_frames'):
        str += ", {} frames".format(img.n_frames) if img.n_frames > 1 else "single frame"
    if hasattr(img, 'filename'):
        str += ", {}".format(img.filename)
    return str


def convert(verbose, overwrite, input_filename, zlib_window_size=default_zlib_window_size):
    # Check if input file exits
    if not os.path.isfile(input_filename):
        print("Error: file {} does not exit!".format(input_filename), file=sys.stderr)
        exit(1) # exit with error

    # Get information from the input filename ("filename.widthxheight.z" or ".raw")
    tmp = input_filename.split(".")
    width = int(tmp[-2].split("x")[0])
    height = int(tmp[-2].split("x")[1])
    output_filename = "{}-generated.gif".format(".".join(tmp[:-2]))
    if debug:
        print(tmp[-1], tmp[-2], width, height, output_filename)

    # Determine if the file is compressed of not and prepare the related decompression
    compression = False
    if tmp[-1] == "z":
        compression = True
        img_in_decompress = zlib.decompressobj(zlib_window_size)
    
    # Check if output file already exists...
    if os.path.isfile(output_filename):
        if not overwrite:
            print("Error: file {} already exits, please delete it or use the proper option to overwrite it!".format(output_filename),
                  file=sys.stderr)
            exit(1) # exit with error
        else:
            if verbose:
                print("Warning: file {} already exits and will be overwritten.".format(output_filename))

    img_in_file = open(input_filename,"rb")

    img_out_buf_size_in_bytes = (width * height) // 8 # 1-bit per pixel
    img_out_buf = bytearray(img_out_buf_size_in_bytes)
    img_out_buf_pos = 0

    img_out = [] # a table of frames (or a single frame)

    # Read the file chunk by chunk
    buf = img_in_file.read(chunk_size)
    buf_size = len(buf)
    if buf_size <= 4:
        print("Error: input file {} is empty or too small".format(input_filename), file=sys.stderr)
        exit(1) # exit with error

    while buf:
        if compression:
            buf = img_in_decompress.decompress(buf) # TODO decompression in place, maybe not so nice
        
        # TODO use memoryview?
        # TODO optimize this code?
        if len(buf) <= img_out_buf_size_in_bytes - img_out_buf_pos:
            img_out_buf[img_out_buf_pos : img_out_buf_pos + len(buf)] = buf
            img_out_buf_pos += len(buf)
            if img_out_buf_pos == img_out_buf_size_in_bytes:
                img_out_buf_pos = 0
                # Convert the buffer from ssd1306 format to "classic" format
                tmp = bytearray(img_out_buf_size_in_bytes) # zeroified by default
                ssd1306_image_converter.from_ssd1306(width, height, img_out_buf, tmp)
                # Create a 1-bit PIL image then convert it in palette mode (gif needs palette mode)
                img = Image.frombuffer("1", (width, height), bytes(tmp), "raw", "1", 0, 1)
                img = img.convert("P")
                if verbose:
                    print(get_pil_image_info_str(img))

                img_out.append(img)
                print("append")
            
        else:
            pass
        

        buf = img_in_file.read(chunk_size)
        buf_size += len(buf)

    print(len(buf), buf_size)
    img_in_file.close()


    # TODO save a single GIF if there is a single image!!!

    # Save as animated gif with infinite loop
    # TODO maybe add a parameter for default duration
    img_out[0].save(output_filename,  save_all = True, append_images = img_out[1:], optimize = True, duration = 50, loop = 0)



def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] filename.gif",
        description=
        """
Convert an animated GIF (or a single image GIF) to an image file for ssd1306-like OLED panel.

Notes:
 - The ssd1306 image filename uses the format filename.WidthxHeight.Frames.raw (.z if compressed).
   For example "my_animation.128x64.42.z".""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("filename")
    parser.add_argument("-f", "--force",    action="store_true", help="force overwrite")
    parser.add_argument("-v", "--verbose",  action="store_true", help="explain what is being done")
    return parser

def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if debug:
        print(args)

    convert(args.verbose, args.force, args.filename)

if __name__ == "__main__":
    main()
