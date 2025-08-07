#!/usr/bin/env python3

"""Adaptive color average image filtering.
-------------------------------------------

Average image colors in a pixel row until difference between averaged and next pixel in row reach threshold. Then repeat the same in column. Thus filter changes smooth image areas to completely flat colored, with detailed edges between them.

Input: PNG, PPM, PGM.

Output: PNG, PPM.

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

History:
----

0.10.14.0   Initial version of filter host template - 14 Oct 2024. Using png in tempfile preview etc.

1.14.1.1    Preview etc with PyPNM. Image list moved to global to reduce rereading.

1.16.4.24   PNG and PPM support, zoom in and out, numerous fixes.

1.16.9.14   Preview switch source/result added. Zoom on click now mimic Photoshop Ctrl + Click and Alt + Click.

2.16.20.20  Changed GUI to menus.

3.20.6.8    Changed GUI to grid to fit all new features. More detailed image info; image edited/saved status displayed as "*" a-la Photoshop.

----
Main site: `The Toad's Slimy Mudhole<https://dnyarri.github.io>`_

Git: `Dnyarri at Github<https://github.com/Dnyarri>`_; `Gitflic mirror<https://gitflic.ru/user/dnyarri>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.20.7.14'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from copy import deepcopy
from pathlib import Path
from random import randbytes  # Used for random icon only
from time import ctime  # Used to show file info only
from tkinter import BooleanVar, Button, Checkbutton, Frame, IntVar, Label, Menu, Menubutton, PhotoImage, Spinbox, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

from pypng.pnglpng import list2png, png2list
from pypnm.pnmlpnm import list2bin, list2pnm, pnm2list

from filter import avgrow

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
    file_size = Path(sourcefilename).stat().st_size
    file_size_str = f'{file_size / 1024:.2f} Kb' if (file_size > 1024) else f'{file_size} bytes'
    modification_str = ctime(Path(sourcefilename).stat().st_mtime)
    channels_str = f'{Z} channel' if Z == 1 else f'{Z} channels'
    showinfo(
        title='Image information',
        message=f'File properties:\nLocation: {sourcefilename}\nSize: {file_size_str}\nLast modified: {modification_str}',
        detail=f'Image properties, as internally represented by program:\nWidth: {X} px\nHeight: {Y} px\nChannels: {channels_str}\nColor depth: {maxcolors + 1} gradations/channel',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled"""
    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox', 'Checkbutton'):
            widget['state'] = 'normal'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'hand2'
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    if Z == 1 or Z == 3:
        check02['state'] = 'disabled'


def UIBusy() -> None:
    """Busy UI state, buttons disabled"""
    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox', 'Checkbutton'):
            widget['state'] = 'disabled'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'arrow'
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
        label_zoom['text'] = f'Zoom {zoom_factor + 1}:1'
    else:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom['text'] = f'Zoom 1:{1 - zoom_factor}'

    zanyato.config(text=caption, font=('helvetica', 8), image=preview, compound='top', padx=0, pady=0, justify='center', background=zanyato.master['background'], relief='flat', borderwidth=1, state='normal')


def GetSource(event=None) -> None:
    """Opening source image and redefining other controls state"""
    global zoom_factor, view_src, is_filtered, is_saved, info_normal
    global preview
    global X, Y, Z, maxcolors, image3D, info, sourcefilename
    global source_image3D, preview_src, preview_filtered  # deep copy of source data and copies of preview

    zoom_factor = 0
    view_src = True
    is_filtered = is_saved = False

    sourcefilename = askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm'), ('Portable network graphics', '.png'), ('Portable network map', '.ppm .pgm .pbm')])
    if sourcefilename == '':
        return

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        │  They are used during saving!          │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm'):
        # ↓ Reading image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)
        # ↓ Creating dummy info needed for possible resaving as PNG later
        info = {}
        # ↓ Fixing color mode. The rest is fixed with pnglpng v. 25.01.07.
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

    # ↓ binding zoom on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel scroll
    sortir.bind_all('<Control-i>', ShowInfo)
    menu02.entryconfig('Image Info...', state='normal')
    # ↓ binding global
    sortir.bind_all('<Return>', RunFilter)
    # ↓ enabling save
    menu02.entryconfig('Save as...', state='normal')

    # ↓ enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # ↓ updating zoom label display
    label_zoom['text'] = 'Zoom 1:1'
    # ↓ Adding filename to window title a-la Photoshop
    sortir.title(f'Averager: {Path(sourcefilename).name}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    # ↓ enabling "Filter"
    UINormal()


def RunFilter(event=None) -> None:
    """Filtering image, and previewing"""
    global zoom_factor, view_src, is_filtered, is_saved, info_normal
    global preview, preview_filtered
    global X, Y, Z, maxcolors, image3D, info

    # ↓ filtering part
    threshold_x = maxcolors * ini_threshold_x.get() // 255  # Rescaling for 16-bit
    threshold_y = maxcolors * ini_threshold_y.get() // 255
    wraparound = ini_wraparound.get()
    keep_alpha = ini_keep_alpha.get()

    UIBusy()

    """ ┌─────────────────┐
        │ Filtering image │
        └─────────────────┘ """
    image3D = avgrow.filter(source_image3D, threshold_x, threshold_y, wraparound, keep_alpha)

    # ↓ preview result
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)
    preview_filtered = PhotoImage(data=preview_data)

    # ↓ Flagging as filtered, not saved
    is_filtered = True
    is_saved = False
    view_src = False

    ShowPreview(preview_filtered, 'Result')

    # ↓ enabling save
    menu02.entryconfig('Save', state='normal')
    menu02.entryconfig('Save as...', state='normal')
    # ↓ enabling zoom
    label_zoom['state'] = 'normal'
    butt_plus.config(state='normal', cursor='hand2')
    # ↓ binding global
    sortir.bind_all('<Control-Shift-S>', SaveAs)
    sortir.bind_all('<Control-s>', Save)
    # ↓ binding switch on preview click
    zanyato.bind('<Button-1>', SwitchView)  # left click
    # ↓ Adding filename to window title a-la Photoshop
    sortir.title(f'Averager: {Path(sourcefilename).name}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    UINormal()


def zoomIn(event=None) -> None:
    """Zooming preview in"""
    global zoom_factor, view_src, preview
    zoom_factor = min(zoom_factor + 1, 4)  # max zoom 5

    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')

    # ↓ reenabling +/- buttons
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

    # ↓ reenabling +/- buttons
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


def Save(event=None) -> None:
    """Once pressed on Save"""
    global is_filtered, is_saved, info_normal

    if is_saved:  # block repetitive saving
        return
    if not is_filtered:  # block useless source resaving
        return
    resultfilename = sourcefilename
    UIBusy()
    # ↓ Save format choice
    if Path(resultfilename).suffix == '.png':  # Explicitly setting compression
        info['compression'] = 9
        list2png(resultfilename, image3D, info)
    elif Path(resultfilename).suffix in ('.ppm', '.pgm'):
        list2pnm(resultfilename, image3D, maxcolors)
    # ↓ Flagging image as saved, not filtered
    is_saved = True  # to block future repetitive saving
    is_filtered = False
    menu02.entryconfig('Save', state='disabled')
    # ↓ Adding filename to window title a-la Photoshop
    sortir.title(f'Averager: {Path(sourcefilename).name}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    UINormal()


def SaveAs(event=None) -> None:
    """Once pressed on Save as..."""
    global sourcefilename, is_saved, is_filtered, info_normal

    # ↓ Adjusting "Save to" formats to be displayed according to bitdepth
    if Z < 3:
        format = [('Portable network graphics', '.png'), ('Portable grey map', '.pgm')]
    else:
        format = [('Portable network graphics', '.png'), ('Portable pixel map', '.ppm')]

    # ↓ Open export file
    resultfilename = asksaveasfilename(
        title='Save image file',
        filetypes=format,
        defaultextension=('PNG file', '.png'),
    )
    if resultfilename == '':
        return None
    UIBusy()
    # ↓ Save format choice
    if Path(resultfilename).suffix == '.png':
        info['compression'] = 9  # Explicitly setting compression
        list2png(resultfilename, image3D, info)
    elif Path(resultfilename).suffix in ('.ppm', '.pgm'):
        list2pnm(resultfilename, image3D, maxcolors)
    sourcefilename = resultfilename
    # ↓ Flagging image as saved, not filtered, and disabling "Save"
    is_saved = True  # to block future repetitive saving
    is_filtered = False
    menu02.entryconfig('Save', state='disabled')
    # ↓ Adding filename to window title a-la Photoshop
    sortir.title(f'Averager: {Path(sourcefilename).name}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    UINormal()


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

zoom_factor = 0
view_src = True
is_filtered = False

sortir = Tk()

sortir.iconphoto(True, PhotoImage(data='P6\n2 8\n255\n'.encode(encoding='ascii') + randbytes(2 * 8 * 3)))
sortir.title('Averager')
sortir.geometry('+200+100')
sortir.minsize(360, 100)

# ↓ Info statuses dictionaries
info_normal = {'txt': f'Adaptive Average {__version__}', 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

# ↓ initial sortir binding, before image load
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

# ↓ File menu
butt01 = Menubutton(frame_top, text='File...'.ljust(10, ' '), font=('helvetica', 12), cursor='hand2', justify='left', state='normal', indicatoron=False, relief='raised', borderwidth=2, background='grey90', activebackground='grey98')
butt01.grid(row=0, column=0, rowspan=2, sticky='ns', padx=(0, 10), pady=0)

menu02 = Menu(butt01, tearoff=False)  # "File" menu
menu02.add_command(label='Open...', state='normal', command=GetSource, accelerator='Ctrl+O')
menu02.add_separator()
menu02.add_command(label='Save', state='disabled', command=Save, accelerator='Ctrl+S')
menu02.add_command(label='Save as...', state='disabled', command=SaveAs, accelerator='Ctrl+Shift+S')
menu02.add_separator()
menu02.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu02.add_separator()
menu02.add_command(label='Exit', state='normal', command=DisMiss, accelerator='Ctrl+Q')

butt01['menu'] = menu02

# ↓ Filter section begins
info00 = Label(frame_top, text='Filtering threshold:', font=('helvetica', 8, 'italic'), justify='right', foreground='brown', state='disabled')
info00.grid(row=0, column=1)

# ↓ X-pass threshold control
info01 = Label(frame_top, text='X:', font=('helvetica', 11), justify='left', state='disabled')
info01.grid(row=0, column=2)

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled', width=3, font=('helvetica', 11))
spin01.grid(row=0, column=3)

# ↓ Y-pass threshold control
info02 = Label(frame_top, text='Y:', font=('helvetica', 11), justify='left', state='disabled')
info02.grid(row=0, column=4)

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled', width=3, font=('helvetica', 11))
spin02.grid(row=0, column=5)

# ↓ Wrap around control
ini_wraparound = BooleanVar(value=False)
check01 = Checkbutton(frame_top, text='Wrap around', font=('helvetica', 9), justify='left', variable=ini_wraparound, onvalue=True, offvalue=False, state='disabled')
check01.grid(row=1, column=1, sticky='ws')

# ↓ Keep alpha control
ini_keep_alpha = BooleanVar(value=False)
check02 = Checkbutton(frame_top, text='Keep alpha', font=('helvetica', 9), justify='left', variable=ini_keep_alpha, onvalue=True, offvalue=False, state='disabled')
check02.grid(row=1, column=3, columnspan=3, sticky='ws')

# ↓ Filter start
butt02 = Button(frame_top, text='Filter'.center(10, ' '), font=('helvetica', 12), cursor='arrow', justify='center', state='disabled', relief='raised', borderwidth=2, background='grey90', activebackground='grey98', command=RunFilter)
butt02.grid(row=0, column=6, rowspan=2, sticky='nsew', padx=(10, 0), pady=0)

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
