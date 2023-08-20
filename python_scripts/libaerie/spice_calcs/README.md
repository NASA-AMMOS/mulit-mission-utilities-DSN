## Running al_el_vp.py
This script is currently set up to compute the azimuth, elevation, and view periods for multiple DSSs from the point of view of the spacecraft Europa-Clipper, between May 2nd, 2028 and May 5th, 2028.

### Computing Azimuth and Elevation for Multiple DSS and Viewing in the Aerie UI
1. Update the `al_el_vp.py` script as needed (see below).
2. Run the `al_el_vp.py` script. Comment out the `view_pr_driver(config)` line. (Running the script as is will result in both azimuth and elevation values being computed for DSN antennas, as well as View Periods being computed. For now, we only want to compute azimuth and elevation.) 
3. Build the jar.
4. Load jar into Aerie UI.
5. Simulate the plan in the UI.
6. View the azimuth and elevation resources in the timeline to ensure the data was computed and included in the jar.

### Computing View Period windows for Multiple DSS and Viewing View Period Activity Instances in the Aerie UI 
(This should be done after loading a jar into the UI.)
1. Comment out the `el_az_driver(config)` line in the script.
2. Update the script with the plan id. Make any configuration updates as needed (see below).
3. Run the `el_az_driver(config)` script
4. Simulate the plan in the UI.
5. View the View Period Activity instances to ensure the data was computed and posted.

### Configuration for Elevation and Azimuth Calculations
1. Update the `al_el_vp.py` script to reflect your mission's time format, plan start, and plan end.
2. Update the step size, which reflects the seconds between time steps for computations.
3. Update the `chosen_dss` list to reflect the stations for which you want to compute azimuth, elevation, or view periods.
4. Update the spacecraft ID
5. Update the plan ID (this can be determined using the UI).

### Additional Configuration for View Period Spice Geometry Finder
The Geometry Finder Spice functions compute the View Period for the specified DSSs and spacecraft. The parameters that can be updated are Spice parameters. The definitions and usage of the Spice functions in this script can be found here (note the python library, SpiceyPy was used in this script):
* [wninsd](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wninsd.html)
* [gfposc](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/gfposc)
* [wncard](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wncard)
* [wnfetd](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wnfetd)
* [timout](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/timout.html)
* [SPICEDOUBLE_CELL](https://spiceypy.readthedocs.io/en/v2.3.1/documentation.html#spiceypy.utils.support_types.SPICEDOUBLE_CELL)
