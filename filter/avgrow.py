#!/usr/bin/env python3

"""
Averaging image pixels in a row until reaching `abs(average - current) > threshold`, then repeating in a column.

Created by: `Ilya Razmanov <https://dnyarri.github.io/>`_

History:
---------

0.10.12.3   Initial version - 12 Oct 2024. RGB only.

0.10.13.2   Forces RGB, skips alpha. Changed threshold condition to r, g, b separately. 
Seem to be just what I need.

0.10.25.1   Bugfix for tiny details.

1.16.5.10   Modularization, some optimization. Force keep alpha.

1.17.10.1   Edge condition bugfix.

2.19.14.16  Wrap around processing introduced.

3.20.1.1    Substantial rewriting with `map` to correctly support L.
No force RGB anymore.

3.20.7.14   Alpha filtering. Full support for L, LA, RGB, RGBA filtering with one `map`.

3.20.20.3   Code harmonization. Lambdas completely replaced with operators
and defined functions to improve speed.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.22.01.11'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from operator import add, floordiv  # Operator in `map` seem to work ca. 7% faster than lambda.


def create_image(X: int, Y: int, Z: int) -> list[list[list[int]]]:
    """Create 3D nested list of X * Y * Z size, filled with zeroes."""

    new_image = [[[0 for z in range(Z)] for x in range(X)] for y in range(Y)]
    return new_image


def filter(source_image: list[list[list[int]]], threshold_x: int, threshold_y: int, wrap_around: bool = False, keep_alpha: bool = False) -> list[list[list[int]]]:
    """Average image pixels in a row until `abs(average - current) > threshold` criterion met, then repeat in a column."""

    # ↓ Determining image sizes.
    Y = len(source_image)
    X = len(source_image[0])
    Z = len(source_image[0][0])
    Z_COLOR = Z if Z == 1 or Z == 3 else min(Z - 1, 3)  # Number of color channels, alpha excluded.

    # ↓ Creating empty intermediate and final images.
    intermediate_image = create_image(X, Y, Z)
    result_image = create_image(X, Y, Z)

    """ ┌──────────────────────────────────────────┐
        │ Coordinates for reading and writing.     │
        │ NOTE: with 0 overhead filter never goes  │
        │ out of image list index, so separate src │
        │ for repeat edge is unnecessary, it's     │
        │ kept here just for reference and reuse.  │
        └──────────────────────────────────────────┘ """

    def cx_repeat(x: int | float) -> int:
        """x for repeat edge"""
        return min((X - 1), max(0, int(x)))  # x repeat edge

    def cx_wrap(x: int | float) -> int:
        """x for wrap around"""
        return int(x) % X  # x wrap around

    def cy_repeat(y: int | float) -> int:
        """y for repeat edge"""
        return min((Y - 1), max(0, int(y)))  # y repeat edge

    def cy_wrap(y: int | float) -> int:
        """y for wrap around"""
        return int(y) % Y  # y wrap around

    # ↓ Setting wrap around as default, with overhead = 0 it works like "as is".
    cx = cx_wrap
    cy = cy_wrap

    if wrap_around:  # Threshold may never be met, yet loop must be stopped somewhere.
        x_overhead = X  # Smaller values sometimes do not work, depending on image;
        y_overhead = Y  # bigger values make no sense.
    else:
        x_overhead = y_overhead = 0

    """ ┌─────────────────┐
        │ Horizontal pass │
        └─────────────────┘ """

    def _criterion_x(channel: int, channel_sum: int) -> bool:
        """Threshold criterion for x, single channel."""
        return abs(channel - (channel_sum / number)) > threshold_x
        # ↑ Defined function seem to work ca. 5% faster than lambda.
        #   Uses outer scope `number` and `threshold_x`.

    for y in range(0, Y, 1):
        x_start = 0  # Defining start of inner loop of averaging until threshold.
        number = 1  # Number of pixels being read during averaging loop.
        pixel = source_image[0][0]  # Current pixel.
        pixels_sum = pixel  # Sum of pixels being read during averaging loop.
        for x in range(0, X + x_overhead, 1):
            number += 1
            pixel = source_image[cy(y)][cx(x)]
            pixels_sum = list(map(add, pixel, pixels_sum))  # Core part of averaging - adding up.
            if (True in list(map(_criterion_x, pixel[:Z_COLOR], pixels_sum[:Z_COLOR]))) or (x == (X - 1 + x_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z))  # Inner loop result.
                for i in range(x_start, x - 1, 1):
                    intermediate_image[y][cx(i)] = average_pixel
                # ↓ Redefining start of new inner loop until threshold.
                x_start = x
                number = 1
                pixels_sum = pixel
            intermediate_image[y][cx(x)] = pixel  # Edge pixel.

    """ ┌───────────────┐
        │ Vertical pass │
        └───────────────┘ """

    def _criterion_y(channel: int, channel_sum: int) -> bool:
        """Threshold criterion for y, single channel"""
        return abs(channel - (channel_sum / number)) > threshold_y

    for x in range(0, X, 1):
        y_start = 0
        number = 1
        pixel = intermediate_image[0][0]
        pixels_sum = pixel
        for y in range(0, Y + y_overhead, 1):
            number += 1
            pixel = intermediate_image[cy(y)][cx(x)]
            pixels_sum = list(map(add, pixel, pixels_sum))
            if (True in list(map(_criterion_y, pixel[:Z_COLOR], pixels_sum[:Z_COLOR]))) or (y == (Y - 1 + y_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z))
                for i in range(y_start, y - 1, 1):
                    result_image[cy(i)][x] = average_pixel
                y_start = y
                number = 1
                pixels_sum = pixel
            result_image[cy(y)][x] = pixel

    """ ┌────────────────┐
        │ Alpha handling │
        └────────────────┘ """
    if Z == 1 or Z == 3:
        return result_image
    else:
        if keep_alpha:
            # ↓ Unpacking result_image pixels, overwriting alpha, and packing back.
            resultimage_plus_alpha = [[[*result_image[y][x][:Z_COLOR], source_image[y][x][Z_COLOR]] for x in range(X)] for y in range(Y)]
            return resultimage_plus_alpha
        else:
            return result_image
# ↑ filter finished

# ↓ Dummy stub for standalone execution attempt
if __name__ == '__main__':
    print('Module to be imported, not run as standalone.')
    need_help = input('Would you like to read some help (y/n)?')
    if need_help.startswith(('y', 'Y')):
        import avgrow
        help(avgrow)
