package dsn.models;

import gov.nasa.jpl.aerie.contrib.models.Register;

import java.time.Instant;

public class Geometry {
  public final Register<Double> settable_value = Register.forImmutable(0.0);
  public final Register<String> settable_string_value = Register.forImmutable("empty");
  public final Register<String> fooString1 = Register.forImmutable("empty");

  public Geometry(Instant start) {

    /*
    double data[] = new double[]{3.14, 1717, 1115, 57};
    for (int i=0; i < data.length; i++) {
      Duration event_duration_since_plan_start = Duration.of(ChronoUnit.MICROS.between(start, start.plusSeconds(3600*i)), Duration.MICROSECONDS);
      int finalI = i;
      ModelActions.defer(event_duration_since_plan_start, () -> ModelActions.replaying(() -> settable_value.set(data[finalI])));
    } */

/*
    InputStream input_data = this.getClass().getResourceAsStream("/data.json");
    BufferedReader reader = new BufferedReader(new InputStreamReader(input_data));

    String datum = "empty";
    int i = 1;
    while(true) {

      try {
        if (!reader.ready()) break;
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
      try {
        datum = reader.readLine();
      } catch (IOException e) {
        throw new RuntimeException(e);
      }

      Duration event_duration_since_plan_start = Duration.of(ChronoUnit.MICROS.between(start, start.plusSeconds(3600*i)), Duration.MICROSECONDS);

      Double my_data = Double.parseDouble(datum);
      ModelActions.defer(event_duration_since_plan_start, () -> ModelActions.replaying(() -> settable_value.set(my_data)));

      String finalDatum = datum;
      ModelActions.defer(event_duration_since_plan_start, () -> ModelActions.replaying(() -> settable_string_value.set(finalDatum)));

      i++;
    }


    InputStream x = this.getClass().getResourceAsStream("/data.json");
    String y = "empty";
    try {
      y = new String(x.readAllBytes(), UTF_8);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    Register<String> fooString1 = Register.forImmutable(y);



    ModelActions.defer(Duration.HOUR, ModelActions.replaying(() -> fooString1.set("HAHA")));
  //  fooString1.set("hahahha");

*/
  }

}
