"""Adaptive average image filtering module.

Usage
-----

::

    from filter.avgrow import filter
    filtered_image = filter(source_image, threshold_x, threshold_y, wraparound, keep_alpha)

where:

- **``source_image``**: input image as list of lists of lists
  of ``int`` channel values;
- **``threshold_x``**: threshold upon which row averaging stops
  and restarts from this pixel on (``int``);
- **``threshold_y``**: threshold upon which column averaging stops
  and restarts from this pixel on (``int``);
- **``wrap_around``**: whether image edge pixel will be read in
  "repeat edge" or "wrap around" mode (``bool``);
- **``keep_alpha``**: whether returned filtered image will have
  alpha channel copied from source image, or alpha channel will be
  filtered along with color (``bool``).

.. note:: Both threshold values (``int``) are used literally,
    regardless of 8 bpc or 16 bpc color depth.
    Filter input does not include color depth and/or range value in any form,
    therefore threshold range normalization, if deemed necessary,
    must be performed at host end.

.. warning:: Some programs completely destroy L or RGB data upon saving
    LA or RGBA image pixels with A=0 (fully transparent) as PNG.
    This may lead to unexpected and unpredictable results of filtering.
    This potential problem is completely out of responsibility scope
    of current filter developer.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.32.8.24'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'
