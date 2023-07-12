package firesat.models.gnc;

import gov.nasa.jpl.aerie.contrib.models.Clock;
import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.contrib.models.SampledResource;
import gov.nasa.jpl.aerie.merlin.framework.Resource;
import gov.nasa.jpl.aerie.merlin.framework.resources.real.RealResource;
import gov.nasa.jpl.aerie.merlin.protocol.types.RealDynamics;
import spice.basic.CSPICE;
import spice.basic.SpiceErrorException;

public class Geometry {

  public final Double elevation = null;
  public final String spice_kernels_location = "/Users/mkumar/Documents/Aerie/mulit-mission-utilities-DSN/kernels/viewpr.tm";

  public Geometry() {
    try {
      CSPICE.furnsh(spice_kernels_location);
    } catch (SpiceErrorException e) {
      throw new RuntimeException(e);
    }
  }

  //we will use the SPICE call SPKCPO: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/spkcpo_c.html
  // Alternatively, you can use AZLCPO: https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/cspice/azlcpo_c.html
  //DSN 301k file: https://deepspace.jpl.nasa.gov/dsndocs/810-005/301/301K.pdf
  //DSN Station Locations: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/stations/earthstns_fx_201023.cmt
  public Double get_elevation(Clock utcClock) {

    //DSS-14 data cartesian coordiantes in ITRF93 ref frame:
    //DSS 14 70-m x: –2353621.420 y: –4641341.472 z" +3677052.318
    //DSS 14 70m     -2353621.420    -4641341.472    +3677052.318

    return 0.0;
  }

  public Geometry(final Clock utcClock) {
    Double elevation = utcClock.ticks.get();
    if (elevation > 5000) {
      elevation = 0.0;
    }
  }

  public Double updategeo(Clock utcClock){
    Double elevation = utcClock.ticks.get();
    return elevation*elevation;
  }


}
