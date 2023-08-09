import spiceypy
import datetime

dsn_pck_location = "dsn/earthstns_itrf93_201023.bsp"
spiceypy.furnsh("/Users/mkumar/Documents/Aerie/mulit-mission-utilities-DSN/kernels/dsn/moon_example/erotat.tm")

# 0. Load kernels
#spiceypy.furnsh(dsn_pck_location)

# 1. Convert time string in UTC to double precision seconds past J2000 (Ephemeris Time -> ET)
timestr = '2007 JAN 1 00:00:00Z' # not ok
timestr = '2007 JAN 1 00:00:00' # ok
timestr = "2025-08-18T00:00:00.00"

et     = spiceypy.str2et(timestr)
print(et)
# 2. Find azimuth and elevation of
# Find the azimuth and elevation of apparent
# position of the Moon in the local topocentric
# reference frame at the DSN station DSS-13.
# First look up the Moon's position relative to the
# station in that frame.
# -159 is clipper
[topov, ltime] = spiceypy.spkpos( '-159', et, 'DSS-13_TOPO',
                                  'lt+s', 'DSS-13')

# Express the station-moon direction in terms of longitude
# and latitude in the DSS-13_TOPO frame.
#
[r, lon, lat] = spiceypy.reclat( topov )

#
# Convert to azimuth-elevation.
#
az = -lon

if  az < 0.0:
  az += spiceypy.twopi()

el = lat

print( 'DSS-13-Clipper az/el using high accuracy '
       'PCK and DSS-13_TOPO frame:\n'
       'Clipper Az (deg):        {0:15.6f}\n'
       'Clipper El (deg):        {1:15.6f}\n'.format(
  az * spiceypy.dpr(),
  el * spiceypy.dpr() )  )



def get_el_az(start, finish, delta):
  timestr = start
  while timestr <= finish:
    et = spiceypy.str2et(timestr)
    [topov, ltime] = spiceypy.spkpos( '-159', et, 'DSS-13_TOPO',
                                      'lt+s', 'DSS-13')
    [r, lon, lat] = spiceypy.reclat( topov )
    az = -lon
    if  az < 0.0:
      az += spiceypy.twopi()
    el = lat

    #write out to csv


  return


