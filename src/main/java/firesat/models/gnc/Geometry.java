package firesat.models.gnc;

import gov.nasa.jpl.aerie.contrib.models.Clock;
import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import java.io.InputStream;

import java.io.*;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Geometry {

  public final Double elevation = null;
  public final String spice_kernels_location = "/Users/mkumar/Documents/Aerie/mulit-mission-utilities-DSN/kernels/viewpr.tm";

  public final Register<Double> settable_elevation = Register.forImmutable(0.0);

  public Geometry(String file_path, Instant plan_start_time) {
    List<List<String>> records = new ArrayList<>();
    try (InputStream in = Geometry.class.getResourceAsStream(file_path)) {
      try (BufferedReader br = new BufferedReader(new InputStreamReader(in))) {
        String headLine = br.readLine();
        String line;
        while ((line = br.readLine()) != null) {
          String[] values = line.split("\t");
          records.add(Arrays.asList());

          Instant event_time = Instant.parse(values[0]);
          Double elevation = Double.parseDouble(values[1]);
          Double azimuth = Double.parseDouble(values[2]);

          Duration event_duration_since_plan_start = Duration.of(ChronoUnit.MICROS.between(plan_start_time, event_time), Duration.MICROSECONDS);
          ModelActions.defer(event_duration_since_plan_start, () -> ModelActions.replaying(() ->  settable_elevation.set(elevation)));

        }
      } catch (FileNotFoundException e) {
        throw new RuntimeException(e);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }



    } catch (IOException e) {
      throw new RuntimeException(e);
    }

  }



  public Geometry() {

    // ModelActions.spawn(); //create a task taht runs as sim runs
    //ModelActions.delay() //how I wait for delta b/w one line and the next

    //ModelActions.replaying() //-> wrap the lambda function in this so you use same thread as sim engine -> but you will literally replay everything if you stop w/ loops
    /*
    opt 1: create a task that reads csv and waits line by line (con: file handles open)
    opt 2: read entire csv file in -> what happens if you run out of csv file data?
     */

    //this goes in a task
//    for (line : csvfile)
      //read and set my register state

    List<List<String>> records = new ArrayList<>();
    try (BufferedReader br = new BufferedReader(new FileReader("firesat/models/gnc/data.csv"))) {
      String line;
      while ((line = br.readLine()) != null) {
        String[] values = line.split(",");
        records.add(Arrays.asList(values));
      }
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    } catch (IOException e) {
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
