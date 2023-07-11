package firesat.models.gnc;

import gov.nasa.jpl.aerie.contrib.models.Clock;
import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.contrib.models.SampledResource;
import gov.nasa.jpl.aerie.merlin.framework.Resource;
import gov.nasa.jpl.aerie.merlin.framework.resources.real.RealResource;
import gov.nasa.jpl.aerie.merlin.protocol.types.RealDynamics;

public class Geometry {

  public final Double elevation = null;

  public Geometry(final Clock utcClock) {
    Double elevation = utcClock.ticks.get();
    if (elevation > 5000) {
      elevation = -100.0;
    }
  }

  public Double updategeo(Clock utcClock){
    Double elevation = utcClock.ticks.get();
    if (elevation > 5000) {
      elevation = -100.0;
    }
    return elevation;
  }


}
