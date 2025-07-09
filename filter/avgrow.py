#!/usr/bin/env python3

'''
Averaging image pixels in a row until reaching abs(average - input) threshold, then repeating in a column.

Created by: `Ilya Razmanov <https://dnyarri.github.io/>`_

History:
---------

0.10.12.3   Initial version - 12 Oct 2024. RGB only.

0.10.13.2   Forces RGB, skips alpha. Changed threshold condition to r, g, b separately. Seem to be just what I need.

0.10.25.1   Bugfix for tiny objects.

1.16.5.10   Modularization, some optimization. Force keep alpha.

'''

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2024-2025 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.17.9.17'
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


def filter(sourceimage: list[list[list[int]]], threshold_x: int, threshold_y: int) -> list[list[list[int]]]:
    """Average image pixels in a row until borderline threshold met, then repeat in a column."""

    Y = len(sourceimage)
    X = len(sourceimage[0])
    Z = len(sourceimage[0][0])

    # Creating empty RGB intermediate image
    medimage = create_image(X, Y, 3)

    # Creating empty RGB final image
    resultimage = create_image(X, Y, 3)

    for y in range(0, Y, 1):
        if Z > 2:
            r_sum, g_sum, b_sum = r, g, b = sourceimage[0][0][0:3]
        else:
            r_sum = g_sum = b_sum = r = g = b = sourceimage[0][0][0]
        x_start = 0
        number = 1
        for x in range(0, X, 1):
            if Z > 2:
                r, g, b = sourceimage[y][x][0:3]
            else:
                r = g = b = sourceimage[y][x][0]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_x) or (abs(g - (g_sum / number)) > threshold_x) or (abs(b - (b_sum / number)) > threshold_x):
                for i in range(x_start, x - 1, 1):
                    medimage[y][i] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                medimage[y][x] = [r, g, b]
                x_start = x
                number = 1
                r_sum, g_sum, b_sum = r, g, b
            else:
                medimage[y][x] = [r, g, b]

    for x in range(0, X, 1):
        r_sum, g_sum, b_sum = r, g, b = medimage[0][0]
        y_start = 0
        number = 1
        for y in range(0, Y, 1):
            r, g, b = medimage[y][x]
            number += 1
            r_sum += r
            g_sum += g
            b_sum += b
            if (abs(r - (r_sum / number)) > threshold_y) or (abs(g - (g_sum / number)) > threshold_y) or (abs(b - (b_sum / number)) > threshold_y):
                for i in range(y_start, y - 1, 1):
                    resultimage[i][x] = [int(r_sum / number), int(g_sum / number), int(b_sum / number)]
                resultimage[y][x] = [r, g, b]
                y_start = y
                number = 1
                r_sum, g_sum, b_sum = r, g, b
            else:
                resultimage[y][x] = [r, g, b]

    # Protect alpha if exist
    if Z == 1 or Z == 3:
        return resultimage
    else:  # Copy source alpha
        resultimage_plus_alpha = [
                        [
                            [*resultimage[y][x], sourceimage[y][x][Z-1]] for x in range(X)
                        ] for y in range(Y)
                    ]
        return resultimage_plus_alpha

if __name__ == '__main__':
    print('Module to be imported, not run as standalone')
