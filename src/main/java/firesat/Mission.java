package firesat;

import firesat.models.gnc.Geometry;
import firesat.models.gnc.GncControlMode;
import gov.nasa.jpl.aerie.contrib.models.Accumulator;
import gov.nasa.jpl.aerie.contrib.models.Clock;
import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.contrib.models.SampledResource;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.DoubleValueMapper;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.framework.Registrar;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import spice.basic.CSPICE;
import spice.basic.SpiceErrorException;

import java.io.FileReader;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicReference;


import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.spawn;

public final class Mission {
  public final Register<GncControlMode> gncControlMode = Register.forImmutable(GncControlMode.THRUSTERS);
  public final Clock utcClock  = new Clock(Instant.parse("2023-08-18T00:00:00.00Z"));



  //first instant is the time
  //then do instant.plus


  public final Accumulator seconds = new Accumulator(0, 1000);
  Geometry geo = new Geometry();

  public final Register<Double> elevation = Register.forImmutable(0.0);
 // public final SampledResource<Double> elevation_sampled = new SampledResource<>(() -> this.geo.elevation);

  public final SampledResource<Double> el = new SampledResource<>(() -> geo.updategeo(utcClock), $-> $, 100000.0);


  public final Register<Double> favorite_number = Register.forImmutable(get_et());




  public Double get_et() {

    double et = 0.0;
    try {
      CSPICE.furnsh("/Users/mkumar/Documents/Aerie/mulit-mission-utilities-DSN/kernels/dsn/moon_example/erotat.tm");
    } catch (SpiceErrorException e) {
      throw new RuntimeException(e);
    }
    String timestr = "2023-08-18T00:00:00.00";
    try {
      et = CSPICE.str2et(timestr);
    } catch (SpiceErrorException e) {
      throw new RuntimeException(e);
    }

    return et;
  }

  public Mission(final Registrar registrar, final Configuration config) {
    registrar.real("/utcClock", this.utcClock.ticks);
    registrar.real("/seconds", this.seconds);
    registrar.discrete("/elevation", this.elevation, new DoubleValueMapper());
    registrar.discrete("/el", this.el, new DoubleValueMapper());
    registrar.discrete("/favorite_number", this.favorite_number, new DoubleValueMapper());
    registrar.discrete("/settable_elevation", this.geo.settable_elevation, new DoubleValueMapper());



    //ModelActions.defer(10, ()-> gncControlMode.set(GncControlMode.REACTION_WHEELS));



    /*
    AtomicReference<Double> i = new AtomicReference<>(0.0);
    spawn(() -> { // Register a never-ending daemon task
      while (true) {
        ModelActions.delay(Duration.SECOND);
        this.elevation.set(geo.updategeo(this.utcClock));
      }
    });*/
    //el = new SampledResource<>();
  }




}
