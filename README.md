# POVRay Thread - Bitmap to 3D canvas and cross stitch simulation converter

Python utilities for conversion of bitmap image (in PNG format) to some sort of solid objects in [POVRay](https://www.povray.org/) format, resembling threads of canvas or cross stitches. Each source image pixel is converted to a 3D object, colored after source pixel.

![Example of linen export rendering](https://dnyarri.github.io/thread/linen24x512.png)

## Brief programs description  

- **linen** - creates an object, simulating canvas, colored after source image (taffeta, print on canvas, and the like).
- **stitch** - simulates common cross stitching embroidery appearance.

![Example of cross-stitch export rendering](https://dnyarri.github.io/thread/stitch24x512.png)

*Dependencies:* Tkinter, [PyPNG](https://gitlab.com/drj11/pypng)

*Usage:* programs are equipped with minimal GUI for file selection. Exported scene contains enough basic stuff (globals, light, camera) to be rendered out of the box, and is well structured and commented for further editing.

[Project website](https://dnyarri.github.io/)