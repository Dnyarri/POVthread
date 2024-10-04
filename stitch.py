#!/usr/bin/env python3

'''
POV Cross-stitch (based on POV Mosaic)

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)

Input: PNG
Output: POVRay

History:    2007 - General idea illustration for Kris Zaklika.

1.10.04.01  Initial public release

-------------------
Main site:
https://dnyarri.github.io

Github repository:
https://github.com/Dnyarri/POVthread

'''

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2007-2024 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.10.4.1'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from random import random
from time import ctime, time
from tkinter import BOTH, Tk, filedialog
from tkinter.ttk import Progressbar

import png  # PNG reading: PyPNG from: https://gitlab.com/drj11/pypng

# --------------------------------------------------------------
# Creating dialog {#8888ff}
sortir = Tk()
sortir.title('Cross stitch')
sortir.geometry(f'500x16+{(sortir.winfo_screenwidth()-500)//2}+{(sortir.winfo_screenheight()-16)//2}')
sortir.resizable(width=True, height=True)
progressbar = Progressbar(sortir, orient='horizontal', mode='determinate', value=0, maximum=100, length=500)
progressbar.pack(fill=BOTH, expand=True)
sortir.overrideredirect(True)
sortir.withdraw()
# Main dialog created and hidden

# --------------------------------------------------------------
# Open source and export files

# Open source image, first get name {#aa0000}
sourcefilename = filedialog.askopenfilename(
    title='Open source PNG file',
    filetypes=[('PNG', '.png')],
    defaultextension=('PNG', '.png'),
)
if (sourcefilename == '') or (sourcefilename is None):
    sortir.destroy()
    quit()

# open PNG file {#aa0000}
source = png.Reader(filename=sourcefilename)  # starting PyPNG

# Opening image, iDAT comes to 'pixels' generator, to be tuple'd later {#aa0000, 26}
X, Y, pixels, info = source.asRGBA()
Z = info['planes']  # Maximum channel number
imagedata = tuple(pixels)  # Building tuple from generator

if info['bitdepth'] == 8:
    maxcolors = 255  # Maximal value for 8-bit channel
if info['bitdepth'] == 16:
    maxcolors = 65535  # Maximal value for 16-bit channel

if 'gamma' in info:
    gamma_note = f'Source PNG gAMA value is {info['gamma']}'
else:
    gamma_note = 'Source PNG gAMA was absent'

# opening result file, first get name
resultfilename = filedialog.asksaveasfilename(
    title='Save POVRay scene file',
    filetypes=[
        ('POV-Ray scene file', '*.pov'),
        ('All Files', '*.*'),
    ],
    defaultextension=('POV-Ray scene file', '.pov'),
)
if (resultfilename == '') or (resultfilename is None):
    sortir.destroy()
    quit()

# open POV file {#aa0000}
resultfile = open(resultfilename, 'w')

# Both files opened


def src(x, y, z):
    '''
    Analog of src from FM, force repeat edge instead of out of range.
    Returns int channel value z for pixel x, y

    '''
    # Repeat edge extrapolation {#cc0000}
    cx = int(x)
    cy = int(y)
    cx = max(0, cx)
    cx = min((X - 1), cx)
    cy = max(0, cy)
    cy = min((Y - 1), cy)

    # Here is the main magic of turning two x, z into one array position {#cc0000}
    position = (cx * Z) + z
    channelvalue = int((imagedata[cy])[position])

    return channelvalue


# end of src function


def src_lum(x, y):
    '''
    Returns brightness of pixel x, y

    '''

    if info['planes'] < 3:  # supposedly L and LA
        yntensity = src(x, y, 0)
    else:  # supposedly RGB and RGBA
        yntensity = int(0.2989 * src(x, y, 0) + 0.587 * src(x, y, 1) + 0.114 * src(x, y, 2))

    return yntensity


# end of src_lum function

# WRITING POV FILE

seconds = time()
localtime = ctime(seconds)  # will be used for randomization and for debug info


#   POV header start # {#aaaa00}
resultfile.writelines(
    [
        '/*\n',
        'Persistence of Vision Ray Tracer Scene Description File\n',
        'Version: 3.7\n',
        'Description: Mosaic picture simulating cross stitch\n',
        'Author: Automatically generated by stitch program, based on POVRay Mosaic project at\n',
        'https://github.com/Dnyarri/POVmosaic\n',
        'https://gitflic.ru/project/dnyarri/povmosaic\n\n',
        'developed by Ilya Razmanov aka Ilyich the Toad\n',
        'https://dnyarri.github.io\n',
        'mailto:ilyarazmanov@gmail.com\n\n',
        f'Generated by:   {__file__} ver: {__version__} at: {localtime}\n'
        f'Converted from: {sourcefilename}\n'
        f'Source info:    {info}\n'
        '*/\n\n',
    ]
)

#   Globals # {#aaaa00}
resultfile.writelines(
    [
        '\n',
        '#version 3.7;\n\n',
        'global_settings{\n',
        '    max_trace_level 3   // Small to speed up preview. May need to be increased for metals\n',
        '    adc_bailout 0.01    // High to speed up preview. May need to be decreased to 1/256\n',
        f'    assumed_gamma 1.0   // {gamma_note}, that may or may not be of value.\n',
        '    ambient_light <0.5, 0.5, 0.5>\n',
        '    charset utf8\n',
        '}\n\n',
        '#include "finish.inc"\n',
        '#include "metals.inc"\n',
        '#include "golds.inc"\n',
        '#include "glass.inc"\n',
        '#include "functions.inc"\n',
        '\n',
    ]
)
#   POV header end

# Thingie element, then scene # {#aaff88}
resultfile.writelines(
    [
        '\n/*  -----------------\n    |  Surface lab  |\n    -----------------  */\n',
        '\n//       Surface finish variants\n',
        '#declare thingie_finish_1 = finish{phong 0.1 phong_size 1}  // Dull\n',
        '#declare thingie_finish_2 = finish{ambient 0.1 diffuse 0.5 specular 1.0 reflection 0.5 roughness 0.01}  // Shiny\n',
        '\n//       Simple texture normal variants\n',
        '// Constant, normal placeholder\n',
        '#declare thingie_normal_0 = normal {function {1}}\n\n',
        '// Regular threads\n',
        '#declare thingie_normal_1 = normal {function{abs(sin(16*y))} rotate <0, 0, 30>}\n\n',
        '// Perlin noise, elongated\n',
        '#declare thingie_normal_3 = normal {function{f_noise_generator(x, 16*y, z, 3)} rotate <0, 0, 10>}\n\n',
        '// Double wire\n',
        '#declare thingie_normal_4 = normal {function{abs(sin(32*y*y))}}\n\n',
        '/*  --------------------------------\n    |  Complex texture normal lab  |\n    --------------------------------  */\n\n',
        '// Layered texture a-la cotton pearl\n\n',
        '   #declare rot = - 0.6; // Controls rotation/skew degree\n',
        '   #declare den = 24; // Controls threads density\n',
        '   #declare f1 = function(x, y, z) {(den/360) * degrees(atan(z/(x + rot*y)))} // Angular, skewed by "rot"\n',
        '   #declare f2 = function(x, y, z) {abs(cos(f1(x, y, z)))} // Ripples on angular\n',
        '   #declare f3 = function(x, y, z) {0.5*f_noise_generator(1*x, 200*(y+x), 1*z, 3)} // Perlin rescaled diagonally\n',
        '   #declare f4 = function(x, y, z) {f2(x,y,z) - 0.5*f3(x,y,z)} // Adding base thread and Perlin fibers together\n\n',
        '#declare thingie_normal_2 = normal {function {f4(x,y,z)} slope_map {[0 <-6, 1>] [0.3 <0.5, 0.7>] [1 <1, 0>]}\n  rotate <0, 0, 0>}  // Rotate normal here\n\n',
        '\n/*  -----------------------\n    |  Thingies facility  |\n    -----------------------  */\n\n',
        '#declare t_width = 1.0;     // Makes thread wider, coefficient (normally > 1)\n',  # Thingie element below # {#669966, 3}
        '#declare t_thick = 1;       // Makes whole fabric thicker, coefficient\n',
        '#declare t_base  = 0.25;    // Base minimal radius, handle with care\n',
        '#declare t_off   = 2.0 * t_base;  // Internal var, better not handle at all\n\n',
        '// MAIN THINGIE OBJECT\n',
        '#declare thingie = torus {0.5, t_base*t_thick scale <1, t_width, t_thick>}  // MAIN THINGIE\n\n',  # {#009900, 0}
        '#declare thingie_finish = thingie_finish_1\n',
        '#declare thingie_normal = thingie_normal_1\n\n',
        '#declare cm = function(k) {k}   // Color transfer function for all channels, all thingies\n',
        '// #declare cm = function(k) {pow(k,(1/0.5))}   // Example of Gamma = 0.5\n',
        '\n//       Per-thingie normal modifiers\n',
        '#declare normal_move_rnd   = <0, 0, 0>;  // Random move of normal map. No constrains on values\n',
        '#declare normal_rotate_rnd = <0, 0, 0>;  // Random rotate of normal map. Values in degrees\n',
        '\n/*  ---------------------------------------------------------\n    |  Space canvas Distortion lab (avoid being distorted)  |\n    ---------------------------------------------------------  */\n\n',
        '#declare scale_rnd  = <0, 0, 0>;  // Rescale thingies according to Perlin noise, see "Distortion functions" below.\n\n',
        '#declare move_rnd  = <0, 0, 0>;   // Move thingies according to Perlin noise, same pattern as rescale.\n\n',
        '#declare scl_pat_x = 6;     // Perlin patterns per X.\n',
        '#declare scl_pat_y = 6;     // Perlin patterns per Y.\n\n',
        '#declare rotate_rnd = 0;    // Rotate thingies according to Perlin noise. Arbitrary value, normally 0..100\n',
        '#declare rot_pat_x = 6;     // Perlin patterns per X.\n',
        '#declare rot_pat_y = 6;     // Perlin patterns per Y.\n\n',
        '/*  -----------------------------------------------------\n    |  Distortion functions, see help.html for details  |\n    -----------------------------------------------------  */\n\n',
        '#declare distort_s = function(x, y, z) {f_noise_generator(x, y, 0, 3)};     // Scale pattern, currently slice of 3D Perlin noise at z = 0.\n',
        '#declare distort_r1 = function(x, y, z) {f_noise_generator(x, y, 0, 3)};    // Rotation pattern (upper), currently slice of 3D Perlin noise at z = 0.\n',
        '#declare distort_r2 = function(x, y, z) {f_noise_generator(x, y, 0.5, 3)};  // Rotation pattern (lower), currently slice of 3D Perlin noise at z = 0.5 to remove visual match between upper and lower.\n\n',
        '// #declare distort_s = function(x, y, z) {z}; // Regular random example\n',
        '\n/*  --------------------------------------------------\n    |  Some properties for whole thething and scene  |\n    --------------------------------------------------  */\n\n',
        '//       Common transform for the whole thething, placed here just to avoid scrolling\n',
        '#declare thething_transform = transform {\n  // You can place your global scale, rotate etc. here\n}\n',
        '\n//       Seed random\n',
        f'#declare rnd_1 = seed({int(seconds * 1000000)});\n\n',
        'background{color rgbft <0, 0, 0, 1, 1>} // Hey, I''m just trying to be explicit in here!\n\n',
        # Camera # {#aaaa00, 13}
        '\n/*   ---------------------\n    |  Camera and light  |\n    ----------------------\n',
        '  NOTE: Coordinate system match Photoshop,\n  origin is top left, z points to the viewer.\n  Sky vector is important!\n----------------------------------------------  */\n\n',
        '#declare camera_position = <0.0, 0.0, 3.0>;  // Camera position over object, used for view angle\n\n',
        'camera{\n',
        '//  orthographic\n',
        '  location camera_position\n',
        '  right x*image_width/image_height\n',
        '  up y\n',
        '  sky <0, -1, 0>\n',
        f'  direction <0, 0, vlength(camera_position - <0.0, 0.0, {1.0/max(X, Y)}>)>  // May alone work for many pictures. Otherwise fiddle with angle below\n',
        f'  angle 2.0*(degrees(atan2({0.5 * max(X, Y)/X}, vlength(camera_position - <0.0, 0.0, {1.0/max(X, Y)}>)))) // Supposed to fit object, unless thingies are too high\n',
        '  look_at <0.0, 0.0, 0.0>\n',
        '}\n\n',
        # Light {#aaaa00, 2}
        'light_source{0*x\n  color rgb <1.1, 1.0, 1.0>\n//  area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on\n  translate <-4, 1, 3>\n}\n\n',
        'light_source{0*x\n  color rgb <0.9, 1.0, 1.0>\n//  area_light <1, 0, 0>, <0, 1, 0>, 5, 5 circular orient area_illumination on\n  translate <1, -3, 4>\n}\n\n',
        '\n/*  ----------------------------------------------\n    |  Insert preset to override settings above  |\n    ----------------------------------------------  */\n\n',
        '// #include "preset.inc"    // Set path and name of your file related to scene file\n\n',
        # Main object start {#ffaa00,0}
        '\n// Object thething made out of thingies\n',
        '#declare thething = union{\n',
    ]
)

# Now going to cycle through image and build big thething

scale_xyz = 1.0 / max(X, Y)  # Overall thething rescaling to 1:1 box factor

progressbar.config(maximum=Y)

for y in range(0, Y, 1):
    sortir.deiconify()  # {#8888ff, 3}
    progressbar.config(value=y)
    sortir.update()
    sortir.update_idletasks()

    resultfile.write(f'\n  // Row {y}\n')
    for x in range(0, X, 1):
        # Colors normalized to 0..1
        r = float(src(x, y, 0)) / maxcolors
        g = float(src(x, y, 1)) / maxcolors
        b = float(src(x, y, 2)) / maxcolors

        # Something to map something to. By default - brightness, normalized to 0..1
        c = float(src_lum(x, y)) / maxcolors

        # alpha to be used for alpha dithering
        a = float(src(x, y, 3)) / maxcolors
        # a = 0 is transparent, a = 1.0 is opaque
        tobe_or_nottobe = a > random()

        # whether to draw thingie in place of partially transparent pixel or not
        if tobe_or_nottobe:
            # Grouping repetitive strings together for easy editing
            normal_string = 'normal{thingie_normal rotate(normal_rotate_rnd * (<rand(rnd_1), rand(rnd_1), rand(rnd_1)> - 0.5)) translate(normal_move_rnd * <rand(rnd_1), rand(rnd_1), rand(rnd_1)>)}'
            rotate_string_1 = f'(rotate_rnd * <distort_r1(rot_pat_x*{scale_xyz*x}, rot_pat_y*{scale_xyz*y}, rand(rnd_1))-0.5, 0, 0>)'
            rotate_string_2 = f'(rotate_rnd * <distort_r2(rot_pat_x*{scale_xyz*x}, rot_pat_y*{scale_xyz*y}, rand(rnd_1))-0.5, 0, 0>)'
            resultfile.writelines(
                [
                    # Union #  {#ff0000}
                    '    union{\n',
                    # upper +45 deg #  {#ff0000, 7}
                    '      object {thingie\n',
                    f'        pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                    f'        finish{{thingie_finish}} {normal_string}\n'
                    f'        scale(<1, 1, 1+t_off>)\n',
                    f'        rotate(<0, 0, 45.0> + {rotate_string_1})\n',
                    '        clipped_by{plane{-z,0}}\n',
                    '      }\n',
                    # lower -45 deg #  {#0000ff, 7}
                    '      object {thingie\n',
                    f'        pigment{{rgb<cm({r}), cm({g}), cm({b})>}}\n',
                    f'        finish{{thingie_finish}} {normal_string}\n'
                    f'        scale(<1, 1, 1-t_off>)\n',
                    f'        rotate(<0, 0, -45.0> + {rotate_string_2})\n',
                    '        clipped_by{plane{-z,0}}\n',
                    '      }\n',
                    f'     scale (<1, 1, 1> + (scale_rnd * distort_s(scl_pat_x*{scale_xyz*x}, scl_pat_y*{scale_xyz*y}, rand(rnd_1) - 0.5) ) )\n',
                    f'     translate move_rnd * (distort_s(scl_pat_x*{scale_xyz*x}, scl_pat_y*{scale_xyz*y}, rand(rnd_1)) - 0.5)\n',
                    f'     translate <{x}, {y}, 0>\n',
                    '    }\n',
                ]
            )


# Transform object to fit 1, 1, 1 cube at 0, 0, 0 coordinates  # {#aaaa00}
resultfile.writelines(
    [
        '\n  // Object transforms to fit 1, 1, 1 cube at 0, 0, 0 coordinates\n',
        f'  translate <0.5, 0.5, 0> + <{-0.5*X}, {-0.5*Y}, 0>\n',  # centering at scene zero
        f'  scale<{scale_xyz}, {scale_xyz}, {scale_xyz}>\n',  # fitting
        '} // thething closed\n\n'
        '\nobject {thething\n'  # inserting thething
        '  transform {thething_transform}\n',
        '}\n',  # insertion complete
        '\n/*\n\nhappy rendering\n\n  0~0\n (---)\n(.>|<.)\n-------\n\n*/',
    ]
)
# Closed scene

# Close output
resultfile.close()

# Destroying dialog  # {#8888ff}
sortir.destroy()
sortir.mainloop()
