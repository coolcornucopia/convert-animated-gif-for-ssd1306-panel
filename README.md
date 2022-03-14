# Convert animated gif & videos for ssd1306-like OLED panel :rainbow: :sparkles:
The goal of this github repo is to offer Python :snake: scripts for **converting animated gif, still pictures (gif, jpeg, png...) and videos (mp4, webm...) in the ssd1306-like OLED panel format, with an optional zlib compression**. You will also find **MicroPython :snake: examples** for demonstrating on a "real case" how to use the converted images...

The ssd1306 OLED panel is pretty famous on Arduino/Nucleo-based electronic devices, like on the [AlphaBot2-Ar](https://www.waveshare.com/wiki/AlphaBot2-Ar) from [Waveshare](https://www.waveshare.com/). You can also find it on the [Mars rover - WB55 version](https://en.vittascience.com/shop/275/Robot-martien---version-Nucleo-WB55RG) from [vittascience](https://en.vittascience.com/).

The **zlib feature** combined with the **ssd1306 conversion** saves both CPU and disk usage:
* **300bytes** for a full screen still picture!
* **3kb** for an animated gif with 36 full screen frames!
* **47kb** for a complex video with 200 full screen frames!


![Animated gif, still picture and video on the VittaScience Robot Martien](examples/alphabot2_example.gif).

 > **Notes**
 > - The above video example is the famous [Big Buck Bunny](https://studio.blender.org/films/big-buck-bunny/?asset=263) from [Blender Studio](https://studio.blender.org) under the license [CC-BY](https://creativecommons.org/licenses/by/4.0/), converted to fit the size of the animated gif, more details [below](#video_big_buck_bunny_details).
 > - The above black cat picture is from [Gretchen Auer on UnSplash](https://unsplash.com/photos/EMnLrtASNKE) and is under the [Unsplash License](https://unsplash.com/license), more details [below](#still_mycat_details).

---

**Table of contents**
<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [How to use the scripts](#how-to-use-the-scripts)
- [Result examples](#result-examples)
- [How to use the generated images in MicroPython](#how-to-use-the-generated-images-in-micropython)
- [Extra: Use ffmpeg for converting video to animated gif](#extra-use-ffmpeg-for-converting-video-to-animated-gif)
- [Other possible solutions with different dependencies](#other-possible-solutions-with-different-dependencies)
- [Any questions or comments are welcome :bird:](#any-questions-or-comments-are-welcome-bird)

<!-- /code_chunk_output -->


## How to use the scripts
The main Python script is **"convert_animated_gif_to_ssd1306_images.py"**.

The only dependency is [Pillow (the friendly fork of PIL Python Imaging Library)](https://python-pillow.org/). You can install it with ```pip install pillow``` or get more details from the [Pillow installation documentation](https://pillow.readthedocs.io/en/stable/installation.html).

Hereafter few script examples:
``` bash
# Get the help
./convert_animated_gif_to_ssd1306_images.py --help

# Convert an animated GIF without compression (result: examples/animated_python.128x64.36img.raw)
./convert_animated_gif_to_ssd1306_images.py examples/animated_python.gif

# Convert an animated GIF with compression (result: examples/animated_python.128x64.36img.z)
./convert_animated_gif_to_ssd1306_images.py examples/animated_python.gif --compress
```

The Python script **"convert_ssd1306_images_to_animated_gif.py"** is useful to check the content of the .raw and .z images by converting them into the GIF format.
``` bash
# Get the help
./convert_ssd1306_images_to_animated_gif.py --help

# Check the conversion (result: animated_python-generated.gif)
./convert_ssd1306_images_to_animated_gif.py examples/animated_python.128x64.36img.z

# Check the conversion with overwrite & 20ms animation delay (result: animated_python-generated.gif)
./convert_ssd1306_images_to_animated_gif.py examples/animated_python.128x64.36img.raw -f -d 20

# Then, open the generated gif with your favorite viewer (web browser, gimp, eog...)
```

## Result examples

| **GIF Input** | **Generated GIF (1-bit)**  | **Description, raw & zlib sizes** |
| :-----------: | :------------------------: | ------------------------------------------------------- |
| ![animated_python.gif](examples/animated_python.gif "animated_python.gif")<br>256 colors, 74kB, read [details](#animated_python_details) | ![animated_python-generated.gif](examples/animated_python-generated.gif "animated_python-generated.gif")<br>2 colors | 128x64, 36 frames<br>animated_python.128x64.36img.raw (37kB)<br>animated_python.128x64.36img.z (**3kB**) |
| ![still_mycat.png](examples/still_mycat.png "still_mycat.png")<br>256 colors, 13kB, read [details](#still_mycat_details) | ![still_mycat-generated.gif](examples/still_mycat-generated.gif "still_mycat-generated.gif")<br>2 colors | 128x64, 1 frame<br>still_mycat.128x64.1img.raw (1kB)<br>still_mycat.128x64.1img.z (**0.3kB**) |
| ![video_Big_Buck_Bunny_256colors.gif](examples/video_Big_Buck_Bunny_256colors.gif "video_Big_Buck_Bunny_256colors.gif")<br>256 colors, 1063kB, read [details](#video_big_buck_bunny_details) | ![video_Big_Buck_Bunny_monow-generated.gif](examples/video_Big_Buck_Bunny_monow-generated.gif "video_Big_Buck_Bunny_monow-generated.gif")<br>2 colors | 128x64, 200 frames<br>video_Big_Buck_Bunny_monow.128x64.200img.raw (205kB)<br>video_Big_Buck_Bunny_monow.128x64.200img.z (**47kB**) |


* **Details on the "animated python" animation**<a name="animated_python_details"></a>

This animation has been generated thanks to the [GFTO online animation tool](https://engfto.com/index/create_animated_bouncing_text/0-26) with the following parameters: 
```
        TEXT/FONT: "Python", FreakomixbyAdvo, 28, normal, 0
        COLORS,BACKGROUND: white, black, black
        ANIMATION: 0.8s, 0.1s, 42, -42, 0, 0, 0, 0
        SCREEN: 128x64
```

* **Details on the "my black cat" still picture** <a name="still_mycat_details"></a>

This image has been created with the great [Inkscape](https://inkscape.org), check "still_mycat.svg" for details. The cat photo has been downloaded from https://unsplash.com/photos/EMnLrtASNKE, the author is Gretchen Auer and the License is the [Unsplash License](https://unsplash.com/license).

* **Details on Big Buck Bunny files** <a name="video_big_buck_bunny_details"></a>

The video is the famous [Big Buck Bunny](https://studio.blender.org/films/big-buck-bunny/?asset=263) from [Blender Studio](https://studio.blender.org) under the license [CC-BY](https://creativecommons.org/licenses/by/4.0/).
```bash
# convert video into animated gif in 8-bit per pixel (256colors)
wget https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c0/Big_Buck_Bunny_4K.webm/Big_Buck_Bunny_4K.webm.480p.webm

export input_filename="Big_Buck_Bunny_4K.webm.480p.webm"
export output_filename="Big_Buck_Bunny_256colors.gif"
ffmpeg -ss 318 -t 20 -i ${input_filename} -vf "fps=10,scale=128x64:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 ${output_filename}

# convert video into animated gif in 1-bit per pixel (monow)
export input_filename="Big_Buck_Bunny_4K.webm.480p.webm"
export output_filename="Big_Buck_Bunny_monow.gif"
ffmpeg -ss 318 -t 20 -i ${input_filename} -vf "fps=10,scale=128x64:flags=lanczos,format=monow,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 ${output_filename}
```


## Any questions or comments are welcome :bird:
If you have any comments or questions, feel free to send me an email at coolcornucopia@outlook.com :email:.

--

Peace

coolcornucopia :smile:


