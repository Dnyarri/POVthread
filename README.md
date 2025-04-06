# POVRay Thread - Bitmap to 3D canvas and cross stitch simulation converter

Python program for conversion of bitmap image to some sort of solid objects in [POVRay](https://www.povray.org/) 3D format, resembling threads of canvas or cross stitches. Each source image pixel is converted to a 3D object, colored after source pixel.

[![Example of linen export rendering](https://dnyarri.github.io/thread/linen24x512.png)](https://dnyarri.github.io/povthread.html)

## Brief effects description  

- **Linen** - creates an object, simulating canvas, colored after source image (taffeta, print on canvas, and the like).
- **Stitch** - simulates common cross stitching embroidery appearance.

[![Example of cross-stitch export rendering](https://dnyarri.github.io/thread/stitch24x512.png)](https://dnyarri.github.io/povthread.html)


## Dependencies

1. [PyPNG](https://gitlab.com/drj11/pypng). Copy included into current img2mesh distribution.
2. [PyPNM](https://pypi.org/project/PyPNM/). Copy included into current img2mesh distribution.
3. Tkinter. Included into standard CPython distribution.

## Installation and Usage

Programs distribution is rather self-contained and is supposed to run right out of the box. Program is equipped with minimal GUI, so all you have to do after starting a program is use "Open..." dialog to open image file, then use "Export..." to name 3D file to be created, then wait while program does the job, then open resulting file with POV-Ray and render the scene.

## Averager

Averager was initially created as an accessory for preprocessing source PNG files. Averages colors in RGB PNG within linear or squarish areas between contrast edges, providing color reduction somewhat similar to used in real cross stitch.

Later this filtering module was added to *POVRayThread*, making *Averager* redundant; however, it is still included into distribution as an illustration of 100% pure Python image filtering program.

### References

[Dnyarri projects website](https://dnyarri.github.io/) - other Python freeware made by the same author.

[POVRay mosaic](https://dnyarri.github.io/povzaika.html) - parent project.
