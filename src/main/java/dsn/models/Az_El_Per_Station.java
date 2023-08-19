package dsn.models;

import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import java.io.*;
import java.util.StringTokenizer;


public class Az_El_Per_Station {
  public final Register<Double> elevation = Register.forImmutable(0.0);
  public final Register<Double> azimuth = Register.forImmutable(0.0);

  public final Register<String> my_path = Register.forImmutable("");

  public Az_El_Per_Station(String path) {

    InputStream inputData = this.getClass().getResourceAsStream("/az_el_DSS-13.txt");
    BufferedReader reader = new BufferedReader(new InputStreamReader(inputData));

    String datum = "empty";
    double secondsElapsed = 0.0;
    double elevationFromFile = 0.0;
    double azimuthFromFile = 0.0;

    while(true) {
      try {
        if(!reader.ready()) break;
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      try {
        datum = reader.readLine();
        StringTokenizer tk = new StringTokenizer(reader.readLine());
        secondsElapsed += Double.parseDouble(tk.nextToken());
        azimuthFromFile = Double.parseDouble(tk.nextToken());
        elevationFromFile = Double.parseDouble(tk.nextToken());
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }

    Duration durationElapsed = Duration.duration((long) secondsElapsed, Duration.SECONDS);
    double finalElevation = elevationFromFile;
    double finalAzimuth = azimuthFromFile;

    ModelActions.defer(durationElapsed, ModelActions.replaying(() -> elevation.set(finalElevation)));
    ModelActions.defer(durationElapsed, ModelActions.replaying(() -> azimuth.set(finalAzimuth)));
  }

}
