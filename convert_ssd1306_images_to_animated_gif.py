#!/usr/bin/env python3

import argparse
import os.path
import sys

from PIL import Image
from PIL.GifImagePlugin import GifImageFile

import ssd1306_image_converter
import ssd1306_image_reader


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


def convert(verbose, overwrite, input_filename):
    img_reader = ssd1306_image_reader.SSD1306_ImageReader(input_filename)
    w = img_reader.width
    h = img_reader.height

    # Prepare output filename
    tmp = input_filename.split(".")
    output_filename = "{}-generated.gif".format(".".join(tmp[:-3])) # -3 to remove 128x64.45img.raw

    if debug:
        print("debug:", str(img_reader), "output", output_filename)

    # Check if output file already exists...
    if os.path.isfile(output_filename):
        if not overwrite:
            print("Error: file {} already exits, please delete it or use the proper option to overwrite it!".format(output_filename),
                  file=sys.stderr)
            exit(1) # exit with error
        else:
            if verbose:
                print("Warning: file {} already exits and will be overwritten.".format(output_filename))

    img_out = [] # a table of frames (or a single frame)

    for frame in range(img_reader.frames):
        if verbose:
            print("{:5}/{} in progress...".format(frame + 1, img_reader.frames))

        # Get the current frame
        img_buf = img_reader.next_frame()

        # Convert to 2d image
        tmp = bytearray(img_reader.buf_size_in_bytes) # zeroified by default
        ssd1306_image_converter.from_ssd1306(w, h, img_buf, tmp)

        # Create a 1-bit PIL image then convert it in palette mode (gif needs palette mode)
        img_pil = Image.frombuffer("1", (w, h), bytes(tmp), "raw", "1", 0, 1)
        img_pil = img_pil.convert("P")
        #if verbose:
        #    print(get_pil_image_info_str(img))

        img_out.append(img_pil)

    # Save as animated gif with infinite loop
    # TODO maybe add a parameter for default duration
    # TODO maybe add a parameter for default loop
    img_out[0].save(output_filename, save_all = True, append_images = img_out[1:], optimize = True, duration = 50, loop = 0)

    if verbose:
        print("{} successfully generated :-)".format(output_filename))


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] filename",
        description=
        """
Convert an image file for ssd1306-like OLED panel to an animated GIF (or a single image GIF).

Notes:
 - The ssd1306 image filename uses the format filename.WidthxHeight.Nimg.raw (.z if compressed).
   For example "my_animation.128x64.42img.z".
 - The animated GIF filename is "my_animation-generated.gif".""",
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
