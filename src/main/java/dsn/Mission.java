package dsn;

import dsn.models.Az_El_Per_Station;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.DoubleValueMapper;
import gov.nasa.jpl.aerie.merlin.framework.Registrar;

public final class Mission {

  public Mission(final Registrar registrar, final Configuration config) {
    Az_El_Per_Station az_el_DSS_13 = new Az_El_Per_Station("/az_el_DSS-13.txt");
    Az_El_Per_Station az_el_DSS_14 = new Az_El_Per_Station("/az_el_DSS-14.txt");
    Az_El_Per_Station az_el_DSS_25 = new Az_El_Per_Station("/az_el_DSS-25.txt");
    Az_El_Per_Station az_el_DSS_26 = new Az_El_Per_Station("/az_el_DSS-26.txt");
    Az_El_Per_Station az_el_DSS_34 = new Az_El_Per_Station("/az_el_DSS-34.txt");
    Az_El_Per_Station az_el_DSS_65 = new Az_El_Per_Station("/az_el_DSS-65.txt");

    registrar.discrete("/DSS_13_Azimuth", az_el_DSS_13.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_13_Elevation", az_el_DSS_13.elevation, new DoubleValueMapper());

    registrar.discrete("/DSS_14_Azimuth", az_el_DSS_14.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_14_Elevation", az_el_DSS_14.elevation, new DoubleValueMapper());

    registrar.discrete("/DSS_25_Azimuth", az_el_DSS_25.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_25_Elevation", az_el_DSS_25.elevation, new DoubleValueMapper());

    registrar.discrete("/DSS_25_Azimuth", az_el_DSS_26.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_25_Elevation", az_el_DSS_26.elevation, new DoubleValueMapper());

    registrar.discrete("/DSS_25_Azimuth", az_el_DSS_34.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_25_Elevation", az_el_DSS_34.elevation, new DoubleValueMapper());

    registrar.discrete("/DSS_25_Azimuth", az_el_DSS_65.azimuth, new DoubleValueMapper());
    registrar.discrete("/DSS_25_Elevation", az_el_DSS_65.elevation, new DoubleValueMapper());

  }
}
