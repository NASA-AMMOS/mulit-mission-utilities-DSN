package dsn.models;

import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.merlin.framework.ModelActions;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

public class Foo {

  public final Register<String> foo_string = Register.forImmutable("empty");
  public final Register<Double> foo_number_array = Register.forImmutable(0.0);

  public final Register<Double> foo_external_number = Register.forImmutable(0.0);

  public final Register<String> foo_external_string = Register.forImmutable("no val");

  public Foo() {
    ModelActions.defer(Duration.HOUR, ModelActions.replaying(() -> foo_string.set("it's been an hour!")));

    double foo_data[] = new double[]{3.14, 1717, 1115, 57};
    for (int i=0; i < foo_data.length; i++) {
      double value = foo_data[i];
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_number_array.set(value)));
    }

    InputStream input_data = this.getClass().getResourceAsStream("/data.json");
    BufferedReader reader = new BufferedReader(new InputStreamReader(input_data));

    String datum = "empty";
    int i = 0;
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

      Double my_data = Double.parseDouble(datum);
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_external_number.set(my_data)));

      String finalDatum = datum;
      ModelActions.defer(Duration.HOUR.times(i+1), ModelActions.replaying(() -> foo_external_string.set(finalDatum)));

      i++;
    }


  }






}
