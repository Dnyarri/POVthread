# POV-Ray Thread - Bitmap to 3D canvas and cross stitch simulation converter

Python program for conversion of bitmap image (in PNG or PPM format) to some sort of solid objects in [POVRay](https://www.povray.org/) 3D format, resembling threads of canvas or cross stitches. Each source image pixel is converted to a 3D object, colored after source pixel.

[![Example of linen export rendering](https://dnyarri.github.io/thread/linen24x512.png "Example of linen export rendering")](https://dnyarri.github.io/povthread.html)

## Main program GUI

Main program [**POVRayThread.py**](https://github.com/Dnyarri/POVthread/blob/main/POVRayThread.py) provides general linking between PNG and PPM/PGM reading modules and POV-Ray writing one.

Useful GUI features include mouse event handling:

- After starting program *double click* on preview area is equal to "Open...", right click to "File..." menu;
- After opening an image *Ctrl + Left click* is *"zoom in"*, *Alt + Left click* is *"zoom out"*, similar to Photoshop;
- After filtering an image (pressing "Enter") left click is source\result preview switch.

## Brief effects module description  

- **Linen.py** - creates an object, simulating canvas, colored after source image (taffeta, print on canvas, and the like).
- **Stitch.py** - simulates common cross stitching embroidery appearance.

[![Example of cross-stitch export rendering](https://dnyarri.github.io/thread/stitch24x512.png "Example of cross-stitch export rendering")](https://dnyarri.github.io/povthread.html)

## Prerequisite and Dependencies

1. [Python](https://www.python.org/) 3.10 or above.
2. [PyPNG](https://gitlab.com/drj11/pypng). Copy included into current POV-Ray Thread distribution.
3. [PyPNM](https://pypi.org/project/PyPNM/). Copy included into current POV-Ray Thread distribution.
4. Tkinter. Normally included into standard CPython distribution.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box. Program is equipped with minimal GUI, so all you have to do after starting a program is use "Open..." dialog to open image file, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with POV-Ray and render the scene.

## Averager

[**Averager.py**](https://github.com/Dnyarri/POVthread/blob/main/Averager.py) was initially created as an accessory for preprocessing source PNG files. It averages image colors (L, LA, RGB, RGBA) within linear or squarish areas between contrast edges, providing color reduction somewhat similar to used in real cross stitch where single thread is used to produce several stitches in a row.

Later this filtering module was added to *POVRayThread*, making *Averager* redundant; however, it is still included into distribution as an illustration of 100% pure Python image filtering program, working at quite acceptable speed without any large third-party C packages.

[![Adaptive Image Averager program GUI](https://dnyarri.github.io/thread/ave.png "Adaptive Image Averager program GUI")](https://dnyarri.github.io/povthread.html#averager)

### Related

[Dnyarri website - other Python freeware](https://dnyarri.github.io) by the same author.

[POV-Ray Thread page with illustrations](https://dnyarri.github.io/povthread.html), explanations etc.

[POV-Ray Thread source at github](https://github.com/Dnyarri/POVthread)

[POV-Ray Thread source at gitflic mirror](https://gitflic.ru/project/dnyarri/povthread)
