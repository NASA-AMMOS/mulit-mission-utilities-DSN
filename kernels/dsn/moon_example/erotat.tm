KPL/MK

Meta-kernel for the "Earth Rotation" task
in the Binary PCK Hands On Lesson.

The names and contents of the kernels referenced by this
meta-kernel are as follows:

File name                                           Contents
------------------------------                      ---------------------------------
naif00012.tls                                       Generic LSK
de440_2020_2040.bsp                                 Solar System Ephemeris # we don't need this anymore, still reading in (2020-2040)
23F01_V1_PD2_scpse_MP.bsp                           Europa Clipper Ephemeris 2031 JUN 10 22:33:41.164            2035 MAY 16 06:48:03.009
21F31_MEGA_L241030_A300411_LP21_V4_scpse_MP.bsp     Europa Clipper Ephemeris 2024 OCT 29 21:21:49.256            2034 SEP 03 05:04:02.415
earthstns_itrf93_050714.bsp                         DSN station Ephemeris 1950 to 2050
earth_topo_201023.tf                                Earth topocentric FK
pck00010.tpc                                        NAIF text PCK
earth_070425_370426_predict.bpc                     Earth binary PCK predict 2007 to 2037


\begindata

KERNELS_TO_LOAD = ( 'kernels/lsk/naif0012.tls'
                    'kernels/spk/de440_2020_2040.bsp'
                    'kernels/spk/21F31_MEGA_L241030_A300411_LP21_V4_scpse_MP.bsp'
                    'kernels/spk/23F01_V1_PD2_scpse_MP.bsp'
                    'kernels/spk/earthstns_itrf93_050714.bsp '
                    'kernels/fk/earth_topo_201023.tf'
                    'kernels/pck/pck00010.tpc'
                    'kernels/pck/earth_070425_370426_predict.bpc' )

\begintext

