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

1.20.20.1   Numerous minor GUI improvements and code cleanup.

----
Main site: `The Toad's Slimy Mudhole<https://dnyarri.github.io>`_

Git repository: `POV-Ray Thread at Github<https://github.com/Dnyarri/POVthread>`_; `Gitflic mirror<https://gitflic.ru/project/dnyarri/povthread>`_.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.21.17.17'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from copy import deepcopy
from pathlib import Path
from random import randbytes  # Used for random icon only
from time import ctime  # Used to show file info only
from tkinter import Button, Frame, IntVar, Label, Menu, Menubutton, PhotoImage, Spinbox, Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

from pypng.pnglpng import png2list
from pypnm.pnmlpnm import list2bin, pnm2list

from export import linen, stitch
from filter import avgrow

""" ╔══════════════════════════════════╗
    ║ GUI events and functions thereof ║
    ╚══════════════════════════════════╝ """


def DisMiss(event=None) -> None:
    """Kill dialog and continue"""

    sortir.destroy()


def ShowMenu(event) -> None:
    """Pop menu up (or sort of drop it down)"""

    menu02.post(event.x_root, event.y_root)


def ShowInfo(event=None) -> None:
    """Show image information"""

    file_size = Path(sourcefilename).stat().st_size
    file_size_str = f'{file_size / 1048576:.2f} Mb' if (file_size > 1048576) else f'{file_size / 1024:.2f} Kb' if (file_size > 1024) else f'{file_size} bytes'
    showinfo(
        title='Image information',
        message=f'File properties:\nLocation: {sourcefilename}\nSize: {file_size_str}\nLast modified: {ctime(Path(sourcefilename).stat().st_mtime)}',
        detail=f'Image properties, as represented internally:\nWidth: {X} px\nHeight: {Y} px\nChannels: {Z} channel{"s" if Z > 1 else ""}\nColor depth: {maxcolors + 1} gradations/channel',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled"""

    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget['state'] = 'normal'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'hand2'
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    sortir.update()


def UIBusy() -> None:
    """Busy UI state, buttons disabled"""

    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox'):
            widget['state'] = 'disabled'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'arrow'
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def ShowPreview(preview_name: PhotoImage, caption: str) -> None:
    """Show preview_name PhotoImage with caption below"""

    global zoom_factor, preview

    preview = preview_name

    if zoom_factor > 0:
        preview = preview.zoom(
            zoom_factor + 1,
        )
        label_zoom['text'] = f'Zoom {zoom_factor + 1}:1'
    elif zoom_factor < 0:
        preview = preview.subsample(
            1 - zoom_factor,
        )
        label_zoom['text'] = f'Zoom 1:{1 - zoom_factor}'
    else:
        preview = preview_name
        label_zoom['text'] = 'Zoom 1:1'

    zanyato.config(text=caption, font=('helvetica', 8), image=preview, compound='top', padx=0, pady=0, justify='center', background=zanyato.master['background'], relief='flat', borderwidth=1, state='normal')


def GetSource(event=None) -> None:
    """Open source image and redefine other controls state"""

    global zoom_factor, view_src, is_filtered, is_saved, info_normal
    global preview, preview_src, preview_filtered  # preview and copies of preview
    global X, Y, Z, maxcolors, image3D, info, sourcefilename
    global source_image3D  # deep copy of source data

    zoom_factor = 0
    view_src = True
    is_filtered = is_saved = False

    sourcefilename = askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm .pnm'), ('Portable network graphics', '.png'), ('Portable any map', '.ppm .pgm .pbm .pnm')])
    if sourcefilename == '':
        return

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │  NOTE: maxcolors, image3D are GLOBALS! │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix == '.png':
        # ↓ Reading PNG image as list
        X, Y, Z, maxcolors, image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix in ('.ppm', '.pgm', '.pbm', '.pnm'):
        # ↓ Reading PNM image as list
        X, Y, Z, maxcolors, image3D = pnm2list(sourcefilename)

    else:
        raise ValueError('Extension not recognized')

    """ ┌────────────────────────────────────────────┐
        │ Creating deep copy of source 3D list       │
        │ to avoid accumulating repetitive filtering │
        └────────────────────────────────────────────┘ """
    source_image3D = deepcopy(image3D)

    """ ┌───────────────┐
        │ Viewing image │
        └───────────────┘ """
    # ↓ Converting list to bytes of PPM-like structure "preview_data" in memory
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)
    # ↓ Now generating preview from "preview_data" bytes using Tkinter
    preview = PhotoImage(data=preview_data)
    # ↓ Finally the show part
    ShowPreview(preview, 'Source')

    """ ┌─────────────────────────────────────────────┐
        │ Creating copy of source preview for further │
        │ switch between source and result            │
        └─────────────────────────────────────────────┘ """
    preview_src = preview_filtered = preview

    # ↓ binding on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel
    sortir.bind_all('<Control-i>', ShowInfo)
    menu02.entryconfig('Image Info...', state='normal')
    # ↓ binding global
    sortir.bind_all('<Return>', RunFilter)
    # ↓ enabling save
    menu02.entryconfig('Export Linen...', state='normal')
    menu02.entryconfig('Export Stitch...', state='normal')

    # ↓ enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # ↓ updating zoom label display
    label_zoom['text'] = 'Zoom 1:1'
    # ↓ Adding filename to window title a-la Photoshop
    sortir.title(f'POV-Ray Thread: {Path(sourcefilename).name}')
    info_normal = {'txt': f'{Path(sourcefilename).name} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    # ↓ enabling "Filter"
    butt_filter.bind('<Enter>', lambda event=None: butt_filter.config(foreground=butt['activeforeground'], background=butt['activebackground']))
    butt_filter.bind('<Leave>', lambda event=None: butt_filter.config(foreground=butt['foreground'], background=butt['background']))
    UINormal()
    sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+{(sortir.winfo_screenheight() - sortir.winfo_height()) // 2 - 32}')
    butt_filter.focus_set()  # moving focus to "Filter"


def RunFilter(event=None) -> None:
    """Filter image, then preview result"""

    global zoom_factor, view_src, is_filtered
    global preview, preview_filtered
    global X, Y, Z, maxcolors, image3D, info

    # ↓ filtering part
    threshold_x = maxcolors * int(spin01.get()) // 255  # Rescaling for 16-bit
    threshold_y = maxcolors * int(spin02.get()) // 255

    UIBusy()

    """ ┌─────────────────┐
        │ Filtering image │
        └─────────────────┘ """
    image3D = avgrow.filter(source_image3D, threshold_x, threshold_y, wrap_around=False, keep_alpha=True)

    # ↓ preview result
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)
    preview_filtered = PhotoImage(data=preview_data)

    # ↓ Flagging as filtered
    is_filtered = True
    view_src = False

    ShowPreview(preview_filtered, 'Result')

    # ↓ enabling zoom
    label_zoom['state'] = 'normal'
    butt_plus.config(state='normal', cursor='hand2')
    # ↓ binding switch on preview click
    zanyato.bind('<Button-1>', SwitchView)  # left click
    zanyato.bind('<space>', SwitchView)  # "Space" key. May be worth binding whole sortir?
    UINormal()
    zanyato.focus_set()  # moving focus to preview


def zoomIn(event=None) -> None:
    """Zoom preview in"""

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
    """Zoom preview out"""

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
    """zoomIn or zoomOut by mouse wheel"""

    if event.delta < 0:
        zoomOut()
    if event.delta > 0:
        zoomIn()


def SwitchView(event=None) -> None:
    """Switch preview between preview_src and preview_filtered"""

    global zoom_factor, view_src, preview
    view_src = not view_src
    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')


def SaveAsLinen() -> None:
    """Once pressed on Linen"""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Linen.pov',
    )
    if savefilename == '':
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        │ using global maxcolors, image3D                     │
        └─────────────────────────────────────────────────────┘ """
    UIBusy()
    linen.linen(image3D, maxcolors, savefilename)
    UINormal()


def SaveAsStitch() -> None:
    """Once pressed on Stitch"""

    global sourcefilename
    savefilename = asksaveasfilename(
        title='Save POV-Ray file',
        filetypes=[
            ('POV-Ray file', '.pov'),
            ('All Files', '*.*'),
        ],
        defaultextension='.pov',
        initialfile=Path(sourcefilename).stem + '_Stitch.pov',
    )
    if savefilename == '':
        return

    """ ┌─────────────────────────────────────────────────────┐
        │ Converting list to POV and saving as "savefilename" │
        │ using global maxcolors, image3D                     │
        └─────────────────────────────────────────────────────┘ """
    UIBusy()
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

# ↓ Buttons dictionaries
butt = {
    'font': ('helvetica', 12),
    'cursor': 'hand2',
    'border': '2',
    'relief': 'groove',
    'overrelief': 'raised',
    'foreground': 'SystemButtonText',
    'background': 'SystemButtonFace',
    'activeforeground': 'dark blue',
    'activebackground': '#E5F1FB',
}

# ↓ Info statuses dictionaries
info_normal = {'txt': f'POV-Ray Thread {__version__}', 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

# ↓ initial sortir binding, before image load
sortir.bind_all('<Button-3>', ShowMenu)  # Popup menu
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)

frame_top = Frame(sortir, borderwidth=2, relief='groove')
frame_top.pack(side='top', anchor='n', pady=(0, 2))
frame_preview = Frame(sortir, borderwidth=2, relief='groove')
frame_preview.pack(side='top', anchor='center', expand=True)

""" ┌──────────────────────┐
    │ Top frame (controls) │
    └─────────────────────-┘ """

# ↓ File and menu
butt_file = Menubutton(
    frame_top,
    text='File...'.ljust(10, ' '),
    font=butt['font'],
    cursor=butt['cursor'],
    relief=butt['relief'],
    activeforeground=butt['activeforeground'],
    activebackground=butt['activebackground'],
    border=butt['border'],
    state='normal',
    indicatoron=False,
)
butt_file.pack(side='left', padx=(0, 10), pady=0, fill='x')

menu02 = Menu(butt_file, tearoff=False)  # "File" menu
menu02.add_command(label='Open...', state='normal', command=GetSource, accelerator='Ctrl+O')
menu02.add_separator()
menu02.add_command(label='Export Linen...', state='disabled', command=SaveAsLinen)
menu02.add_command(label='Export Stitch...', state='disabled', command=SaveAsStitch)
menu02.add_separator()
menu02.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu02.add_separator()
menu02.add_command(label='Exit', state='normal', command=DisMiss, accelerator='Ctrl+Q')

butt_file['menu'] = menu02

butt_file.bind('<Enter>', lambda event=None: butt_file.config(relief=butt['overrelief']))
butt_file.bind('<Leave>', lambda event=None: butt_file.config(relief=butt['relief']))

butt_file.focus_set()  # Setting focus to "File..."

# ↓ Filter section begins
info00 = Label(frame_top, text='Filtering \nThreshold:', font=('helvetica', 8, 'italic'), justify='right', foreground='brown', state='disabled')
info00.pack(side='left', padx=(0, 4), pady=0, fill='x')

# ↓ X-pass threshold control
info01 = Label(frame_top, text='X:', font=('helvetica', 10), state='disabled')
info01.pack(side='left', padx=0, pady=0, fill='x')

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_x, state='disabled', width=3, font=('helvetica', 11))
spin01.pack(side='left', padx=(0, 4), pady=0, fill='x')

# ↓ Y-pass threshold control
info02 = Label(frame_top, text='Y:', font=('helvetica', 10), state='disabled')
info02.pack(side='left', padx=0, pady=0, fill='both')

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_top, from_=0, to=256, increment=1, textvariable=ini_threshold_y, state='disabled', width=3, font=('helvetica', 11))
spin02.pack(side='left', padx=(0, 4), pady=0, fill='x')

# ↓ Filter start
butt_filter = Button(
    frame_top,
    text='Filter',
    font=butt['font'],
    cursor='arrow',
    relief=butt['relief'],
    overrelief=butt['overrelief'],
    activeforeground=butt['activeforeground'],
    activebackground=butt['activebackground'],
    border=butt['border'],
    state='disabled',
    command=RunFilter,
)
butt_filter.pack(side='left', padx=0, pady=0, fill='both')

""" ┌──────────────────────────────┐
    │ Center frame (image preview) │
    └─────────────────────────────-┘ """
zanyato = Label(
    frame_preview,
    text='Preview area.\n  Double click to open image,\n  Right click or Alt+F for a menu.\nWith image opened,\n  Ctrl+Click to zoom in,\n  Alt+Click to zoom out,\n  Enter to filter.\nWhen filtered, click or Space bar\nto switch source/result.',
    font=('helvetica', 12),
    justify='left',
    borderwidth=2,
    padx=24,
    pady=24,
    background='grey90',
    relief='groove',
)
zanyato.bind('<Double-Button-1>', GetSource)  # Double-click to "Open"
frame_preview.bind('<Double-Button-1>', GetSource)
zanyato.pack(side='top')

frame_zoom = Frame(frame_preview, width=300, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

# ↓ Center window horizontally, +100 vertically
sortir.update()
# print(sortir.winfo_width(), sortir.winfo_height())
sortir.minsize(sortir.winfo_width(), 320)
sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+100')

sortir.mainloop()
