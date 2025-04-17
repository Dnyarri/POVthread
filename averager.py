#!/usr/bin/env python3

"""Adaptive color average image filtering.

Average image colors in a pixel row until difference between averaged and next pixel in row reach threshold. Then repeat the same in column. Thus filter changes smooth image areas to completely flat colored, with detailed edges between them.

Input: PNG, PPM, PGM.

Output: PNG, PPM, PGM.

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

History:
---

0.10.14.0   Initial version of filter host template - 14 Oct 2024. Using png in tempfile preview etc.

1.14.1.1    Preview etc with PyPNM. Image list moved to global to reduce rereading.

1.16.4.24   PNG and PPM support, zoom in and out, numerous fixes.

1.16.9.14   Preview switch source/result added. Zoom on click now mimic Photoshop Ctrl + Click and Alt + Click.

1.16.16.16  Preview switch bugs fixed.

---
Main site: `The Toad's Slimy Mudhole<https://dnyarri.github.io>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.16.16.16'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from copy import deepcopy
from pathlib import Path
from tkinter import Button, Frame, IntVar, Label, PhotoImage, Spinbox, Tk, filedialog
from tkinter.ttk import Separator

from filter import avgrow
from pypng import pnglpng
from pypnm import pnmlpnm

""" ┌────────────┐
    │ GUI events │
    └────-───────┘ """


def DisMiss():
    """Kill dialog and continue"""
    sortir.destroy()


def UINormal():
    """Normal UI state, buttons enabled"""
    for widget in frame_left.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget.config(state='normal')
        if widget.winfo_class() == 'Button':
            widget.config(cursor='hand2')
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])


def UIBusy():
    """Busy UI state, buttons disabled"""
    for widget in frame_left.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget.config(state='disabled')
        if widget.winfo_class() == 'Button':
            widget.config(cursor='arrow')
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def GetSource(event=None):
    """Opening source image and redefining other controls state"""
    global zoom_factor, view_src, preview
    global X, Y, Z, maxcolors, image3D, info
    global source_image3D, preview_src, preview_filtered  # deep copy of source data and copies of preview

    zoom_factor = 0
    view_src = True

    sourcefilename = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('PNG', '.png'), ('PNM', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = pnglpng.png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnmlpnm.pnm2list(sourcefilename)
        # Creating dummy info
        info = {}
        # Fixing color mode. The rest is fixed with pnglpng v. 25.01.07.
        if maxcolors > 255:
            info['bitdepth'] = 16
        else:
            info['bitdepth'] = 8

    else:
        raise ValueError('Extension not recognized')

    # Creating deep copy of source image3D
    source_image3D = deepcopy(image3D)

    """ ┌─────────────────────────────────────────────────────────────────────────┐
        │ Converting list to bytes of PPM-like structure "preview_data" in memory │
        └────────────────────────────────────────────────────────────────────────-┘ """
    preview_data = pnmlpnm.list2bin(image3D, maxcolors, show_chessboard=True)

    """ ┌────────────────────────────────────────────────┐
        │ Now showing "preview_data" bytes using Tkinter │
        └────────────────────────────────────────────────┘ """
    preview = PhotoImage(data=preview_data)
    # Creating copy of source preview for further switch between source and result
    preview_src = preview_filtered = preview

    zanyato.config(text='Source', font=('helvetica', 8), image=preview, compound='top', padx=0, pady=0, state='normal')
    # binding zoom on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    zanyato.bind('<MouseWheel>', zoomWheel)  # Wheel
    # binding global
    sortir.bind_all('<Return>', RunFilter)
    # enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # updating zoom label display
    label_zoom.config(text='Zoom 1:1')
    # enabling "Filter"
    UINormal()


def RunFilter(event=None):
    """Filtering image, and previewing"""
    global zoom_factor, view_src, preview
    global X, Y, Z, maxcolors, image3D, info
    global preview_filtered

    # filtering part
    threshold_x = maxcolors * int(spin01.get()) // 255  # Rescaling for 16-bit
    threshold_y = maxcolors * int(spin02.get()) // 255

    UIBusy()

    """ ┌─────────────────┐
        │ Filtering image │
        └─────────────────┘ """
    image3D = avgrow.filter(source_image3D, threshold_x, threshold_y)

    UINormal()

    # preview result
    preview_data = pnmlpnm.list2bin(image3D, maxcolors, show_chessboard=True)
    preview_filtered = PhotoImage(data=preview_data)

    view_src = False
    preview = preview_filtered
    preview_label = 'Result'

    if zoom_factor >= 0:
        preview = preview.zoom(
            zoom_factor + 1,
        )
        label_zoom.config(text=f'Zoom {zoom_factor + 1}:1')
    else:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom.config(text=f'Zoom 1:{1 - zoom_factor}')

    zanyato.config(text=preview_label, image=preview)

    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')

    # binding global
    sortir.bind_all('<Control-Shift-S>', SaveAs)
    # binding switch on preview click
    zanyato.bind('<Button-1>', SwitchView)  # left click


def zoomIn(event=None):
    global zoom_factor, view_src, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5

    if view_src:
        preview = preview_src
        preview_label = 'Source'
    else:
        preview = preview_filtered
        preview_label = 'Result'

    if zoom_factor >= 0:
        preview = preview.zoom(
            zoom_factor + 1,
        )
        label_zoom.config(text=f'Zoom {zoom_factor + 1}:1')
    else:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom.config(text=f'Zoom 1:{1 - zoom_factor}')

    zanyato.config(text=preview_label, image=preview)

    # reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 4:  # max zoom 5
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut(event=None):
    global zoom_factor, view_src, preview
    zoom_factor = max(zoom_factor - 1, -4)  # min zoom 1/5

    if view_src:
        preview = preview_src
        preview_label = 'Source'
    else:
        preview = preview_filtered
        preview_label = 'Result'

    if zoom_factor >= 0:
        preview = preview.zoom(
            zoom_factor + 1,
        )
        label_zoom.config(text=f'Zoom {zoom_factor + 1}:1')
    else:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom.config(text=f'Zoom 1:{1 - zoom_factor}')

    zanyato.config(text=preview_label, image=preview)

    # reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == -4:  # min zoom 1/5
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


def zoomWheel(event):
    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


def SwitchView(event=None):
    """Switching preview between preview_src and preview_filtered"""
    global zoom_factor, view_src, preview
    view_src = not view_src
    if view_src:
        preview = preview_src
        preview_label = 'Source'
    else:
        preview = preview_filtered
        preview_label = 'Result'

    if zoom_factor >= 0:
        preview = preview.zoom(
            zoom_factor + 1,
        )
        label_zoom.config(text=f'Zoom {zoom_factor + 1}:1')
    else:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom.config(text=f'Zoom 1:{1 - zoom_factor}')

    zanyato.config(text=preview_label, image=preview)


def SaveAs(event=None):
    """Once pressed on Save as..."""

    # Adjusting "Save to" formats to be displayed according to bitdepth
    if Z < 3:
        format = [('PNG', '.png'), ('Portable grey map', '.pgm')]
    else:
        format = [('PNG', '.png'), ('Portable pixel map', '.ppm')]

    # Open export file
    resultfilename = filedialog.asksaveasfilename(
        title='Save image file',
        filetypes=format,
        defaultextension=('PNG file', '.png'),
    )
    if resultfilename == '':
        return None

    UIBusy()

    if Path(resultfilename).suffix == '.png':
        pnglpng.list2png(resultfilename, image3D, info)
    elif Path(resultfilename).suffix in ('.ppm', '.pgm'):
        pnmlpnm.list2pnm(resultfilename, image3D, maxcolors)

    UINormal()


""" ╔══════════╗
    ║ Mainloop ║
    ╚══════════╝ """

zoom_factor = 0

sortir = Tk()

sortir.title('Averager')
sortir.geometry('+200+100')
sortir.minsize(300, 360)

# Main dialog icon is PPM as well!
icon = PhotoImage(data=b'P6\n2 2\n255\n\xff\x00\x00\xff\xff\x00\x00\x00\xff\x00\xff\x00')
sortir.iconphoto(True, icon)

# Info statuses dictionaries
info_normal = {'txt': f'Adaptive Average Filter {__version__}', 'fg': 'grey', 'bg': 'light grey'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 8), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

frame_left = Frame(sortir, borderwidth=2, relief='groove')
frame_left.pack(side='left', anchor='nw')
frame_right = Frame(sortir, borderwidth=2, relief='groove')
frame_right.pack(side='left', anchor='nw')

""" ┌────────────┐
    │ Left frame │
    └───────────-┘ """
# Open image
butt01 = Button(frame_left, text='Open image...'.center(16, ' '), font=('helvetica', 14), cursor='hand2', justify='center', command=GetSource)
butt01.pack(side='top', padx=4, pady=(2, 18), fill='both')

sep01 = Separator(frame_left, orient='horizontal')
sep01.pack(side='top', fill='both')

info00 = Label(frame_left, text='Filtering', font=('helvetica', 12, 'italic'), justify='center', foreground='brown', background='light blue', state='disabled')
info00.pack(side='top', padx=0, pady=(0, 6), fill='both')

# X-pass threshold control
info01 = Label(frame_left, text='Threshold X', font=('helvetica', 10), justify='left', state='disabled')
info01.pack(side='top', padx=4, pady=(0, 2), fill='both')

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled')
spin01.pack(side='top', padx=4, pady=(0, 2), fill='both')

# Y-pass threshold control
info02 = Label(frame_left, text='Threshold Y', font=('helvetica', 10), justify='left', state='disabled')
info02.pack(side='top', padx=4, pady=(0, 2), fill='both')

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_left, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled')
spin02.pack(side='top', padx=4, pady=(0, 2), fill='both')

# Filter start
butt02 = Button(frame_left, text='Filter', font=('helvetica', 14), cursor='arrow', justify='center', state='disabled', command=RunFilter)
butt02.pack(side='top', padx=4, pady=0, fill='both')

sep02 = Separator(frame_left, orient='horizontal')
sep02.pack(side='top', pady=(2, 18), fill='both')

# Save result
butt89 = Button(frame_left, text='Save as...', font=('helvetica', 14), justify='center', state='disabled', command=SaveAs)
butt89.pack(side='top', padx=4, pady=2, fill='both')

# Exit
butt99 = Button(frame_left, text='Exit', font=('helvetica', 14), cursor='hand2', justify='center', command=DisMiss)
butt99.pack(side='bottom', padx=4, pady=(18, 2), fill='both')

""" ┌─────────────┐
    │ Right frame │
    └────────────-┘ """
zanyato = Label(
    frame_right,
    text='Preview area.\n  Double click to open image,\nWith image opened,\n  Ctrl+Click to zoom in,\n  Alt+Click to zoom out,\n  or use mouse wheel.\nWhen filtered, click to switch\nsource/result.',
    font=('helvetica', 12),
    justify='left',
    borderwidth=2,
    padx=24,
    pady=24,
    background='grey90',
    relief='groove',
)
zanyato.bind('<Double-Button-1>', GetSource)
zanyato.pack(side='top')

frame_zoom = Frame(frame_right, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
