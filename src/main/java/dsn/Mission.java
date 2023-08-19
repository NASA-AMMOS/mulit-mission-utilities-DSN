package dsn;

import dsn.models.Az_El_Per_Station;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.DoubleValueMapper;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.StringValueMapper;
import gov.nasa.jpl.aerie.merlin.framework.Registrar;

public final class Mission {

  public Mission(final Registrar registrar, final Configuration config) {
    Az_El_Per_Station az_el_DSS_13 = new Az_El_Per_Station("/az_el_DSS-13.txt");
    registrar.discrete("/DSS_13_Azimuth", az_el_DSS_13.azimuth, new DoubleValueMapper());
    registrar.discrete("/my_path", az_el_DSS_13.my_path, new StringValueMapper());
  }
}
