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

"""

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '2.19.14.16'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'


def create_image(X: int, Y: int, Z: int) -> list[list[list[int]]]:
    """Create empty 3D nested list of X * Y * Z size."""

    new_image = [
                    [
                        [0 for z in range(Z)] for x in range(X)
                    ] for y in range(Y)
                ]

    return new_image


def filter(sourceimage: list[list[list[int]]], threshold_x: int, threshold_y: int, wrap_around: bool = False) -> list[list[list[int]]]:
    """Average image pixels in a row until borderline threshold met, then repeat in a column."""

    Y = len(sourceimage)
    X = len(sourceimage[0])
    Z = len(sourceimage[0][0])

    # Creating empty RGB intermediate image
    medimage = create_image(X, Y, 3)

    # Creating empty RGB final image
    resultimage = create_image(X, Y, 3)

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

    if wrap_around:  # Threshold may never be met, yet loop must be stopped somewhere
        x_overhead = X
        y_overhead = Y
    else:
        x_overhead = 0
        y_overhead = 0

    for y in range(0, Y, 1):
        if Z > 2:
            r_sum, g_sum, b_sum = r, g, b = sourceimage[0][0][0:3]
        else:
            r_sum = g_sum = b_sum = r = g = b = sourceimage[0][0][0]
        x_start = 0  # Defining start of inner loop until threshold
        number = 1
        for x in range(0, X + x_overhead, 1):
            if Z > 2:
                r, g, b = sourceimage[cy(y)][cx(x)][0:3]
            else:
                r = g = b = sourceimage[cy(y)][cx(x)][0]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_x) or (abs(g - (g_sum / number)) > threshold_x) or (abs(b - (b_sum / number)) > threshold_x) or (x == (X - 1 + x_overhead)):
                for i in range(x_start, x - 1, 1):
                    medimage[y][cx(i)] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                medimage[y][cx(x)] = [r, g, b]
                x_start = x  # Redefining start of new inner loop until threshold
                number = 1
                r_sum, g_sum, b_sum = r, g, b
                if x > X - 1:  # Questionable idea. No definite conclusion yet
                    break
            else:
                medimage[y][cx(x)] = [r, g, b]

    for x in range(0, X, 1):
        r_sum, g_sum, b_sum = r, g, b = medimage[0][0]
        y_start = 0  # Defining start of inner loop until threshold
        number = 1
        for y in range(0, Y + y_overhead, 1):
            r, g, b = medimage[cy(y)][cx(x)]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_y) or (abs(g - (g_sum / number)) > threshold_y) or (abs(b - (b_sum / number)) > threshold_y) or (y == (Y - 1 + y_overhead)):
                for i in range(y_start, y - 1, 1):
                    resultimage[cy(i)][x] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                resultimage[cy(y)][x] = [r, g, b]
                y_start = y  # Redefining start of new inner loop until threshold
                number = 1
                r_sum, g_sum, b_sum = r, g, b
                if y > Y - 1:  # Questionable idea. No definite conclusion yet
                    break
            else:
                resultimage[cy(y)][x] = [r, g, b]

    # Protect alpha if exist
    if Z == 1 or Z == 3:
        return resultimage
    else:  # Copy source alpha
        resultimage_plus_alpha = [[[*resultimage[y][x], sourceimage[y][x][Z - 1]] for x in range(X)] for y in range(Y)]
        return resultimage_plus_alpha


if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
