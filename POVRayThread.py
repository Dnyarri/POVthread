#!/usr/bin/env python3

"""POV-Ray Thread: Linen and Stitch - Converting image into textile simulation in POV-Ray format.
--------------------------------------------------------------------------------------------------

Input: PNG, PPM, PGM.

Output: `POV-Ray<https://www.povray.org/>`_.

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

History:
----

0.10.14.0   Initial version of filter host template - 14 Oct 2024. Using png in tempfile preview etc.

1.14.1.1    Preview etc with PyPNM. Image list moved to global to reduce rereading.

1.16.4.24   PNG and PPM support, zoom in and out, numerous fixes.

1.16.9.14   Preview switch source/result added. Zoom on click now mimic Photoshop Ctrl + Click and Alt + Click.

1.16.16.16  Preview switch bugs fixed.

1.16.20.20  Changed GUI to menus.

----
Main site: `The Toad's Slimy Mudhole<https://dnyarri.github.io>`_

Git repository: `POV-Ray Thread at Github<https://github.com/Dnyarri/POVthread>`_; `Gitflic mirror<https://gitflic.ru/project/dnyarri/povthread>`_.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.19.1.7'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from copy import deepcopy
from pathlib import Path
from random import randbytes  # Used for random icon only
from tkinter import Button, Frame, IntVar, Label, Menu, Menubutton, PhotoImage, Spinbox, Tk, filedialog
from tkinter.messagebox import showinfo

from export import linen, stitch
from filter import avgrow
from pypng.pnglpng import png2list
from pypnm.pnmlpnm import list2bin, pnm2list

""" ┌────────────┐
    │ GUI events │
    └────-───────┘ """


def DisMiss(event=None) -> None:
    """Kill dialog and continue"""
    sortir.destroy()


def ShowMenu(event) -> None:
    """Pop menu up (or sort of drop it down)"""
    menu02.post(event.x_root, event.y_root)


def ShowInfo(event=None) -> None:
    """Show image information"""
    showinfo(
        title='Image information',
        message=f'File: {sourcefilename}',
        detail=f'Image: X={X}, Y={Y}, Z={Z}, maxcolors={maxcolors}',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled"""
    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget.config(state='normal')
        if widget.winfo_class() == 'Button':
            widget.config(cursor='hand2')
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])


def UIBusy() -> None:
    """Busy UI state, buttons disabled"""
    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget.config(state='disabled')
        if widget.winfo_class() == 'Button':
            widget.config(cursor='arrow')
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def ShowPreview(preview_name: PhotoImage, caption: str) -> None:
    """Show preview_name PhotoImage with caption below"""
    global zoom_factor, preview

    preview = preview_name

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

    zanyato.config(text=caption, font=('helvetica', 8), image=preview, compound='top', padx=0, pady=0, justify='center', background=zanyato.master['background'], relief='flat', borderwidth=1, state='normal')


def GetSource(event=None) -> None:
    """Opening source image and redefining other controls state"""
    global zoom_factor, view_src, is_filtered, is_saved
    global preview
    global X, Y, Z, maxcolors, image3D, info, sourcefilename
    global source_image3D, preview_src, preview_filtered  # deep copy of source data and copies of preview
    global info_normal

    zoom_factor = 0
    view_src = True
    is_filtered = False
    is_saved = False

    sourcefilename = filedialog.askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('Portable network graphics', '.png'), ('Portable network map', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return

    info_normal = {'txt': f'{Path(sourcefilename).name}', 'fg': 'grey', 'bg': 'grey90'}

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        │  They are used during saving!          │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # Reading image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # Reading image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)
        # Creating dummy info
        info = {}
        # Fixing color mode. The rest is fixed with pnglpng v. 25.01.07.
        if maxcolors > 255:
            info['bitdepth'] = 16
        else:
            info['bitdepth'] = 8

    else:
        raise ValueError('Extension not recognized')

    """ ┌────────────────────────────────────────────┐
        │ Creating deep copy of source 3D list       │
        │ to avoid accumulating repetitive filtering │
        └────────────────────────────────────────────┘ """
    source_image3D = deepcopy(image3D)

    """ ┌─────────────────────────────────────────────────────────────────────────┐
        │ Converting list to bytes of PPM-like structure "preview_data" in memory │
        └────────────────────────────────────────────────────────────────────────-┘ """
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)

    """ ┌────────────────────────────────────────────────┐
        │ Now showing "preview_data" bytes using Tkinter │
        └────────────────────────────────────────────────┘ """
    preview = PhotoImage(data=preview_data)

    """ ┌─────────────────────────────────────────────┐
        │ Creating copy of source preview for further │
        │ switch between source and result            │
        └─────────────────────────────────────────────┘ """
    preview_src = preview_filtered = preview

    ShowPreview(preview, 'Source')

    # binding zoom on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    sortir.bind_all('<Control-i>', ShowInfo)
    menu02.entryconfig('Image Info...', state='normal')
    # binding global
    sortir.bind_all('<Return>', RunFilter)
    # enabling save
    menu02.entryconfig('Export Linen...', state='normal')
    menu02.entryconfig('Export Stitch...', state='normal')

    # enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # updating zoom label display
    label_zoom.config(text='Zoom 1:1')
    # enabling "Filter"
    UINormal()


def RunFilter(event=None) -> None:
    """Filtering image, and previewing"""
    global zoom_factor, view_src, is_filtered
    global preview, preview_filtered
    global X, Y, Z, maxcolors, image3D, info

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
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)
    preview_filtered = PhotoImage(data=preview_data)

    # Flagging as filtered
    is_filtered = True
    view_src = False

    ShowPreview(preview_filtered, 'Result')

    # enabling zoom
    label_zoom.config(state='normal')
    butt_plus.config(state='normal', cursor='hand2')
    # binding switch on preview click
    zanyato.bind('<Button-1>', SwitchView)  # left click


def zoomIn(event=None) -> None:
    """Zooming preview in"""
    global zoom_factor, view_src, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5

    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')

    # reenabling +/- buttons
    butt_minus.config(state='normal', cursor='hand2')
    if zoom_factor == 4:  # max zoom 5
        butt_plus.config(state='disabled', cursor='arrow')
    else:
        butt_plus.config(state='normal', cursor='hand2')


def zoomOut(event=None) -> None:
    """Zooming preview out"""
    global zoom_factor, view_src, preview
    zoom_factor = max(zoom_factor - 1, -4)  # min zoom 1/5

    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')

    # reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    if zoom_factor == -4:  # min zoom 1/5
        butt_minus.config(state='disabled', cursor='arrow')
    else:
        butt_minus.config(state='normal', cursor='hand2')


def zoomWheel(event) -> None:
    """Starting zoomIn or zoomOut by mouse wheel"""
    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


def SwitchView(event=None) -> None:
    """Switching preview between preview_src and preview_filtered"""
    global zoom_factor, view_src, preview
    view_src = not view_src
    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')


def SaveAsLinen() -> None:
    """Once pressed on Linen"""
    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension=('POV-Ray scene file', '.pov'),
    )
    if savefilename == '':
        return

    UIBusy()

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        │ using global maxcolors, image3D                     │
        └─────────────────────────────────────────────────────┘ """

    linen.linen(image3D, maxcolors, savefilename)

    UINormal()


def SaveAsStitch() -> None:
    """Once pressed on Linen"""
    savefilename = filedialog.asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension=('POV-Ray scene file', '.pov'),
    )
    if savefilename == '':
        return

    UIBusy()

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        │ using global maxcolors, image3D                     │
        └─────────────────────────────────────────────────────┘ """

    stitch.stitch(image3D, maxcolors, savefilename)

    UINormal()


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

zoom_factor = 0
view_src = True
is_filtered = False

sortir = Tk()

sortir.iconphoto(True, PhotoImage(data='P6\n2 8\n255\n'.encode(encoding='ascii') + randbytes(2 * 8 * 3)))
sortir.title('POV-Ray Thread')
sortir.geometry('+200+100')

# Info statuses dictionaries
info_normal = {'txt': f'POV-Ray Thread {__version__}', 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

# initial sortir binding, before image load
sortir.bind_all('<Button-3>', ShowMenu)  # Popup menu
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)

frame_top = Frame(sortir, borderwidth=2, relief='groove')
frame_top.pack(side='top', anchor='nw', pady=(0, 2))
frame_preview = Frame(sortir, borderwidth=2, relief='groove')
frame_preview.pack(side='top')

""" ┌──────────────────────┐
    │ Top frame (controls) │
    └─────────────────────-┘ """

# File and menu
butt01 = Menubutton(frame_top, text='File...'.ljust(10, ' '), font=('helvetica', 10), cursor='hand2', justify='left', state='normal', indicatoron=False, relief='raised', borderwidth=2, background='grey90', activebackground='grey98')
butt01.pack(side='left', padx=(0, 10), pady=0, fill='both')

menu02 = Menu(butt01, tearoff=False)  # "File" menu
menu02.add_command(label='Open...', state='normal', command=GetSource, accelerator='Ctrl+O')
menu02.add_separator()
menu02.add_command(label='Export Linen...', state='disabled', command=SaveAsLinen)
menu02.add_command(label='Export Stitch...', state='disabled', command=SaveAsStitch)
menu02.add_separator()
menu02.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu02.add_separator()
menu02.add_command(label='Exit', state='normal', command=DisMiss, accelerator='Ctrl+Q')

butt01.config(menu=menu02)

# Filter section begins
info00 = Label(frame_top, text='Filtering \nThreshold:', font=('helvetica', 8, 'italic'), justify='right', foreground='brown', state='disabled')
info00.pack(side='left', padx=(0, 4), pady=0, fill='both')

# X-pass threshold control
info01 = Label(frame_top, text='X:', font=('helvetica', 10), justify='left', state='disabled')
info01.pack(side='left', padx=0, pady=0, fill='both')

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled', width=3)
spin01.pack(side='left', padx=(0, 4), pady=0, fill='both')

# Y-pass threshold control
info02 = Label(frame_top, text='Y:', font=('helvetica', 10), justify='left', state='disabled')
info02.pack(side='left', padx=0, pady=0, fill='both')

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled', width=3)
spin02.pack(side='left', padx=(0, 4), pady=0, fill='both')

# Filter start
butt02 = Button(frame_top, text='Filter', font=('helvetica', 10), cursor='arrow', justify='center', state='disabled', relief='raised', borderwidth=2, background='grey90', activebackground='grey98', command=RunFilter)
butt02.pack(side='left', padx=0, pady=0, fill='both')

""" ┌──────────────────────────────┐
    │ Center frame (image preview) │
    └─────────────────────────────-┘ """
zanyato = Label(
    frame_preview,
    text='Preview area.\n  Double click to open image,\n  Right click or Alt+F for a menu.\nWith image opened,\n  Ctrl+Click to zoom in,\n  Alt+Click to zoom out,\n  Enter to filter.\nWhen filtered, click to switch\nsource/result.',
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

frame_zoom = Frame(frame_preview, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', justify='center', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

sortir.mainloop()
