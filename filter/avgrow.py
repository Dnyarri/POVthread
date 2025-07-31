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

3.20.1.1    Rewriting with map to correctly support L. No force RGB anymore.

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '3.20.1.1'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'

from operator import add, floordiv


def create_image(X: int, Y: int, Z: int) -> list[list[list[int]]]:
    """Create empty 3D nested list of X * Y * Z size."""

    new_image = [[[0 for z in range(Z)] for x in range(X)] for y in range(Y)]

    return new_image


def filter(sourceimage: list[list[list[int]]], threshold_x: int, threshold_y: int, wrap_around: bool = False) -> list[list[list[int]]]:
    """Average image pixels in a row until borderline threshold met, then repeat in a column."""

    Y = len(sourceimage)
    X = len(sourceimage[0])
    Z = len(sourceimage[0][0])

    if Z == 1 or Z == 3:
        Z_COLOR = Z
    else:
        Z_COLOR = Z - 1  # Color channels without alpha

    # Creating empty intermediate image
    medimage = create_image(X, Y, Z_COLOR)

    # Creating empty final image
    resultimage = create_image(X, Y, Z_COLOR)

    """ ┌──────────────────────────────────────────┐
        │ Coordinates for reading and writing.     │
        │ NOTE: with 0 overhead filter never goes  │
        │ out of image list index, so I don't need │
        │ separate src for repeat edge, it's kept  │
        │ here just as a pattern for reference.    │
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

    cx = cx_w  # wrap around, with overhead = 0 works "as is"
    cy = cy_w

    if wrap_around:  # Threshold may never be met, yet loop must be stopped somewhere.
        x_overhead = X  # Smaller values sometimes do not work, depending on image;
        y_overhead = Y  # bigger values make no sense.
    else:
        x_overhead = y_overhead = 0

    """ ┌─────────────────┐
        │ Horizontal pass │
        └─────────────────┘ """
    for y in range(0, Y, 1):
        pixels_sum = pixel = sourceimage[0][0]
        x_start = 0  # Defining start of inner loop until threshold
        number = 1
        for x in range(0, X + x_overhead, 1):
            pixel = sourceimage[cy(y)][cx(x)]
            number += 1
            pixels_sum = list(map(add, pixel, pixels_sum))  # Core part of averaging
            if (True in list(map(lambda c, s: abs(c - (s / number)) > threshold_x, pixel, pixels_sum))) or (x == (X - 1 + x_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z_COLOR))  # Inner loop result
                for i in range(x_start, x - 1, 1):
                    medimage[y][cx(i)] = average_pixel
                x_start = x  # Redefining start of new inner loop until threshold
                number = 1
                pixels_sum = pixel
            medimage[y][cx(x)] = pixel  # Edge pixel

    """ ┌───────────────┐
        │ Vertical pass │
        └───────────────┘ """
    for x in range(0, X, 1):
        pixels_sum = pixel = medimage[0][0]
        y_start = 0  # Defining start of inner loop until threshold
        number = 1
        for y in range(0, Y + y_overhead, 1):
            pixel = medimage[cy(y)][cx(x)]
            number += 1
            pixels_sum = list(map(add, pixel, pixels_sum))  # Core part of averaging
            if (True in list(map(lambda c, s: abs(c - (s / number)) > threshold_y, pixel, pixels_sum))) or (y == (Y - 1 + y_overhead)):
                average_pixel = list(map(floordiv, pixels_sum, (number,) * Z_COLOR))  # Inner loop result
                for i in range(y_start, y - 1, 1):
                    resultimage[cy(i)][x] = average_pixel
                y_start = y  # Redefining start of new inner loop until threshold
                number = 1
                pixels_sum = pixel
            resultimage[cy(y)][x] = pixel  # Edge pixel

    """ ┌────────────────────────────────────────────┐
        │ Protect alpha if exist, then return result │
        └────────────────────────────────────────────┘ """
    if Z == 1 or Z == 3:
        return resultimage
    else:  # Unpack filtered color channels and add source alpha to list
        resultimage_plus_alpha = [[[*resultimage[y][x], sourceimage[y][x][Z - 1]] for x in range(X)] for y in range(Y)]
        return resultimage_plus_alpha


if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
