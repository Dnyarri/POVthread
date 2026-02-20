"""Adaptive average image filtering module.

Usage
-----

::

    from filter import avgrow
    result_image = avgrow.filter(source_image, threshold_x, threshold_y, wraparound, keep_alpha)

where:

- ``source_image``: input image as list of lists of lists of int channel values;
- ``threshold_x``: threshold upon which row averaging stops
  and restarts from this pixel on (int);
- ``threshold_y``: threshold upon which column averaging stops
  and restarts from this pixel on (int);
- ``wrap_around``: whether image edge pixel will be read in
  "repeat edge" or "wrap around" mode (bool);
- ``keep_alpha``: whether returned filtered image will have
  alpha channel matching source image, or alpha channel will be
  filtered along with color (bool).

.. note:: Both threshold values (int) are used literally,
    regardless of 8 bpc or 16 bpc color depth.
    Filter input does not include color depth and/or range value in any form,
    therefore threshold range normalization, if deemed necessary,
    must be performed at host end.

"""
