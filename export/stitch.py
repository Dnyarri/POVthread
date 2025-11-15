#!/usr/bin/env python3

"""
======================
POV-Ray Thread: Stitch
======================
--------------------------------------------------------------
Converting image to cross stitch simulation in POV-Ray format.
--------------------------------------------------------------

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_
aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Overview
--------

**stitch** export module present function for converting images
and image-like nested lists to an assembly of 3D objects,
colored after source pixels, and forming a simulation of cross stitches.

Objects may be displaced when rendering, based on POV-Ray internal
Perlin noise, simulating base canvas deformation.

Usage
-----

::

    stitch.stitch(image3D, maxcolors, savefilename)

where:

- ``image3d``: image as list of lists of lists of int channel values;
- ``maxcolors``: maximum of channel value in ``image3d`` list (int),
255 for 8 bit and 65535 for 16 bit input;
- ``savefilename``: name of POV-Ray file to export (str).

----
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

`POV-Ray Thread`_ previews and description

.. _POV-Ray Thread: https://dnyarri.github.io/povthread.html

POV-Ray Thread Git repositories: `@Github`_, `@Gitflic`_

.. _@Github: https://github.com/Dnyarri/POVthread

.. _@Gitflic: https://gitflic.ru/project/dnyarri/povthread

"""

# History:
# --------
# ca. 2007 AD   General idea illustration for Kris Zaklika.
# 1.10.4.1      Initial public release of Python version.
# 1.16.6.2      Modularization.
# 1.22.1.11     Acceleration, numerous internal changes.

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2007-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.23.13.13'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from random import random
from time import strftime, time


def stitch(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str) -> None:
    """POV-Ray Thread export, Cross stitch pattern.

        .. function:: stitch(image3d, maxcolors, resultfilename)
        :param image3d: image as list of lists of lists of int channel values;
        :type image3d: list[list[list[int]]
        :param int maxcolors: maximum of channel value in ``image3d`` list (int),
    255 for 8 bit and 65535 for 16 bit input;
        :param str resultfilename: name of POV file to export.

    """

    Y = len(image3d)
    X = len(image3d[0])
    Z = len(image3d[0][0])

    """ ╔═══════════════╗
        ║ src functions ║
        ╚═══════════════╝ """

    def src(x: int | float, y: int | float, z: int) -> int:
        """Analog of src from FilterMeister, force repeat edge instead of out of range.
        Returns int channel value z for pixel x, y."""

        cx = min((X - 1), max(0, int(x)))
        cy = min((Y - 1), max(0, int(y)))

        channelvalue = image3d[cy][cx][z]

        return channelvalue

    """ ╔══════════════════╗
        ║ Writing POV file ║
        ╚══════════════════╝ """

    resultfile = open(resultfilename, 'w')

    """ ┌────────────┐
        │ POV header │
        └────────────┘ """
    resultfile.write(
        '\n'.join(
            [
                '/*',
                'Persistence of Vision Ray Tracer Scene Description File',
                'Version: 3.7',
                'Description: Mosaic picture simulating cross stitch',
                f'Source image properties: Width {X} px, Height {Y} px, Colors per channel: {maxcolors + 1}',
                f'File created automatically at {strftime("%d %b %Y %H:%M:%S")}\nby {f"{__name__}".rpartition(".")[2]} ver. {__version__}',
                '   developed by Ilya Razmanov aka Ilyich the Toad',
                '       https://dnyarri.github.io',
                '       mailto:ilyarazmanov@gmail.com\n*/\n\n',
            ]
        )
    )

    """ ┌──────────────────────┐
        │ Globals and includes │
        └──────────────────────┘ """
    resultfile.write(
        '\n'.join(
            [
                '#version 3.7;\n',
                'global_settings{',
                '    max_trace_level 3   // Small to speed up preview. May need to be increased for metals',
                '    adc_bailout 0.01    // High to speed up preview. May need to be decreased to 1/256',
                '    assumed_gamma 1.0',
                '    ambient_light <0.5, 0.5, 0.5>',
                '    charset utf8',
                '}\n',
                '#include "functions.inc"\n',
            ]
        )
    )
    #   POV header end

    """ ┌─────────────────────┐
        │ Thingie, then scene │
        └─────────────────────┘ """
    resultfile.write(
        '\n'.join(
            [
                '\n/*  -----------------\n    |  Surface lab  |\n    -----------------  */',
                '\n//       Surface finish variants',
                '#declare thingie_finish_1 = finish{phong 0.1 phong_size 1};  // Dull',
                '#declare thingie_finish_2 = finish{ambient 0.1 diffuse 0.5 specular 1.0 reflection 0.5 roughness 0.01};  // Shiny',
                '\n//       Simple texture normal variants',
                '// Constant, normal placeholder',
                '#declare thingie_normal_0 = normal {function {1}};\n',
                '// Regular threads',
                '#declare thingie_normal_1 = normal {function{abs(sin(16*y))} rotate <0, 0, 30>};\n',
                '// Perlin noise, elongated',
                '#declare thingie_normal_3 = normal {function{f_noise_generator(x, 16*y, z, 3)} rotate <0, 0, 10>};\n',
                '// Double wire',
                '#declare thingie_normal_4 = normal {function{abs(sin(32*y*y))}};\n',
                '/*  --------------------------------\n    |  Complex texture normal lab  |\n    --------------------------------  */\n',
                '// Layered texture a-la cotton pearl\n',
                '   #declare rot = - 0.6; // Controls rotation/skew degree',
                '   #declare den = 24; // Controls threads density',
                '   #declare f1 = function(x, y, z) {(den/360) * degrees(atan(z/(x + rot*y)))}; // Angular, skewed by "rot"',
                '   #declare f2 = function(x, y, z) {abs(cos(f1(x, y, z)))}; // Ripples on angular',
                '   #declare f3 = function(x, y, z) {0.5*f_noise_generator(1*x, 200*(y+x), 1*z, 3)}; // Perlin rescaled diagonally',
                '   #declare f4 = function(x, y, z) {f2(x,y,z) - 0.5*f3(x,y,z)}; // Adding base thread and Perlin fibers together\n',
                '#declare thingie_normal_2 = normal {function {f4(x,y,z)} slope_map {[0 <-6, 1>] [0.3 <0.5, 0.7>] [1 <1, 0>]}\n  rotate <0, 0, 0>};  // Rotate normal here\n',
                '\n/*  -----------------------\n    |  Thingies facility  |\n    -----------------------  */\n',
                '#declare t_width = 1.0;     // Makes thread wider, coefficient (normally > 1)',  # Thingie element below
                '#declare t_thick = 1;       // Makes whole fabric thicker, coefficient',
                '#declare t_base  = 0.25;    // Base minimal radius, handle with care',
                '#declare t_off   = 2.0 * t_base;  // Internal var, better not handle at all\n',
                '// MAIN THINGIE OBJECT',
                '#declare thingie = torus {0.5, t_base*t_thick scale <1, t_width, t_thick>};  // MAIN THINGIE\n',
                '#declare thingie_finish = thingie_finish_1;',
                '#declare thingie_normal = thingie_normal_1;\n',
                '#declare cm = function(k) {k};   // Color transfer function for all channels, all thingies',
                '// #declare cm = function(k) {pow(k,(1/0.5))};   // Example of Gamma = 0.5',
                '\n//       Per-thingie normal modifiers',
                '#declare normal_move_rnd   = <0, 0, 0>;  // Random move of normal map. No constrains on values',
                '#declare normal_rotate_rnd = <0, 0, 0>;  // Random rotate of normal map. Values in degrees',
                '\n/*  ---------------------------------------------------------\n    |  Space canvas Distortion lab (avoid being distorted)  |\n    ---------------------------------------------------------  */\n',
                '#declare scale_rnd  = <0, 0, 0>;  // Rescale thingies according to Perlin noise, see "Distortion functions" below.\n',
                '#declare move_rnd  = <0, 0, 0>;   // Move thingies according to Perlin noise, same pattern as rescale.\n',
                '#declare scl_pat_x = 6;     // Perlin patterns per X.',
                '#declare scl_pat_y = 6;     // Perlin patterns per Y.\n',
                '#declare rotate_rnd = 0;    // Rotate thingies according to Perlin noise. Arbitrary value, normally 0..100',
                '#declare rot_pat_x = 6;     // Perlin patterns per X.',
                '#declare rot_pat_y = 6;     // Perlin patterns per Y.\n',
                '/*  -----------------------------------------------------\n    |  Distortion functions, see help.html for details  |\n    -----------------------------------------------------  */\n',
                '#declare distort_s = function(x, y, z) {f_noise_generator(x, y, 0, 3)};     // Scale pattern, currently slice of 3D Perlin noise at z = 0.',
                '#declare distort_r1 = function(x, y, z) {f_noise_generator(x, y, 0, 3)};    // Rotation pattern (upper), currently slice of 3D Perlin noise at z = 0.',
                '#declare distort_r2 = function(x, y, z) {f_noise_generator(x, y, 0.5, 3)};  // Rotation pattern (lower), currently slice of 3D Perlin noise at z = 0.5 to remove visual match between upper and lower.\n',
                '// #declare distort_s = function(x, y, z) {z}; // Regular random example',
                '\n/*  --------------------------------------------------\n    |  Some properties for whole thething and scene  |\n    --------------------------------------------------  */\n',
                '//       Common transform for the whole thething, placed here just to avoid scrolling',
                '#declare thething_transform = transform {\n  // You can place your global scale, rotate etc. here\n}',
                '\n//       Seed random',
                f'#declare rnd_1 = seed({int(time() * 1000000)});\n',
                'background{color rgbft <0, 0, 0, 1, 1>} // Hey, I am just trying to be explicit in here!\n\n',
                '/*  -----------------------------------------\n    |  Source image width and height.       |\n    |  Necessary for further calculations.  |\n    -----------------------------------------  */\n',
                f'#declare X = {X};  // Source image width, px',
                f'#declare Y = {Y};  // Source image height, px\n',
                # Camera
                '\n/*   ---------------------\n    |  Camera and light  |\n    ----------------------',
                '  NOTE: Coordinate system match Photoshop,\n  origin is top left, z points to the viewer.\n  Sky vector is important!\n----------------------------------------------  */\n',
                '#declare camera_position = <0.0, 0.0, 3.0>;  // Camera position over object, used for view angle\n',
                'camera{',
                '//  orthographic',
                '  location camera_position',
                '  right x*image_width/image_height',
                '  up y',
                '  sky <0, -1, 0>',
                '  direction <0, 0, vlength(camera_position - <0.0, 0.0, 1.0 / max(X, Y)>)>  // May alone work for many pictures. Otherwise fiddle with angle below',
                '  angle 2.0*(degrees(atan2(0.5 * image_width * max(X/image_width, Y/image_height) / max(X, Y), vlength(camera_position - <0.0, 0.0, 1.0 / max(X, Y)>)))) // Supposed to fit object',
                '  look_at <0.0, 0.0, 0.0>',
                '}\n',
                # Light
                'light_source{0*x\n  color rgb <1.1, 1.0, 1.0>\n//  area_light <0.5, 0, 0>, <0, 0.5, 0>, 5, 5 circular orient area_illumination on\n  translate <-4, 1, 3>\n}\n',
                'light_source{0*x\n  color rgb <0.9, 1.0, 1.0>\n//  area_light <0.5, 0, 0>, <0, 0.5, 0>, 5, 5 circular orient area_illumination on\n  translate <1, -3, 4>\n}\n',
                '\n/*  ----------------------------------------------\n    |  Insert preset to override settings above  |\n    ----------------------------------------------  */\n',
                '// #include "preset.inc"    // Set path and name of your file related to scene file\n',
                # Main object start
                '\n// Object thething made out of thingies\n',
                '#declare thething = union{\n',
            ]
        )
    )

    """ ┌─────────────────────────────────────────────────┐
        │ Cycling through image and building big thething │
        └─────────────────────────────────────────────────┘ """

    scale_xyz = 1.0 / max(X, Y)  # Overall thething rescaling to 1:1 box factor

    for y in range(0, Y, 1):
        resultfile.write(f'\n  // Row {y}\n')
        for x in range(0, X, 1):
            # Colors normalized to 0..1
            if Z > 2:
                r = float(src(x, y, 0)) / maxcolors
                g = float(src(x, y, 1)) / maxcolors
                b = float(src(x, y, 2)) / maxcolors
            else:
                r = g = b = float(src(x, y, 0)) / maxcolors

            # alpha to be used for alpha dithering
            if Z == 4 or Z == 2:
                a = 1.02 * (float(src(x, y, Z - 1)) / maxcolors) - 0.01  # Slightly extending +/- 1%
                tobe_or_nottobe = a >= random()
                # a = 0 is transparent, a = 1.0 is opaque
            else:
                tobe_or_nottobe = True

            # whether to draw thingie in place of partially transparent pixel or not
            if tobe_or_nottobe:
                # Grouping repetitive strings together for easy editing
                normal_string = 'normal{thingie_normal rotate(normal_rotate_rnd * (<rand(rnd_1), rand(rnd_1), rand(rnd_1)> - 0.5)) translate(normal_move_rnd * <rand(rnd_1), rand(rnd_1), rand(rnd_1)>)}'
                rotate_string_1 = f'(rotate_rnd * <distort_r1(rot_pat_x*{scale_xyz * x}, rot_pat_y*{scale_xyz * y}, rand(rnd_1))-0.5, 0, 0>)'
                rotate_string_2 = f'(rotate_rnd * <distort_r2(rot_pat_x*{scale_xyz * x}, rot_pat_y*{scale_xyz * y}, rand(rnd_1))-0.5, 0, 0>)'
                resultfile.write(
                    ''.join(
                        [
                            # Union
                            '    union{\n',
                            # upper +45 deg
                            '      object {thingie\n',
                            f'        pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'        finish{{thingie_finish}} {normal_string}\n        scale(<1, 1, 1+t_off>)\n',
                            f'        rotate(<0, 0, 45.0> + {rotate_string_1})\n',
                            '        clipped_by{plane{-z,0}}\n',
                            '      }\n',
                            # lower -45 deg
                            '      object {thingie\n',
                            f'        pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'        finish{{thingie_finish}} {normal_string}\n        scale(<1, 1, 1-t_off>)\n',
                            f'        rotate(<0, 0, -45.0> + {rotate_string_2})\n',
                            '        clipped_by{plane{-z,0}}\n',
                            '      }\n',
                            f'     scale (<1, 1, 1> + (scale_rnd * distort_s(scl_pat_x*{scale_xyz * x}, scl_pat_y*{scale_xyz * y}, rand(rnd_1) - 0.5) ) )\n',
                            f'     translate move_rnd * (distort_s(scl_pat_x*{scale_xyz * x}, scl_pat_y*{scale_xyz * y}, rand(rnd_1)) - 0.5)\n',
                            f'     translate <{x}, {y}, 0>\n',
                            '    }\n',
                        ]
                    )
                )

    # Transform object to fit 1, 1, 1 cube at 0, 0, 0 coordinates
    resultfile.write(
        '\n'.join(
            [
                '\n  // Object transforms to fit 1, 1, 1 cube at 0, 0, 0 coordinates',
                '  translate <0.5, 0.5, 0> + <-0.5 * X, -0.5 * Y, 0>',  # centering at scene zero
                '  scale<1.0 / max(X, Y), 1.0 / max(X, Y), 1.0 / max(X, Y)>',  # fitting
                '} // thething closed\n\n'
                '\nobject {thething\n'  # inserting thething
                '  transform {thething_transform}',
                '}',  # insertion complete
                '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
            ]
        )
    )
    # Closed scene

    # Close output
    resultfile.close()


# ↑ stitch finished

# ↓ Dummy stub for standalone execution attempt
if __name__ == '__main__':
    print('Module to be imported, not run as standalone.')
