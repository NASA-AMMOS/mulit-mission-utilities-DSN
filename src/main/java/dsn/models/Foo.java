package dsn.models;

import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import java.io.*;
import java.nio.file.Path;
import java.util.StringTokenizer;

public class Foo {

  public final Register<String> foo_string = Register.forImmutable("empty");
  public final Register<Double> foo_number_array = Register.forImmutable(0.0);

  public final Register<Double> foo_external_number = Register.forImmutable(0.0);

  public final Register<String> foo_external_string = Register.forImmutable("no val");

  public final Register<Double> ec_elevation = Register.forImmutable(0.0);

  public final Register<Double> ec_azimuth = Register.forImmutable(0.0);

  public Foo(Path path) {
    ModelActions.defer(Duration.HOUR, ModelActions.replaying(() -> foo_string.set("it's been an hour!")));

    double foo_data[] = new double[]{3.14, 1717, 1115, 57};
    for (int i=0; i < foo_data.length; i++) {
      double value = foo_data[i];
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_number_array.set(value)));
    }

    //InputStream input_data = this.getClass().getResourceAsStream("/data.json");
    // InputStream input_data = this.getClass().getResourceAsStream(path.toString());
    File initialFile = new File(path.toString());
    InputStream input_data = null;
    try {
      input_data = new FileInputStream(initialFile);
    } catch (FileNotFoundException e) {
      throw new RuntimeException(e);
    }
    BufferedReader reader = new BufferedReader(new InputStreamReader(input_data));


    String datum = "empty";
    double seconds_elapsed = 0.0;
    double elevation = 0.0;
    double azimuth = 0.0;

    int i = 0;
    while(true) {
      try {
        if (!reader.ready()) break;
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      try {
        //datum = reader.readLine();
        StringTokenizer tk = new StringTokenizer(reader.readLine());
        seconds_elapsed += Double.parseDouble(tk.nextToken());
        elevation = Double.parseDouble(tk.nextToken());
        azimuth = Double.parseDouble(tk.nextToken());
      } catch (IOException e) {
        throw new RuntimeException(e);
      }


      // caching
      Duration duration_elapsed = Duration.duration((long) seconds_elapsed,Duration.SECONDS);
      double finalElevation = elevation;
      ModelActions.defer(duration_elapsed, ModelActions.replaying(() -> ec_elevation.set(git )));

      double finalAzimuth = azimuth;
      ModelActions.defer(duration_elapsed, ModelActions.replaying(() -> ec_azimuth.set(finalAzimuth)));


      /*
      Double my_data = Double.parseDouble(datum);
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_external_number.set(my_data)));

      String finalDatum = datum;
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_external_string.set(finalDatum)));

      i++;*/
    }


  }






}
