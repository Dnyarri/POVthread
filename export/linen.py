#!/usr/bin/env python3

"""
POV Thread textile simulation (based on POV Mosaic)
---

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

Output: `POV-Ray<https://www.povray.org/>`_.

History:
---

2007 - General idea illustration for Kris Zaklika.

1.10.04.01  Initial public release.

1.16.5.23   Modularization.

1.22.01.11  Acceleration, numerous internal changes.

---
Main site: `The Toad's Slimy Mudhole <https://dnyarri.github.io>`_

Git repository: `POV-Ray Thread at Github<https://github.com/Dnyarri/POVthread>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2007-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.22.01.11'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from time import strftime, time


def linen(image3d: list[list[list[int]]], maxcolors: int, resultfilename: str) -> None:
    """POV-Ray Thread export, Linen pattern.

    - `image3d` - image as list of lists of lists of int channel values;
    - `maxcolors` - maximum value of int in `image3d` list, either 255 or 65535;
    - `resultfilename` - name of POV-Ray file to export.

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
                'Description: Mosaic picture simulating textile, linen pattern',
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
                '   #declare rot = 1.5; // Controls rotation/skew degree',
                '   #declare den = 24;  // Controls threads density',
                '   #declare f1 = function(x, y, z) {(den/360) * degrees(atan(z/(x + rot*y)))}; // Angular, skewed by "rot"',
                '   #declare f2 = function(x, y, z) {abs(cos(f1(x, y, z)))}; // Ripples on angular',
                '   #declare f3 = function(x, y, z) {0.5*f_noise_generator(1*x, 200*(y+x), 1*z, 3)}; // Perlin rescaled diagonally',
                '   #declare f4 = function(x, y, z) {f2(x,y,z) * f3(x,y,z)}; // Multiplying base thread and Perlin fibers\n',
                '#declare thingie_normal_2 = normal {function {f4(x,y,z)} slope_map {[0 <-2, 1>] [0.3 <0.5, 0.7>] [1 <1, 0>]}\n  rotate <0, 0, 0>};  // Rotate normal here\n',
                '\n/*  -----------------------\n    |  Thingies facility  |\n    -----------------------  */\n',
                '#declare t_width = 1.25;    // Makes thread wider, coefficient (normally > 1)',  # Thingie element below
                '#declare t_thick = 1;       // Makes whole fabric thicker, coefficient',
                '#declare t_base  = 0.3;     // Base minimal radius, handle with care\n',
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
                '#declare scale_rnd  = 0;    // Rescale thingies according to Perlin noise, see "Distortion functions" below.',
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
                '#declare thething_transform = transform {\n  // You can place your global scale, rotate etc. here\n};',
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
                'light_source{0*x\n  color rgb <1.1, 1.0, 1.0>\n//  area_light <0.5, 0, 0>, <0, 0.5, 0>, 5, 5 circular orient area_illumination on\n  translate <-4, -3, 2>\n}\n',
                'light_source{0*x\n  color rgb <0.9, 1.0, 1.0>\n//  area_light <0.5, 0, 0>, <0, 0.5, 0>, 5, 5 circular orient area_illumination on\n  translate <1, -2, 3>\n}\n',
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

            # Grouping repetitive strings together for easy editing
            normal_string = 'normal{thingie_normal rotate(normal_rotate_rnd * (<rand(rnd_1), rand(rnd_1), rand(rnd_1)> - 0.5)) translate(normal_move_rnd * <rand(rnd_1), rand(rnd_1), rand(rnd_1)>)}'
            scale_string = f'scale(<1, 1, 1> + (scale_rnd * <0, 0, distort_s(scl_pat_x*{scale_xyz * x}, scl_pat_y*{scale_xyz * y}, rand(rnd_1))-0.5>))'
            rotate_string_horz = f'rotate(rotate_rnd * <distort_r1(rot_pat_x*{scale_xyz * x}, rot_pat_y*{scale_xyz * y}, rand(rnd_1))-0.5, 0, 0>)'
            rotate_string_vert = f'rotate(<0, 0, 90> + (rotate_rnd * <distort_r2(rot_pat_x*{scale_xyz * x}, rot_pat_y*{scale_xyz * y}, rand(rnd_1))-0.5, 0, 0>))'
            # checker pattern
            if ((y + 1) % 2) == ((x + 1) % 2):
                resultfile.write(
                    ''.join(
                        [
                            # lower horizontal start from corner 0,0
                            '    object {thingie\n',
                            f'      pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'      finish{{thingie_finish}} {normal_string}\n      {scale_string}\n',
                            f'      {rotate_string_horz}\n',
                            f'      translate<{x}, {y}, 0>\n',
                            '      clipped_by{plane{z,0}}\n',
                            '    }\n',
                            # upper vertical start from corner 0,0
                            '    object {thingie\n',
                            f'      pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'      finish{{thingie_finish}} {normal_string}\n      {scale_string}\n',
                            f'      {rotate_string_vert}\n',
                            f'      translate<{x}, {y}, 0>\n',
                            '      clipped_by{plane{-z,0}}\n',
                            '    }\n',
                        ]
                    )
                )

            # checker pattern switch
            else:
                resultfile.write(
                    ''.join(
                        [
                            # upper horizontal start from row 0 col 1
                            '    object {thingie\n',
                            f'      pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'      finish{{thingie_finish}} {normal_string}\n      {scale_string}\n',
                            f'      {rotate_string_horz}\n',
                            f'      translate<{x}, {y}, 0>\n',
                            '      clipped_by{plane{-z,0}}\n',
                            '    }\n',
                            # lower vertical start from row 0 col 1
                            '    object {thingie\n',
                            f'      pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                            f'      finish{{thingie_finish}} {normal_string}\n      {scale_string}\n',
                            f'      {rotate_string_vert}\n',
                            f'      translate<{x}, {y}, 0>\n',
                            '      clipped_by{plane{z,0}}\n',
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
                '} // thething closed\n',
                '\nobject {thething',  # inserting thething
                '  transform {thething_transform}',
                '}',  # insertion complete
                '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
            ]
        )
    )
    # Closed scene

    # Close output
    resultfile.close()
# ↑ linen finished

# ↓ Dummy stub for standalone execution attempt
if __name__ == '__main__':
    print('Module to be imported, not run as standalone.')
