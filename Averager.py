#!/usr/bin/env python3

"""Adaptive color average image filtering.
-------------------------------------------

Average image colors in a pixel row until difference between averaged and next pixel in a row reach threshold. Then repeat the same in column. Thus filter changes smooth image areas to completely flat colored, with detailed edges between them.

Input: PNG, PPM, PGM, PBM.

Output: PNG, PPM, PGM.

Created by: `Ilya Razmanov<mailto:ilyarazmanov@gmail.com>`_ aka `Ilyich the Toad<mailto:amphisoft@gmail.com>`_.

History:
----

0.10.14.0   Initial version of filter host template - 14 Oct 2024. Using png in tempfile preview etc.

1.14.1.1    Preview etc with PyPNM. Image list moved to global to reduce rereading.

1.16.4.24   PNG and PPM support, zoom in and out, numerous fixes.

1.16.9.14   Preview switch source/result added. Zoom on click now mimic Photoshop Ctrl + Click and Alt + Click.

2.16.20.20  Changed GUI to menus.

3.20.8.8    Changed GUI to grid to fit all new features. More detailed image info;
image mode and edited/saved status displayed in window title (and task manager) a-la Photoshop.

1.23.1.1    Even more GUI improvements, including spinbox control with mousewheel.

----
Main site: `The Toad's Slimy Mudhole<https://dnyarri.github.io>`_

Git: `Dnyarri at Github<https://github.com/Dnyarri>`_; `Gitflic mirror<https://gitflic.ru/user/dnyarri>`_

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.23.7.9'
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

""" ╔══════════════════════════════════╗
    ║ GUI events and functions thereof ║
    ╚══════════════════════════════════╝ """


def DisMiss(event=None) -> None:
    """Kill dialog and continue."""

    sortir.destroy()


def ShowMenu(event) -> None:
    """Pop menu up (or sort of drop it down)."""

    menu02.post(event.x_root, event.y_root)


def ShowInfo(event=None) -> None:
    """Show image information."""

    file_size = Path(sourcefilename).stat().st_size
    file_size_str = f'{file_size / 1048576:.2f} Mb' if (file_size > 1048576) else f'{file_size / 1024:.2f} Kb' if (file_size > 1024) else f'{file_size} bytes'
    showinfo(
        title='Image information',
        message=f'File properties:\nLocation: {sourcefilename}\nSize: {file_size_str}\nLast modified: {ctime(Path(sourcefilename).stat().st_mtime)}',
        detail=f'Image properties, as represented internally:\nStatus: {is_filtered=}, {is_saved=}\nWidth: {X} px\nHeight: {Y} px\nChannels: {Z} channel{"s" if Z > 1 else ""}\nColor depth: {maxcolors + 1} gradations/channel',
    )


def UINormal() -> None:
    """Normal UI state, buttons enabled."""

    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox', 'Checkbutton'):
            widget['state'] = 'normal'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'hand2'
    info_string.config(text=info_normal['txt'], foreground=info_normal['fg'], background=info_normal['bg'])
    if Z == 1 or Z == 3:
        check02['state'] = 'disabled'
    sortir.update()


def UIBusy() -> None:
    """Busy UI state, buttons disabled."""

    for widget in frame_top.winfo_children():
        if widget.winfo_class() in ('Label', 'Button', 'Spinbox', 'Checkbutton'):
            widget['state'] = 'disabled'
        if widget.winfo_class() == 'Button':
            widget['cursor'] = 'arrow'
    info_string.config(text=info_busy['txt'], foreground=info_busy['fg'], background=info_busy['bg'])
    sortir.update()


def ShowPreview(preview_name: PhotoImage, caption: str) -> None:
    """Show preview_name PhotoImage with caption below."""

    global zoom_factor, preview

    preview = preview_name

    if zoom_factor > 0:
        preview = preview.zoom(zoom_factor + 1)
        label_zoom['text'] = f'Zoom {zoom_factor + 1}:1'
    elif zoom_factor < 0:
        preview = preview.subsample(1 - zoom_factor)
        label_zoom['text'] = f'Zoom 1:{1 - zoom_factor}'
    else:
        preview = preview_name
        label_zoom['text'] = 'Zoom 1:1'

    zanyato.config(text=caption, font=('helvetica', 8), image=preview, compound='top', padx=0, pady=0, justify='center', background=zanyato.master['background'], relief='flat', borderwidth=1, state='normal')
    zanyato.pack_configure(pady=max(0, 16 - (preview.height() // 2)))


def GetSource(event=None) -> None:
    """Open source image and redefine other controls state."""

    global zoom_factor, view_src, is_filtered, is_saved, info_normal, color_mode_str
    global preview, preview_src, preview_filtered  # preview and copies of preview
    global X, Y, Z, maxcolors, image3D, info, sourcefilename
    global source_image3D  # deep copy of source data, to be used as a source for filtering

    zoom_factor = 0
    view_src = True
    is_filtered = False
    is_saved = True

    sourcefilename = askopenfilename(title='Open image file', filetypes=[('Supported formats', '.png .ppm .pgm .pbm .pnm'), ('Portable network graphics', '.png'), ('Portable any map', '.ppm .pgm .pbm .pnm')])
    if sourcefilename == '':
        return

    UIBusy()

    """ ┌────────────────────────────────────────┐
        │ Loading file, converting data to list. │
        │ NOTE: maxcolors, image3D, info MUST be │
        │ GLOBALS! They are used during saving!  │
        └────────────────────────────────────────┘ """

    if Path(sourcefilename).suffix.lower() == '.png':
        # ↓ Reading PNG image as list
        X, Y, Z, maxcolors, source_image3D, info = png2list(sourcefilename)

    elif Path(sourcefilename).suffix.lower() in ('.ppm', '.pgm', '.pbm', '.pnm'):
        # ↓ Reading PNM image as list
        X, Y, Z, maxcolors, source_image3D = pnm2list(sourcefilename)
        # ↓ Creating dummy info required to correctly Save As PNG later.
        #   Fixing color mode, the rest is fixed with pnglpng v. 25.01.07.
        info = {'bitdepth': 16} if maxcolors > 255 else {'bitdepth': 8}

    else:
        raise ValueError('Extension not recognized')

    """ ┌────────────────────────────────────────────┐
        │ Creating deep copy of source 3D list       │
        │ to avoid accumulating repetitive filtering │
        └────────────────────────────────────────────┘ """
    image3D = deepcopy(source_image3D)

    """ ┌───────────────┐
        │ Viewing image │
        └───────────────┘ """
    # ↓ Converting list to bytes of PNM-like structure "preview_data" in memory
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

    # ↓ Attempt to zoom to fit. Singe zoomOut() must fit for a reasonable image size.
    #   GUI X extra = 8 px, GUI Y extra = 150 px
    if X + 16 > sortir.winfo_screenwidth() or Y + 152 > sortir.winfo_screenheight():
        zoomOut()

    # ↓ binding on preview click
    zanyato.bind('<Control-Button-1>', zoomIn)  # Ctrl + left click
    zanyato.bind('<Double-Control-Button-1>', zoomIn)  # Ctrl + left click too fast
    zanyato.bind('<Control-+>', zoomIn)
    zanyato.bind('<Control-=>', zoomIn)
    zanyato.bind('<Alt-Button-1>', zoomOut)  # Alt + left click
    zanyato.bind('<Double-Alt-Button-1>', zoomOut)  # Alt + left click too fast
    zanyato.bind('<Control-minus>', zoomOut)
    zanyato.bind('<Control-Key-1>', zoomOne)
    zanyato.bind('<Control-Alt-Key-0>', zoomOne)
    # ↓ binding global
    sortir.bind_all('<Return>', RunFilter)
    sortir.bind_all('<MouseWheel>', zoomWheel)  # Wheel scroll
    sortir.bind_all('<Control-i>', ShowInfo)
    menu02.entryconfig('Image Info...', state='normal')
    # ↓ Spin
    spin01.unbind('<MouseWheel>')
    spin01.bind('<MouseWheel>', incWheel)
    spin02.unbind('<MouseWheel>')
    spin02.bind('<MouseWheel>', incWheel)
    # ↓ enabling Save as...
    menu02.entryconfig('Save as...', state='normal')
    sortir.bind_all('<Control-Shift-S>', SaveAs)
    # ↓ enabling zoom buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')
    # ↓ Adding filename, mode and status to window title a-la Photoshop
    if Z == 1:
        color_mode_str = f' (L:{"8" if maxcolors < 256 else "16"})'
    elif Z == 2:
        color_mode_str = f' (LA:{"8" if maxcolors < 256 else "16"})'
    elif Z == 3:
        color_mode_str = f' (RGB:{"8" if maxcolors < 256 else "16"})'
    elif Z == 4:
        color_mode_str = f' (RGBA:{"8" if maxcolors < 256 else "16"})'
    else:
        color_mode_str = ''  # Just in case
    sortir.title(f'{product_name}: {Path(sourcefilename).name}{color_mode_str}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    # ↓ enabling "Filter"
    butt_filter.bind('<Enter>', lambda event=None: butt_filter.config(foreground=butt['activeforeground'], background=butt['activebackground']))
    butt_filter.bind('<Leave>', lambda event=None: butt_filter.config(foreground=butt['foreground'], background=butt['background']))
    UINormal()
    sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+{(sortir.winfo_screenheight() - sortir.winfo_height()) // 2 - 32}')
    zanyato.focus_set()


def RunFilter(event=None) -> None:
    """Filter image, then preview result."""

    global zoom_factor, view_src, is_filtered, is_saved, info_normal, color_mode_str
    global preview, preview_filtered
    global X, Y, Z, maxcolors, image3D, source_image3D, info

    # ↓ filtering parameters
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
    # ↓ binding global
    sortir.bind_all('<Control-s>', Save)
    # ↓ binding switch on preview click
    zanyato.bind('<Button-1>', SwitchView)  # left click
    zanyato.bind('<space>', SwitchView)  # # "Space" key. May be worth binding whole sortir?
    # ↓ Adding filename, mode and status to window title a-la Photoshop
    sortir.title(f'{product_name}: {Path(sourcefilename).name}{color_mode_str}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    UINormal()
    zanyato.focus_set()  # moving focus to preview


def zoomIn(event=None) -> None:
    """Zoom preview in."""

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
    """Zoom preview out."""

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


def zoomOne(event=None) -> None:
    """Zoom 1:1."""

    global zoom_factor, view_src, preview
    zoom_factor = 0

    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')

    # ↓ reenabling +/- buttons
    butt_plus.config(state='normal', cursor='hand2')
    butt_minus.config(state='normal', cursor='hand2')


def zoomWheel(event) -> None:
    """zoomIn or zoomOut by mouse wheel."""

    if event.widget not in transparent_controls:
        if event.delta < 0:
            zoomOut()
        if event.delta > 0:
            zoomIn()


def SwitchView(event=None) -> None:
    """Switch preview between preview_src and preview_filtered."""

    global zoom_factor, view_src, preview
    view_src = not view_src
    if view_src:
        ShowPreview(preview_src, 'Source')
    else:
        ShowPreview(preview_filtered, 'Result')


def onSave() -> None:
    global sourcefilename, resultfilename, is_saved
    global source_image3D, image3D, X, Y, Z, maxcolors
    global preview_data, preview_filtered, preview_src, info_normal

    sourcefilename = resultfilename  # Now saved file becomes new source file
    source_image3D = deepcopy(image3D)
    preview_data = list2bin(image3D, maxcolors, show_chessboard=True)
    preview_filtered = PhotoImage(data=preview_data)
    preview_src = preview_filtered

    # ↓ disabling save
    menu02.entryconfig('Save', state='disabled')
    sortir.unbind_all('<Control-s>')
    # ↓ binding switch on preview click
    zanyato.unbind('<Button-1>')  # left click
    zanyato.unbind('<space>')  # # "Space" key. May be worth binding whole sortir?
    # ↓ preview source
    ShowPreview(preview_src, 'Source')
    # ↓ Adding filename, mode and status to window title a-la Photoshop
    sortir.title(f'{product_name}: {Path(sourcefilename).name}{color_mode_str}{"*" if is_filtered else ""}')
    info_normal = {'txt': f'{Path(sourcefilename).name}{"*" if is_filtered else ""} X={X} Y={Y} Z={Z} maxcolors={maxcolors}', 'fg': 'grey', 'bg': 'grey90'}
    UINormal()


def Save(event=None) -> None:
    """Once pressed on Save."""

    global is_filtered, is_saved, info_normal, color_mode_str
    global source_image3D, sourcefilename, resultfilename

    if is_saved:  # block repetitive saving
        return
    if not is_filtered:  # block useless source resaving
        return
    resultfilename = sourcefilename
    UIBusy()
    # ↓ Save format choice
    if Path(resultfilename).suffix.lower() == '.png':
        info['compression'] = 9  # Explicitly setting compression
        list2png(resultfilename, image3D, info)  # Writing file
    elif Path(resultfilename).suffix.lower() in ('.ppm', '.pgm', '.pnm'):
        list2pnm(resultfilename, image3D, maxcolors)  # Writing file
    # ↓ Flagging image as saved, not filtered
    is_saved = True  # to block future repetitive saving
    is_filtered = False
    # ↓ Now saved file becomes new source file
    onSave()
    UINormal()


def SaveAs(event=None) -> None:
    """Once pressed on Save as..."""

    global is_saved, is_filtered, info_normal, color_mode_str
    global source_image3D, sourcefilename, resultfilename

    # ↓ Adjusting "Save as" formats to be displayed
    #   according to bitdepth and source extension
    src_extension = Path(sourcefilename).suffix.lower()
    if Z == 1:
        if src_extension in ('.pgm', '.pnm'):
            format_list = [('Portable grey map', '.pgm'), ('Portable network graphics', '.png')]
            proposed_name = Path(sourcefilename).stem + '.pgm'
        else:
            format_list = [('Portable network graphics', '.png'), ('Portable grey map', '.pgm')]
            proposed_name = Path(sourcefilename).stem + '.png'
    elif Z == 2:
        format_list = [('Portable network graphics', '.png')]
        proposed_name = Path(sourcefilename).stem + '.png'
    elif Z == 3:
        if src_extension in ('.ppm', '.pnm'):
            format_list = [('Portable pixel map', '.ppm'), ('Portable network graphics', '.png')]
            proposed_name = Path(sourcefilename).stem + '.ppm'
        else:
            format_list = [('Portable network graphics', '.png'), ('Portable pixel map', '.ppm')]
            proposed_name = Path(sourcefilename).stem + '.png'
    else:
        format_list = [('Portable network graphics', '.png')]
        proposed_name = Path(sourcefilename).stem + '.png'

    # ↓ Open export file
    resultfilename = asksaveasfilename(
        title='Save image file',
        filetypes=format_list,
        defaultextension='.png',  # No extension should never happen but just in case
        initialdir=Path(sourcefilename).parent,
        initialfile=proposed_name,
    )
    if resultfilename == '':
        return None
    UIBusy()
    # ↓ Save format choice
    if Path(resultfilename).suffix.lower() == '.png':
        info['compression'] = 9  # Explicitly setting compression
        list2png(resultfilename, image3D, info)  # Writing file
    elif Path(resultfilename).suffix.lower() in ('.ppm', '.pgm'):
        list2pnm(resultfilename, image3D, maxcolors)  # Writing file
    else:
        raise ValueError('Extension not recognized')
    # ↓ Flagging image as saved, not filtered, and disabling "Save"
    is_saved = True  # to block future repetitive saving
    is_filtered = False
    # ↓ Now saved file becomes new source file
    onSave()
    UINormal()


def valiDig(new_value):
    """Validate Spinbox input and reject non-integer."""

    if new_value.strip() == '':
        return True
    try:
        _ = int(new_value)
        if _ >= 0 and _ < 256:
            return True
        else:
            return False
    except ValueError:
        return False


def incWheel(event) -> None:
    """Increment or decrement spinboxes by mouse wheel."""

    if event.widget == spin01:
        if event.delta < 0:
            ini_threshold_x.set(min(255, max(0, ini_threshold_x.get() - 1)))
        if event.delta > 0:
            ini_threshold_x.set(min(255, max(0, ini_threshold_x.get() + 1)))
    if event.widget == spin02:
        if event.delta < 0:
            ini_threshold_y.set(min(255, max(0, ini_threshold_y.get() - 1)))
        if event.delta > 0:
            ini_threshold_y.set(min(255, max(0, ini_threshold_y.get() + 1)))


""" ╔═══════════╗
    ║ Main body ║
    ╚═══════════╝ """

zoom_factor = 0
view_src = True
is_filtered = False
product_name = 'Averager'

sortir = Tk()

sortir.iconphoto(True, PhotoImage(data='P6\n2 8\n255\n'.encode(encoding='ascii') + randbytes(2 * 8 * 3)))
sortir.title(product_name)

validate_entry = sortir.register(valiDig)

# ↓ Info statuses dictionaries
info_normal = {'txt': f'Adaptive Average {__version__}', 'fg': 'grey', 'bg': 'grey90'}
info_busy = {'txt': 'BUSY, PLEASE WAIT', 'fg': 'red', 'bg': 'yellow'}
color_mode_str = ' '

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

info_string = Label(sortir, text=info_normal['txt'], font=('courier', 7), foreground=info_normal['fg'], background=info_normal['bg'], relief='groove')
info_string.pack(side='bottom', padx=0, pady=(2, 0), fill='both')

# ↓ initial sortir binding, before image load
sortir.bind_all('<Button-3>', ShowMenu)  # Popup menu
sortir.bind_all('<Alt-f>', ShowMenu)
sortir.bind_all('<Control-o>', GetSource)
sortir.bind_all('<Control-q>', DisMiss)

frame_top = Frame(sortir, borderwidth=2, relief='groove')
frame_top.pack(side='top', anchor='w', pady=(0, 2))
frame_preview = Frame(sortir, borderwidth=2, relief='groove')
frame_preview.pack(side='top', anchor='center', expand=True)

""" ┌──────────────────────┐
    │ Top frame (controls) │
    └─────────────────────-┘ """

# ↓ File menu
butt_file = Menubutton(
    frame_top,
    text='File...',
    width=8,
    anchor='w',
    font=butt['font'],
    cursor=butt['cursor'],
    relief=butt['relief'],
    activeforeground=butt['activeforeground'],
    activebackground=butt['activebackground'],
    border=butt['border'],
    state='normal',
    indicatoron=False,
)
butt_file.grid(row=0, column=0, rowspan=2, sticky='ns', padx=(0, 10), pady=0)

menu02 = Menu(butt_file, tearoff=False)  # "File" menu
menu02.add_command(label='Open...', state='normal', command=GetSource, accelerator='Ctrl+O')
menu02.add_separator()
menu02.add_command(label='Save', state='disabled', command=Save, accelerator='Ctrl+S')
menu02.add_command(label='Save as...', state='disabled', command=SaveAs, accelerator='Ctrl+Shift+S')
menu02.add_separator()
menu02.add_command(label='Image Info...', accelerator='Ctrl+I', state='disabled', command=ShowInfo)
menu02.add_separator()
menu02.add_command(label='Exit', state='normal', command=DisMiss, accelerator='Ctrl+Q')

butt_file['menu'] = menu02

butt_file.bind('<Enter>', lambda event=None: butt_file.config(relief=butt['overrelief']))
butt_file.bind('<Leave>', lambda event=None: butt_file.config(relief=butt['relief']))

butt_file.focus_set()  # Setting focus to "File..."

# ↓ Filter section begins
info00 = Label(frame_top, text='Filtering threshold:', font=('helvetica', 8, 'italic'), justify='right', foreground='brown', state='disabled')
info00.grid(row=0, column=1)

# ↓ X-pass threshold control
info01 = Label(frame_top, text='X:', font=('helvetica', 11), state='disabled')
info01.grid(row=0, column=2)

ini_threshold_x = IntVar(value=16)
spin01 = Spinbox(frame_top, from_=0, to=255, increment=1, textvariable=ini_threshold_x, state='disabled', width=3, font=('helvetica', 11), validate='key', validatecommand=(validate_entry, '%P'))
spin01.grid(row=0, column=3)

# ↓ Y-pass threshold control
info02 = Label(frame_top, text='Y:', font=('helvetica', 11), state='disabled')
info02.grid(row=0, column=4)

ini_threshold_y = IntVar(value=8)
spin02 = Spinbox(frame_top, from_=0, to=255, increment=1, textvariable=ini_threshold_y, state='disabled', width=3, font=('helvetica', 11), validate='key', validatecommand=(validate_entry, '%P'))
spin02.grid(row=0, column=5)

# ↓ Wrap around control
ini_wraparound = BooleanVar(value=False)
check01 = Checkbutton(frame_top, text='Wrap around', font=('helvetica', 9), variable=ini_wraparound, onvalue=True, offvalue=False, state='disabled')
check01.grid(row=1, column=1, sticky='ws')

# ↓ Keep alpha control
ini_keep_alpha = BooleanVar(value=False)
check02 = Checkbutton(frame_top, text='Keep alpha', font=('helvetica', 9), variable=ini_keep_alpha, onvalue=True, offvalue=False, state='disabled')
check02.grid(row=1, column=3, columnspan=3, sticky='ws')

# ↓ Filter start
butt_filter = Button(
    frame_top,
    text='Filter',
    width=8,
    anchor='center',
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
butt_filter.grid(row=0, column=6, rowspan=2, sticky='nsew', padx=(10, 0), pady=0)

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

frame_zoom = Frame(frame_preview, borderwidth=2, relief='groove')
frame_zoom.pack(side='bottom')

butt_plus = Button(frame_zoom, text='+', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomIn)
butt_plus.pack(side='left', padx=0, pady=0, fill='both')

butt_minus = Button(frame_zoom, text='-', font=('courier', 8), width=2, cursor='arrow', state='disabled', borderwidth=1, command=zoomOut)
butt_minus.pack(side='right', padx=0, pady=0, fill='both')

label_zoom = Label(frame_zoom, text='Zoom 1:1', font=('courier', 8), state='disabled')
label_zoom.pack(side='left', anchor='n', padx=2, pady=0, fill='both')

transparent_controls = (spin01, spin02)  # To be cut off global evens

# ↓ Center window horizontally, +100 vertically
sortir.update()
# print(sortir.winfo_width(), sortir.winfo_height())
sortir.minsize(frame_top.winfo_width(), 320)
sortir.maxsize(9 * sortir.winfo_screenwidth() // 10, 9 * sortir.winfo_screenheight() // 10)
sortir.geometry(f'+{(sortir.winfo_screenwidth() - sortir.winfo_width()) // 2}+100')

sortir.mainloop()
