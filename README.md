# POV-Ray Thread - Bitmap to 3D canvas and cross stitch simulation converter

Python program for conversion of bitmap image to some sort of solid objects in [POVRay](https://www.povray.org/) 3D format, resembling threads of canvas or cross stitches. Each source image pixel is converted to a 3D object, colored after source pixel.

[![Example of linen export rendering](https://dnyarri.github.io/thread/linen24x512.png "Example of linen export rendering")](https://dnyarri.github.io/povthread.html)

## Main program GUI

Main program **POVRayThread.py** provides general linking between PNG and PPM/PGM reading modules and POV-Ray writing one.

Useful GUI features include mouse event handling:

- After starting program any click on preview area is equal to "Open image";
- After opening an image left-click is *"zoom in"*, right-click is *"zoom out"*;
- After filtering an image left click is source\result preview switch, *Ctrl + Left click* is *"zoom in"*, *Alt + Left click* is *"zoom out"*, similar to Photoshop.

## Brief effects module description  

- **Linen.py** - creates an object, simulating canvas, colored after source image (taffeta, print on canvas, and the like).
- **Stitch.py** - simulates common cross stitching embroidery appearance.

[![Example of cross-stitch export rendering](https://dnyarri.github.io/thread/stitch24x512.png "Example of cross-stitch export rendering")](https://dnyarri.github.io/povthread.html)

## Dependencies

1. [PyPNG](https://gitlab.com/drj11/pypng). Copy included into current POV-Ray Thread distribution.
2. [PyPNM](https://pypi.org/project/PyPNM/). Copy included into current POV-Ray Thread distribution.
3. Tkinter. Included into standard CPython distribution.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box. Program is equipped with minimal GUI, so all you have to do after starting a program is use "Open..." dialog to open image file, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with POV-Ray and render the scene.

## Averager

**Averager.py** was initially created as an accessory for preprocessing source PNG files. It averages colors in RGB PNG or PPM within linear or squarish areas between contrast edges, providing color reduction somewhat similar to used in real cross stitch.

Later this filtering module was added to *POVRayThread*, making *Averager* redundant; however, it is still included into distribution as an illustration of 100% pure Python image filtering program, working at quite acceptable speed without any large third-party C packages.

[![Adaptive Image Averager program GUI](https://dnyarri.github.io/thread/ave.png "Adaptive Image Averager program GUI")](https://dnyarri.github.io/povthread.html#averager)

### Related

[Dnyarri website - other Python freeware](https://dnyarri.github.io) by the same author.

[POV-Ray Thread page with illustrations](https://dnyarri.github.io/povthread.html), explanations etc.

[POV-Ray Thread source at github](https://github.com/Dnyarri/POVthread)

[POV-Ray Thread source at gitflic mirror](https://gitflic.ru/project/dnyarri/povthread)
