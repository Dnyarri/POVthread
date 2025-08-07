#!/usr/bin/env python3

"""
Averaging image pixels in a row until reaching abs(average - input) threshold, then repeating in a column.

Created by: `Ilya Razmanov <https://dnyarri.github.io/>`_

History:
---------

0.10.12.3   Initial version - 12 Oct 2024. RGB only.

0.10.13.2   Forces RGB, skips alpha. Changed threshold condition to r, g, b separately. Seem to be just what I need.

0.10.25.1   Bugfix for tiny objects.

1.16.5.10   Modularization, some optimization. Force keep alpha.

1.17.10.1   Edge condition bugfix.

2.19.14.16  Wrap around processing introduced.

3.20.1.1    Substantial rewriting with `map` to correctly support L. No force RGB anymore.

3.20.7.14   Alpha filtering. Full support for L, LA, RGB, RGBA filtering with one `map`.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.20.7.14'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from operator import add, floordiv  # Operator in `map` seem to work ca. 7% faster than lambda


def create_image(X: int, Y: int, Z: int) -> list[list[list[int]]]:
    """Create empty 3D nested list of X * Y * Z size."""

    new_image = [[[0 for z in range(Z)] for x in range(X)] for y in range(Y)]

    return new_image


def filter(source_image: list[list[list[int]]], threshold_x: int, threshold_y: int, wrap_around: bool = False, keep_alpha: bool = False) -> list[list[list[int]]]:
    """Average image pixels in a row until borderline threshold met, then repeat in a column."""

    Y = len(source_image)
    X = len(source_image[0])
    Z = len(source_image[0][0])

    if Z == 1 or Z == 3:
        Z_COLOR = Z
    else:
        Z_COLOR = Z - 1  # Color channels without alpha

    # ↓ Creating empty intermediate and final images
    intermediate_image = create_image(X, Y, Z)
    result_image = create_image(X, Y, Z)

    """ ┌──────────────────────────────────────────┐
        │ Coordinates for reading and writing.     │
        │ NOTE: with 0 overhead filter never goes  │
        │ out of image list index, so separate src │
        │ for repeat edge is unnecessary, it's     │
        │ kept here just for reference and reuse.  │
        └──────────────────────────────────────────┘ """

    def cx_r(x: int | float) -> int:
        """x for repeat edge"""
        cx = min((X - 1), max(0, int(x)))  # x repeat edge
        return cx

    def cx_w(x: int | float) -> int:
        """x for wrap around"""
        cx = int(x) % X  # x wrap around
        return cx

    def cy_r(y: int | float) -> int:
        """y for repeat edge"""
        cy = min((Y - 1), max(0, int(y)))  # y repeat edge
        return cy

    def cy_w(y: int | float) -> int:
        """y for wrap around"""
        cy = int(y) % Y  # y wrap around
        return cy

    # ↓ setting wrap around as default, with overhead = 0 it works like "as is"
    cx = cx_w
    cy = cy_w

    if wrap_around:  # Threshold may never be met, yet loop must be stopped somewhere.
        x_overhead = X  # Smaller values sometimes do not work, depending on image;
        y_overhead = Y  # bigger values make no sense.
    else:
        x_overhead = y_overhead = 0

    """ ┌─────────────────┐
        │ Horizontal pass │
        └─────────────────┘ """
    number: int  # Have to be declared somehow in order to define function below

    def _criterion_x(channel: int, channel_sum: int) -> bool:  # Defined function seem to work ca. 5% faster than lambda
        """Threshold criterion for x"""
        return abs(channel - (channel_sum / number)) > threshold_x  # Uses outer scope `number` and `threshold_x`

    for y in range(0, Y, 1):
        pixel = source_image[0][0]
        pixels_sum = pixel
        x_start = 0  # Defining start of inner loop until threshold
        number = 1
        for x in range(0, X + x_overhead, 1):
            pixel = source_image[cy(y)][cx(x)]
            number += 1
            pixels_sum = list(map(add, pixel, pixels_sum))  # Core part of averaging - adding up
            if (True in list(map(_criterion_x, pixel[:Z_COLOR], pixels_sum[:Z_COLOR]))) or (x == (X - 1 + x_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z))  # Inner loop result
                for i in range(x_start, x - 1, 1):
                    intermediate_image[y][cx(i)] = average_pixel
                x_start = x  # Redefining start of new inner loop until threshold
                number = 1
                pixels_sum = pixel
            intermediate_image[y][cx(x)] = pixel  # Edge pixel

    """ ┌───────────────┐
        │ Vertical pass │
        └───────────────┘ """

    def _criterion_y(channel: int, channel_sum: int) -> bool:
        """Threshold criterion for y"""
        return abs(channel - (channel_sum / number)) > threshold_y  # Uses outer scope `number` and `threshold_y`

    for x in range(0, X, 1):
        pixel = intermediate_image[0][0]
        pixels_sum = pixel
        y_start = 0  # Defining start of inner loop until threshold
        number = 1
        for y in range(0, Y + y_overhead, 1):
            pixel = intermediate_image[cy(y)][cx(x)]
            number += 1
            pixels_sum = list(map(add, pixel, pixels_sum))  # Core part of averaging - adding up
            if (True in list(map(_criterion_y, pixel[:Z_COLOR], pixels_sum[:Z_COLOR]))) or (y == (Y - 1 + y_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z))  # Inner loop result
                for i in range(y_start, y - 1, 1):
                    result_image[cy(i)][x] = average_pixel
                y_start = y  # Redefining start of new inner loop until threshold
                number = 1
                pixels_sum = pixel
            result_image[cy(y)][x] = pixel  # Edge pixel

    """ ┌────────────────┐
        │ Alpha handling │
        └────────────────┘ """
    if Z == 1 or Z == 3:
        return result_image
    else:
        if keep_alpha:
            resultimage_plus_alpha = [[[*result_image[y][x][:Z_COLOR], source_image[y][x][Z_COLOR]] for x in range(X)] for y in range(Y)]  # Unpacking result_image pixels, overwriting alpha, and packing back
            return resultimage_plus_alpha
        else:
            return result_image


if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
