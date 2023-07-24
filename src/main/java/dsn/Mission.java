package dsn;

import gov.nasa.jpl.aerie.contrib.models.Register;
import gov.nasa.jpl.aerie.contrib.serialization.mappers.StringValueMapper;
import gov.nasa.jpl.aerie.merlin.framework.Registrar;

import java.io.IOException;
import java.io.InputStream;

import static java.nio.charset.StandardCharsets.UTF_8;

public final class Mission {

  //public final Register<Double> foo = Register.forImmutable(0.0);


  public Mission(final Registrar registrar, final Configuration config) {
    //File myObj1 = new File(System.getProperty("user.dir"));
    //File myObj2 = new File(System.getProperty("~./data.json"));
    //File myObj2 = new File("../" + System.getProperty("user.dir"));
    //File myObj3 = new File(System.getProperty("../../" + "user.dir"));

    //Register<String> fooString = Register.forImmutable(System.getProperty("user.dir"));

    InputStream x = this.getClass().getResourceAsStream("/data.json");
    String y = "empty";
    try {
      y = new String(x.readAllBytes(), UTF_8);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    Register<String> fooString1 = Register.forImmutable(y);
    registrar.discrete("/fooString1", fooString1, new StringValueMapper());

   // Register<String> fooString1 = Register.forImmutable(myObj2.toString());
  //  Register<String> fooString2 = Register.forImmutable(myObj2.list().toString());
  //  Register<String> fooString3 = Register.forImmutable(myObj3.list().toString());
   // registrar.discrete("/foo", this.foo, new DoubleValueMapper());

 //   registrar.discrete("/fooString1", fooString2, new StringValueMapper());
   // registrar.discrete("/fooString1", fooString3, new StringValueMapper());


    //foo.set(myReader.nextDouble());
    //fooString.set("hi");

  }
}
