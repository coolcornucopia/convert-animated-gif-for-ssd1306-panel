import machine
from stm32_alphabot_v2 import AlphaBot_v2
from stm32_ssd1306 import SSD1306, SSD1306_I2C

import ssd1306_image_reader

alphabot = AlphaBot_v2()
oled = SSD1306_I2C(128, 64, machine.I2C(1))

def test_ssd1306_image_reader(filename):
    img_reader = ssd1306_image_reader.SSD1306_ImageReader(filename)
    print(str(img_reader))

    # Play the animation 2 times to check the loop
    frames = img_reader.frames * 2
    for frame in range(frames):
        print("{:5}/{} in progress...".format(frame + 1, frames))

        # Get the current frame
        img_buf = img_reader.next_frame()

        # Display it
        oled.send_buffer(img_buf)


print("TESTING an animation with compression")
test_ssd1306_image_reader("animated_python.128x64.36img.z")
input("Press enter")

print("TESTING an animation without compression")
test_ssd1306_image_reader("animated_python.128x64.36img.raw")
input("Press enter")

print("TESTING a still picture with compression")
test_ssd1306_image_reader("still_mycat.128x64.1img.z")
input("Press enter")

print("TESTING a still picture without compression")
test_ssd1306_image_reader("still_mycat.128x64.1img.raw")
input("Press enter")

print("TESTING an animation from a video with compression")
test_ssd1306_image_reader("video_Big_Buck_Bunny_monow.128x64.200img.z")
input("Press enter")
