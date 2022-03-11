#!/usr/bin/env python3

import argparse
import os.path
import sys
import zlib

from PIL import Image
from PIL.GifImagePlugin import GifImageFile

import ssd1306_image_converter
import ssd1306_image_reader

# By default, we use do not use the dithering when converting the GIF to 1-bit per pixel
# It may be useful when the animated GIF uses a lot of colors (videos...)
default_dither_method = Image.NONE # or Image.FLOYDSTEINBERG

debug = False


def get_pil_image_info_str(img) -> str:
    str = "{}x{} mode {}".format(img.width, img.height, img.mode)
    if img.format != None:
        str += ", {}".format(img.format)
    if hasattr(img, 'n_frames'):
        str += ", {} frames".format(img.n_frames) if img.n_frames > 1 else "single frame"
    if hasattr(img, 'filename'):
        str += ", {}".format(img.filename)
    return str


def convert(verbose, compression, overwrite, input_filename,
            zlib_window_size=ssd1306_image_reader.DEFAULT_ZLIB_WINDOW_SIZE,
            dither_method=default_dither_method):
    # Check if input file exits
    if not os.path.isfile(input_filename):
        print("Error: file {} does not exit!".format(input_filename), file=sys.stderr)
        exit(1) # exit with error

    # Load animation file with PIL
    img_in = Image.open(input_filename)
    if verbose:
        print("input image : {}".format(get_pil_image_info_str(img_in)))

    #img_in.seek(0)
    #img_in.show("default")

    # Determine the number of frames
    if hasattr(img_in, 'n_frames'):
        n_frames = img_in.n_frames  # Animated GIF case
    else:
        n_frames = 1                # Single frame image (PNG, GIF...)

    # Prepare the output filename (from "filename.gif" to "filename.widthxheight.nimg.z" or ".raw")
    output_filename = "{}.{}x{}.{}img".format(input_filename.rsplit('.', 1)[0], img_in.width, img_in.height, n_frames)
    if compression:
        output_filename = "{}.z".format(output_filename)
    else:
        output_filename = "{}.raw".format(output_filename)
    if verbose:
        print("output image: {}".format(output_filename))

    # Check if output file already exists...
    if os.path.isfile(output_filename):
        if not overwrite:
            print("Error: file {} already exits, please delete it or use the proper option to overwrite it!".format(output_filename),
                  file=sys.stderr)
            exit(1) # exit with error
        else:
            if verbose:
                print("Warning: file {} already exits and will be overwritten.".format(output_filename))

    img_out_file = open(output_filename, "wb") # TODO better manage errors

    # Prepare the compression if necessary
    if compression:
        img_out_compress = zlib.compressobj(9, zlib.DEFLATED, zlib_window_size)

    for frame in range(n_frames):
        if verbose:
            print("{:5}/{} in progress...".format(frame + 1, n_frames))

        img_in.seek(frame)

        # Convert in 1-bit (black & white), stored with 1 pixel per byte in PIL buffer (0, 1)
        img_tmp = img_in.convert("1", dither = dither_method)
        if debug:
            print("tmp image: {}".format(get_pil_image_info_str(img_tmp)))

        # Extract the buffer from the current frame
        img_tmp_buf = img_tmp.tobytes(encoder_name = "raw")

        # Convert to ssd1306 format (TODO add a documentation link somewhere) 
        img_out_buf = bytearray((img_in.width * img_in.height) // 8)
        ssd1306_image_converter.to_ssd1306(img_in.width, img_in.height, img_tmp_buf, img_out_buf)

        # Compress the buffer if requested
        if compression:
            # TODO check compress returned value?
            img_out_compressed_buf = img_out_compress.compress(img_out_buf)
            # Save the buffer to disk
            img_out_file.write(img_out_compressed_buf) # TODO better manage errors
        else:
            # Save the buffer to disk
            img_out_file.write(img_out_buf) # TODO better manage errors

    # Close the file
    if compression:
        img_out_compressed_buf = img_out_compress.flush()
        # Save the buffer to disk
        img_out_file.write(img_out_compressed_buf) # TODO better manage errors

    img_out_file.close()

    if verbose:
        print("{} successfully generated :-)".format(output_filename))


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] filename.gif",
        description=
        """
Convert an animated GIF (or a single image GIF) to an image file for ssd1306-like OLED panel.

Notes:
 - The ssd1306 image filename uses the format filename.WidthxHeight.Nimg.raw (.z if compressed).
   For example "my_animation.128x64.42img.z".""",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("filename")
    parser.add_argument("-c", "--compress", action="store_true", help="compress output (zlib)")
    parser.add_argument("-f", "--force",    action="store_true", help="force overwrite")
    parser.add_argument("-v", "--verbose",  action="store_true", help="explain what is being done")
    return parser

def main() -> None:
    parser = init_argparse()
    args = parser.parse_args()
    if debug:
        print(args)

    convert(args.verbose, args.compress, args.force, args.filename)

if __name__ == "__main__":
    main()
