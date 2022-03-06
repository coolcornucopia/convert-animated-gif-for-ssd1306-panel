#
# Various image helper functions for ssd1306-like Oled panel
#
# MIT License
#
# Copyright (c) 2022 coolcornucopia
#

def to_ssd1306(width:int, height:int, buf_in, buf_out):
    """Convert a 1-bit per pixel 2d image buffer to
       a 1-bit per pixel ssd1306-like image format buffer.
       Note: The output buffer previous content is preserved.

    Args:
        width (int): width in pixels
        height (int): height in pixels
        buf_in (_type_): input buffer
        buf_out (_type_): output buffer (ssd1306-like format)
    """

    stride_w = width // 8               # 1-bit per pixel, 1 byte = 8 pixels
    for y in range(height // 8):
        buf_in_pos  = y * stride_w * 8  # move 8 lines at a time
        buf_out_pos = y * width         # move to next page
        for x in range(stride_w):
            for z in range(8):
                a = buf_in[buf_in_pos + (z * stride_w)]
                buf_out[buf_out_pos + 0] |= ((a >> 7) & 1) << z
                buf_out[buf_out_pos + 1] |= ((a >> 6) & 1) << z
                buf_out[buf_out_pos + 2] |= ((a >> 5) & 1) << z
                buf_out[buf_out_pos + 3] |= ((a >> 4) & 1) << z
                buf_out[buf_out_pos + 4] |= ((a >> 3) & 1) << z
                buf_out[buf_out_pos + 5] |= ((a >> 2) & 1) << z
                buf_out[buf_out_pos + 6] |= ((a >> 1) & 1) << z
                buf_out[buf_out_pos + 7] |= ((a >> 0) & 1) << z
            buf_in_pos += 1
            buf_out_pos += 8


def from_ssd1306(width:int, height:int, buf_in, buf_out):
    """Convert a 1-bit per pixel ssd1306-like image format buffer to
       a 1-bit per pixel 2d image buffer.
       Note: The output buffer previous content is preserved.

    Args:
        width (int): width in pixels
        height (int): height in pixels
        buf_in (_type_): input buffer (ssd1306-like format)
        buf_out (_type_): output buffer
    """

    stride_w = width // 8               # 1-bit per pixel, 1 byte = 8 pixels
    for y in range(height // 8):
        buf_in_pos  = y * width         # move to next page
        buf_out_pos = y * stride_w * 8  # move 8 lines at a time
        for x in range(width // 8):
            for z in range(8):
                a = buf_in[buf_in_pos + z]
                buf_out[buf_out_pos + (0 * stride_w)] |= ((a >> 0) & 1) << (7 - z)
                buf_out[buf_out_pos + (1 * stride_w)] |= ((a >> 1) & 1) << (7 - z)
                buf_out[buf_out_pos + (2 * stride_w)] |= ((a >> 2) & 1) << (7 - z)
                buf_out[buf_out_pos + (3 * stride_w)] |= ((a >> 3) & 1) << (7 - z)
                buf_out[buf_out_pos + (4 * stride_w)] |= ((a >> 4) & 1) << (7 - z)
                buf_out[buf_out_pos + (5 * stride_w)] |= ((a >> 5) & 1) << (7 - z)
                buf_out[buf_out_pos + (6 * stride_w)] |= ((a >> 6) & 1) << (7 - z)
                buf_out[buf_out_pos + (7 * stride_w)] |= ((a >> 7) & 1) << (7 - z)
            buf_in_pos += 8
            buf_out_pos += 1
