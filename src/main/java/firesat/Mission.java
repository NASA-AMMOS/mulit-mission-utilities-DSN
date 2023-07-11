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

import java.time.Instant;
import java.util.concurrent.atomic.AtomicReference;

import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.spawn;

public final class Mission {
  public final Register<GncControlMode> gncControlMode = Register.forImmutable(GncControlMode.THRUSTERS);
  public final Clock utcClock  = new Clock(Instant.parse("2023-08-18T00:00:00.00Z"));

  public final Accumulator seconds = new Accumulator(0, 1000);
  Geometry geo = new Geometry(utcClock);

  public final Register<Double> elevation = Register.forImmutable(0.0);
 // public final SampledResource<Double> elevation_sampled = new SampledResource<>(() -> this.geo.elevation);

  public final SampledResource<Double> el = new SampledResource<>(() -> geo.updategeo(utcClock), $-> $, 10.0);

  public Mission(final Registrar registrar, final Configuration config) {
    registrar.real("/utcClock", this.utcClock.ticks);
    registrar.real("/seconds", this.seconds);
    registrar.discrete("/elevation", this.elevation, new DoubleValueMapper());
    registrar.discrete("/el", this.el, new DoubleValueMapper());

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
