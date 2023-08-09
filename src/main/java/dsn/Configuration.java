package dsn;

import java.nio.file.Path;

import static gov.nasa.jpl.aerie.merlin.framework.annotations.Export.Template;

public record Configuration(Path path) {
  public static @Template Configuration defaultConfiguration() {
    return new Configuration(Path.of(""));
  }
}
