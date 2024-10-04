/*
POVRay include file
Description: Preset file for scene generated with stitch.py

    Isosurface like 2-strands thread.
    Highly detailed but extremely slow to render.
    Details require large rendering with high antialiaising to be seen in full.

    Largerly based on "Isosurface Tutorial" by Mike Williams
    https://povlab.online/isotutorial/

https://github.com/Dnyarri/POVmosaic
Read project help.html for options description.
Author: Ilya Razmanov, based on "Isosurface Tutorial" by Mike Williams
 {#008800, 0} */

#include "functions.inc"

#local R1 = 0.3;    // Strand thickness.
#local R2 = 0.2;    /* Overall thread thickness.
                         Increasing may require subsequent increase of contained_by box size below. */
#local R3 = 2.0;    // Torus major radius.
#local Strands = 2; // Strand number.

#local Turns = 8;   /* Number of helix turns in the loop.
                         Turns*Strands should be an integer to avoid a discontinuity  */

#local F1 = function {
    f_helix1(x,z,y, Strands, +Turns, R1, R2, 1, 0.8, -20)
}

#local thread = isosurface {
   function {F1(f_r(x,y,z)-R3, y, f_th(x,y,z))}
        max_gradient 2.3
        contained_by {box {<-3, -0.75, -0>, <3, 0.75, 3>}}
}

#declare thingie = object {thread scale <0.5, 0.7, 0.7>}  /* This is a good place 
to transform your object to fit {#880000, 0} */

#declare thingie_normal = normal {
    function{f_noise_generator(x, 64*y, z, 3)} // 3 is type of noise_generator for Perlin noise {#000088, 5}
    slope_map {  // [Input, <Height, Slope>]  {#006688, 3}
        [0      <0,     0.5>]
        [0.5    <0.2,   0.0>]
        [1      <0,     0.5>]
    }
  rotate <0, 0, -17>}

#declare thingie_finish = finish {phong 0.1 phong_size 1} // Dull, good color representation {#888800, 0}