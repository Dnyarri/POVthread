"""
==============
POV-Ray Thread
==============
-----------------------------------------------------
Converting image textile simulation in POV-Ray format
-----------------------------------------------------

Export module present function for converting images
and image-like nested lists to an assembly of 3D objects,
colored after source pixels, and forming a simulation of textile.

Objects may be displaced when rendering, based on POV-Ray internal
Perlin noise, simulating base canvas deformation.

----
Main site: `The Toad's Slimy Mudhole`_

.. _The Toad's Slimy Mudhole: https://dnyarri.github.io

`POV-Ray Thread`_ previews and description

.. _POV-Ray Thread: https://dnyarri.github.io/povthread.html

POV-Ray Thread Git repositories: main `@Github`_ and mirror `@Gitflic`_

.. _@Github: https://github.com/Dnyarri/POVthread

.. _@Gitflic: https://gitflic.ru/project/dnyarri/povthread

"""

# History:
# --------
# ca. 2007 AD   General idea illustration for Kris Zaklika.
# 1.10.4.1      Initial public release of Python version.
# 1.16.6.2      Modularization.
# 1.22.1.11     Acceleration, numerous internal changes.

__author__ = 'Ilya Razmanov'
__copyright__ = '(c) 2007-2026 Ilya Razmanov'
__credits__ = 'Ilya Razmanov'
__license__ = 'unlicense'
__version__ = '1.32.8.24'
__maintainer__ = 'Ilya Razmanov'
__email__ = 'ilyarazmanov@gmail.com'
__status__ = 'Production'
