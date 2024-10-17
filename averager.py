#!/usr/bin/env python3

'''
Adaptive color averager.

Averages colors in RGB PNG within linear or squarish areas between contrast edges. Released as accessory for POV Thread project to provide color reduction somewhat similar to used in real cross stitch.

Created by: Ilya Razmanov (mailto:ilyarazmanov@gmail.com)
            aka Ilyich the Toad (mailto:amphisoft@gmail.com)

History:

24.10.14.0  Initial version of filter template.
24.10.17.2  GUI for "Averager" v. 24.10.15.1 finished.
24.10.17.3  Linked all includes to standalone version for distribution.

'''

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '24.10.17.3'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from tkinter import Tk, Button, Frame, IntVar, Label, PhotoImage, Spinbox, filedialog
import tempfile
import shutil

import png  # PNG I/O: PyPNG from: https://gitlab.com/drj11/pypng

# ╔══════════╗
# ║ PNG part ║
# ╚══════════╝

def png2list(in_filename):
    '''
    Take PNG filename and return PNG data in a suitable form.

    Usage:
    -------

    ``image3D, X, Y, Z, maxcolors, info = png2list(in_filename)``

    Takes PNG filename ``in_filename`` and returns the following tuple:

    ``image3D`` - Y*X*Z list (image) of lists (rows) of lists (pixels) of ints (channels), from PNG iDAT.

    ``X, Y, Z`` - int, PNG image sizes.

    ``maxcolors`` - int, value maximum per channel, either 255 or 65535, for 8 bpc and 16 bpc PNG respectively.

    ``info`` - dictionary, chunks like resolution etc. as they are accessible by PyPNG.
    '''

    source = png.Reader(in_filename)

    X, Y, pixels, info = source.asDirect()  # Opening image, iDAT comes to "pixels" as bytearray
    Z = info['planes']  # Channels number
    if info['bitdepth'] == 8:
        maxcolors = 255  # Maximal value for 8-bit channel
    if info['bitdepth'] == 16:
        maxcolors = 65535  # Maximal value for 16-bit channel

    imagedata = tuple(pixels)  # Creates tuple of bytes or whatever "pixels" generator returns

    # Next part forcedly creates 3D list of int out of "imagedata" tuple of hell knows what
    image3D = [[[int(((imagedata[y])[(x * Z) + z])) for z in range(Z)] for x in range(X)] for y in range(Y)]
    # List (image) of lists (rows) of lists (pixels) of ints (channels) created

    return (X, Y, Z, maxcolors, image3D, info)


# --------------------------------------------------------------


def list2png(out_filename, image3D, info):
    '''
    Take filename and image data in a suitable form, and create PNG file.

    Usage:
    -------

    ``list2png(out_filename, image3D, info)``

    Takes data described below and writes PNG file ``out_filename`` out of it:

    ``image3D`` - Y*X*Z list (image) of lists (rows) of lists (pixels) of ints (channels)

    ``info`` - dictionary, chunks like resolution etc. as you want them to be present in PNG
    '''

    # Determining list sizes
    Y = len(image3D)
    X = len(image3D[0])
    Z = len(image3D[0][0])

    # Overwriting "info" properties with ones determined from the list
    info['size'] = (X, Y)
    info['planes'] = Z

    # flattening 3D list to 1D list for PNG .write_array method
    image1D = [c for row in image3D for px in row for c in px]

    # Writing PNG
    resultPNG = open(out_filename, mode='wb')
    writer = png.Writer(X, Y, **info)
    writer.write_array(resultPNG, image1D)
    resultPNG.close()  # Close output

    return None


def create_image(X, Y, Z):
    '''Create empty 3D list of X, Y, Z sizes'''

    new_image = [[[0 for z in range(Z)] for x in range(X)] for y in range(Y)]

    return new_image


# ╔════════════════╗
# ║ Filtering part ║
# ╚════════════════╝

def filter(sourcefilename, resultfilename, threshold_x, threshold_y):
    '''Take name of source PNG, open PNG, filter adoptive average 24.10.15.1, save resulting PNG with a given name'''

    # Reading source image as 3D list
    X, Y, Z, maxcolors, sourceimage, info = png2list(sourcefilename)
    # Image ready

    # Creating empty intermediate image
    medimage = create_image(X, Y, 3)

    # Creating empty final image
    resultimage = create_image(X, Y, 3)

    for y in range(0, Y, 1):
        r_sum, g_sum, b_sum = r, g, b = sourceimage[0][0][0:3]
        x_start = 0
        number = 1
        for x in range(0, X, 1):
            r, g, b = sourceimage[y][x][0:3]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_x) or (abs(g - (g_sum / number)) > threshold_x) or (abs(b - (b_sum / number)) > threshold_x) or x == X:
                for i in range(x_start, x, 1):
                    medimage[y][i] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                medimage[y][x] = [r, g, b]
                x_start = x
                number = 1
                r_sum, g_sum, b_sum = r, g, b
            else:
                medimage[y][x] = [r, g, b]

    for x in range(0, X, 1):
        r_sum, g_sum, b_sum = r, g, b = medimage[0][0]
        y_start = 0
        number = 1
        for y in range(0, Y, 1):
            r, g, b = medimage[y][x]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_y) or (abs(g - (g_sum / number)) > threshold_y) or (abs(b - (b_sum / number)) > threshold_y) or x == X:
                for i in range(y_start, y, 1):
                    resultimage[i][x] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                resultimage[y][x] = [r, g, b]
                y_start = y
                number = 1
                r_sum, g_sum, b_sum = r, g, b
            else:
                resultimage[y][x] = [r, g, b]

    # Explicitly skipping alpha and setting compression
    info['alpha'] = False
    info['compression'] = 9

    # Writing PNG file
    list2png(resultfilename, resultimage, info)
    # Export file written and closed

    return None


# ╔══════════╗
# ║ GUI part ║
# ╚══════════╝

temp_dir_itself = tempfile.TemporaryDirectory()  # Filesystem object
temp_dir_name = temp_dir_itself.name  # Name of filesystem object above


def DisMiss():  # Kill dialog and continue
    sortir.destroy()


def GetSource():  # Opening source image and redefining other controls state
    global zoom_factor
    zoom_factor = 1
    global sourcefilename
    global resultfilename
    global preview
    sourcefilename = filedialog.askopenfilename(title='Open PNG file to filter', filetypes=[('PNG', '.png')])
    if sourcefilename == '':
        sortir.destroy()
        quit()
    # preview part
    preview = PhotoImage(file=sourcefilename)
    preview = preview.zoom(zoom_factor, zoom_factor)  # "zoom" zooms in, "subsample" zooms out
    zanyato.config(text='Source', image=preview, compound='top')
    # filtered image address
    resultfilename = f'{str(temp_dir_name)}/huj.png'
    # enabling "Threshold" spins and their labels
    spin01.config(state='normal')
    spin02.config(state='normal')
    info01.config(state='normal')
    info02.config(state='normal')
    # enabling "Filter" button
    butt02.config(state='normal')
    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')


def RunFilter():  # Filtering image, saving as temporary file, and previewing temporary file
    # filtering part
    threshold_x = int(spin01.get())
    threshold_y = int(spin02.get())
    filter(sourcefilename, resultfilename, threshold_x, threshold_y)
    # preview result
    global preview
    preview = PhotoImage(file=resultfilename)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(text='Result', image=preview, compound='top')
    # enabling "Save as..." button
    butt03.config(state='normal')


def SaveAs():  # "Save as..." function - simply copies temporary file above to user-selected location
    global savefilename
    savefilename = filedialog.asksaveasfilename(
        title='Save filtered image',
        filetypes=[('PNG', '.png')],
        defaultextension=('PNG file', '.png'),
    )
    if savefilename == '':
        sortir.destroy()
        quit()
    shutil.copy(resultfilename, savefilename)


def zoomIn():
    global zoom_factor
    zoom_factor = min(zoom_factor + 1, 3)
    global preview
    preview = PhotoImage(file=sourcefilename)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(text='Source', image=preview, compound='top')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_minus.config(state='normal')
    if zoom_factor == 3:
        butt_plus.config(state='disabled')
    else:
        butt_plus.config(state='normal')


def zoomOut():
    global zoom_factor
    zoom_factor = max(zoom_factor - 1, 1)
    global preview
    preview = PhotoImage(file=sourcefilename)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(text='Source', image=preview, compound='top')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_plus.config(state='normal')
    if zoom_factor == 1:
        butt_minus.config(state='disabled')
    else:
        butt_minus.config(state='normal')


# ╔═════════════════════════════╗
# ║ Packing all this up finally ║
# ╚═════════════════════════════╝

sortir = Tk()

zoom_factor = 1

sortir.title(f'Averager {__version__}')
sortir.geometry('+200+100')
sortir.minsize(250, 310)

frame_left = Frame(sortir, borderwidth=2, relief='groove')
frame_left.pack(side='left', anchor='nw')
frame_right = Frame(sortir, borderwidth=2, relief='groove')
frame_right.pack(side='left', anchor='nw')

butt01 = Button(frame_left, text='Open PNG...', font=('arial', 16), cursor='hand2', justify='center', command=GetSource)
butt01.pack(side='top', padx=4, pady=2, fill='both')

info01 = Label(frame_left, text='Threshold X', font=('arial', 10), justify='left', state='disabled')
info01.pack(side='top', padx=4, pady=[10, 2], fill='both')

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled')
spin01.pack(side='top', padx=4, pady=[0, 2], fill='both')

info02 = Label(frame_left, text='Threshold Y', font=('arial', 10), justify='left', state='disabled')
info02.pack(side='top', padx=4, pady=[0, 2], fill='both')

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled')
spin02.pack(side='top', padx=4, pady=[0, 2], fill='both')

butt02 = Button(frame_left, text='Filter', font=('arial', 16), cursor='hand2', justify='center', state='disabled', command=RunFilter)
butt02.pack(side='top', padx=4, pady=2, fill='both')

butt03 = Button(frame_left, text='Save as...', font=('arial', 16), cursor='hand2', justify='center', state='disabled', command=SaveAs)
butt03.pack(side='top', padx=4, pady=[10, 2], fill='both')

butt99 = Button(frame_left, text='Exit', font=('arial', 16), cursor='hand2', justify='center', command=DisMiss)
butt99.pack(side='bottom', padx=4, pady=[10, 2], fill='both')

zanyato = Label(frame_right, text='Preview area', font=('arial', 10), justify='center', borderwidth=2, relief='groove')
zanyato.pack(side='top')

frame_zoom = Frame(frame_right, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='hand2', justify='center', state='disabled', command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='hand2', justify='center', state='disabled', command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text=f'Zoom {zoom_factor}:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
