#!/usr/bin/env python3

"""Adaptive color average.

Average image colors in a pixel row until difference between averaged and next pixel in row reach threshold. Then repeat the same in column. Thus filter changes smooth image areas to completely flat colored, with detailed edges between them.

Standalone version for https://dnyarri.github.io/povthread.html

Preview part based on https://dnyarri.github.io/pypnm.html

History:

24.10.14.0  Initial version of filter template.
24.12.09.1  Finished rebuilding for standalone filter+GUI complex, with in-RAM PPM-based preview.
24.12.09.3  Fix for RGBA and fix for 16-bit.
24.12.30.1  Fix for L, fix for export.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '24.12.30.1'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Development'

import array
from tkinter import Button, Frame, IntVar, Label, PhotoImage, Spinbox, Tk, filedialog

import png  # PNG I/O: PyPNG from: https://gitlab.com/drj11/pypng

""" ┌─────────────────────────────┐
    │ Image editing defined first │
    └────-────────────────────────┘ """


def create_image(X: int, Y: int, Z: int) -> list[list[list[int]]]:
    """Create empty 3D nested list of X*Y*Z sizes"""

    new_image = [[[0 for z in range(Z)] for x in range(X)] for y in range(Y)]

    return new_image


def png2list(in_filename: str) -> tuple[int, int, int, int, list[list[list[int]]], dict]:
    """Take PNG filename and return PNG data in a human-friendly form."""

    source = png.Reader(in_filename)

    X, Y, pixels, info = source.asDirect()  # Opening image, iDAT comes to "pixels" as bytearray
    Z = info['planes']  # Channels number
    if info['bitdepth'] == 8:
        maxcolors = 255  # Maximal value for 8-bit channel
    if info['bitdepth'] == 16:
        maxcolors = 65535  # Maximal value for 16-bit channel

    imagedata = tuple(pixels)  # Creates tuple of bytes or whatever "pixels" generator returns

    # Next part forcedly creates 3D list of int out of "imagedata" tuple of hell knows what
    image3D = [[[int((imagedata[y])[(x * Z) + z]) for z in range(Z)] for x in range(X)] for y in range(Y)]
    # List (image) of lists (rows) of lists (pixels) of ints (channels) created

    return (X, Y, Z, maxcolors, image3D, info)


def list2png(out_filename: str, image3D: list[list[list[int]]], info: dict) -> None:
    """Take filename and image data in a suitable form, and create PNG file."""

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


def list2bin(in_list_3d: list[list[list[int]]], maxcolors: int) -> bytes:
    """Convert PNG to PGM P5 or PPM P6 (binary) data structure in memory."""

    # Determining list sizes
    Y = len(in_list_3d)
    X = len(in_list_3d[0])
    Z = len(in_list_3d[0][0])

    # Flattening 3D list to 1D list
    in_list_1d = [c for row in in_list_3d for px in row for c in px]

    if Z == 1:  # L image
        magic = 'P5'

    if Z == 2:  # LA image
        magic = 'P5'
        del in_list_1d[1::2]  # Deleting A channel

    if Z == 3:  # RGB image
        magic = 'P6'

    if Z == 4:  # RGBA image
        magic = 'P6'
        del in_list_1d[3::4]  # Deleting A channel

    if maxcolors < 256:
        datatype = 'B'
    else:
        datatype = 'H'

    header = array.array('B', f'{magic}\n{X} {Y}\n{maxcolors}\n'.encode())
    content = array.array(datatype, in_list_1d)

    content.byteswap()  # Critical!

    pnm = header.tobytes() + content.tobytes()

    return pnm  # End of "list2bin" list to PNM conversion function


def filter(sourceimage: list[list[list[int]]], threshold_x: int, threshold_y: int) -> list[list[list[int]]]:
    """Average image pixels in a row until borderline threshold met, then repeat in a column.

    Be careful: it works with RGB, so RGBA need to be fixed when saving!"""

    # Determining list sizes
    Y = len(sourceimage)
    X = len(sourceimage[0])
    Z = len(sourceimage[0][0])

    # Creating empty intermediate image
    medimage = create_image(X, Y, 3)

    # Creating empty final image
    resultimage = create_image(X, Y, 3)

    for y in range(0, Y, 1):
        if Z > 2:
            r_sum, g_sum, b_sum = r, g, b = sourceimage[0][0][0:3]
        else:
            channel = sourceimage[0][0][0]
            r_sum, g_sum, b_sum = r, g, b = channel, channel, channel
        x_start = 0
        number = 1
        for x in range(0, X, 1):

            if Z > 2:
                r, g, b = sourceimage[y][x][0:3]
            else:
                channel = sourceimage[y][x][0]
                r, g, b = channel, channel, channel

            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_x) or (abs(g - (g_sum / number)) > threshold_x) or (abs(b - (b_sum / number)) > threshold_x) or x == X:
                for i in range(x_start, x - 1, 1):
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
                for i in range(y_start, y - 1, 1):
                    resultimage[i][x] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                resultimage[y][x] = [r, g, b]
                y_start = y
                number = 1
                r_sum, g_sum, b_sum = r, g, b
            else:
                resultimage[y][x] = [r, g, b]

    return resultimage


""" ┌────────────┐
    │ GUI events │
    └────-───────┘ """


def DisMiss():
    """Kill dialog and continue"""

    sortir.destroy()


def GetSource():
    """Opening source image and redefining other controls state"""

    global zoom_factor, sourcefilename, preview, preview_data

    zoom_factor = 1

    sourcefilename = filedialog.askopenfilename(title='Open image file to filter', filetypes=[('PNG', '.png')])
    if sourcefilename == '':
        return

    X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    preview_data = list2bin(image3D, maxcolors)
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)  # "zoom" zooms in, "subsample" zooms out
    zanyato.config(text='Source', image=preview, compound='top')
    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # enabling "Save as..."
    butt89.config(state='normal', cursor='hand2')
    # enabling "Threshold" spins and their labels
    spin01.config(state='normal')
    spin02.config(state='normal')
    info01.config(state='normal')
    info02.config(state='normal')
    # enabling "Filter" button
    butt02.config(state='normal', cursor='hand2')
    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')


def RunFilter():
    """Filtering image, and previewing"""

    X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    # filtering part
    threshold_x = maxcolors * int(spin01.get()) / 255  # Rescaling for 16-bit
    threshold_y = maxcolors * int(spin02.get()) / 255

    result3D = filter(image3D, threshold_x, threshold_y)

    # preview result
    global preview, preview_data
    preview_data = list2bin(result3D, maxcolors)
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)  # "zoom" zooms in, "subsample" zooms out
    zanyato.config(text='Result', image=preview, compound='top')
    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # enabling "Save as..."
    butt89.config(state='normal', cursor='hand2')


def SaveAs():
    """Once pressed on Save as"""

    X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    # filtering part
    threshold_x = maxcolors * int(spin01.get()) / 255  # Rescaling for 16-bit
    threshold_y = maxcolors * int(spin02.get()) / 255

    result3D = filter(image3D, threshold_x, threshold_y)

    # Open "Save as..." file
    savefilename = filedialog.asksaveasfilename(
        title='Save filtered image',
        filetypes=[('PNG', '.png')],
        defaultextension=('PNG file', '.png'),
    )
    if savefilename == '':
        return

    # Forcing RGB on export
    info['greyscale'] = False
    info['planes'] = 3
    info['alpha'] = False

    list2png(savefilename, result3D, info)


def zoomIn():
    global zoom_factor, preview
    zoom_factor = min(zoom_factor + 1, 3)  # max zoom 3
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(image=preview)
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 3:  # max zoom 3
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut():
    global zoom_factor, preview
    zoom_factor = max(zoom_factor - 1, 1)  # min zoom 1
    preview = PhotoImage(data=preview_data)
    preview = preview.zoom(zoom_factor, zoom_factor)
    zanyato.config(image=preview)
    # updating zoom factor display
    label_zoom.config(text=f'Zoom {zoom_factor}:1')
    # reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == 1:  # min zoom 1
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


""" ╔══════════╗
    ║ Mainloop ║
    ╚══════════╝ """

sortir = Tk()

zoom_factor = 1

sortir.title('Averager')
sortir.geometry('+200+100')
sortir.minsize(300, 110)

# Main dialog icon is PPM as well!
icon = PhotoImage(data=b'P6\n2 2\n255\n\xff\x00\x00\xff\xff\x00\x00\x00\xff\x00\xff\x00')
sortir.iconphoto(True, icon)

frame_left = Frame(sortir, borderwidth=2, relief='groove')
frame_left.pack(side='left', anchor='nw')
frame_right = Frame(sortir, borderwidth=2, relief='groove')
frame_right.pack(side='left', anchor='nw')

""" ┌────────────┐
    │ Left frame │
    └───────────-┘ """
# Open image
butt01 = Button(frame_left, text='Open...', font=('arial', 16), cursor='hand2', justify='center', command=GetSource)
butt01.pack(side='top', padx=4, pady=[2, 12], fill='both')

# X control
info01 = Label(frame_left, text='Threshold X', font=('arial', 10), justify='left', state='disabled')
info01.pack(side='top', padx=4, pady=[10, 2], fill='both')

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled')
spin01.pack(side='top', padx=4, pady=[0, 2], fill='both')

# Y control
info02 = Label(frame_left, text='Threshold Y', font=('arial', 10), justify='left', state='disabled')
info02.pack(side='top', padx=4, pady=[0, 2], fill='both')

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled')
spin02.pack(side='top', padx=4, pady=[0, 2], fill='both')

# Filter start
butt02 = Button(frame_left, text='Filter', font=('arial', 16), cursor='arrow', justify='center', state='disabled', command=RunFilter)
butt02.pack(side='top', padx=4, pady=[0, 24], fill='both')

# Save result
butt89 = Button(frame_left, text='Save as...', font=('arial', 16), cursor='arrow', justify='center', state='disabled', command=SaveAs)
butt89.pack(side='top', padx=4, pady=2, fill='both')

# Exit
butt99 = Button(frame_left, text='Exit', font=('arial', 16), cursor='hand2', justify='center', command=DisMiss)
butt99.pack(side='bottom', padx=4, pady=2, fill='both')

""" ┌─────────────┐
    │ Right frame │
    └────────────-┘ """
zanyato = Label(frame_right, text='Preview area', font=('arial', 10), justify='center', borderwidth=2, relief='groove')
zanyato.pack(side='top')

frame_zoom = Frame(frame_right, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text=f'Zoom {zoom_factor}:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
