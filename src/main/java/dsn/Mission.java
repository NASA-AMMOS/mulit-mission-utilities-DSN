package dsn;

import dsn.models.Foo;
import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.DoubleValueMapper;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.StringValueMapper;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.framework.Registrar;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

public final class Mission {

  public final Register<Double> val_from_array = Register.forImmutable(0.0);

  public Mission(final Registrar registrar, final Configuration config) {

    Instant start = Instant.parse("2023-07-24T00:00:00.00Z");

  //  Geometry geometry = new Geometry(start);
    Foo foo = new Foo(config.path());

  //  registrar.discrete("/val_from_array", geometry.settable_value, new DoubleValueMapper());
  //  registrar.discrete("/set_string_val", geometry.settable_string_value, new StringValueMapper());


    double data[] = new double[]{3.14, 1717, 1115, 57};
    for (int i=0; i < data.length; i++) {
      Duration event_duration_since_plan_start = Duration.of(ChronoUnit.MICROS.between(start, start.plusSeconds(3600*i)), Duration.MICROSECONDS);
      int finalI = i;
      ModelActions.defer(event_duration_since_plan_start, () -> ModelActions.replaying(() -> val_from_array.set(data[finalI])));
    }

   // registrar.discrete("/set_array_number", val_from_array, new DoubleValueMapper());
   // registrar.discrete("/set_geo_number", geometry.settable_value, new DoubleValueMapper());
   // registrar.discrete("/set_geo_string", geometry.settable_string_value, new StringValueMapper());



    //registrar.discrete("/fooString1", geometry.fooString1, new StringValueMapper());
    registrar.discrete("/foo", foo.foo_string, new StringValueMapper());
    registrar.discrete("/foo_num", foo.foo_number_array, new DoubleValueMapper());

    registrar.discrete("/foo_external_number", foo.foo_external_number, new DoubleValueMapper());
    registrar.discrete("/foo_external_string", foo.foo_external_string, new StringValueMapper());

    registrar.discrete("/elevation", foo.ec_elevation, new DoubleValueMapper());
    registrar.discrete("/azimuth", foo.ec_azimuth,new DoubleValueMapper());
  }
}
