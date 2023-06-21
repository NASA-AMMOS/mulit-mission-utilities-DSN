package gradle.test;

import dsn.activities.gnc.GncChangeControlMode;
import dsn.generated.activities.gnc.GncChangeControlModeMapper;
import org.junit.jupiter.api.Test;

class GncChangeControlModeTest {
  private final GncChangeControlModeMapper mapper;

  public GncChangeControlModeTest() {
    this.mapper = new GncChangeControlModeMapper();
  }

  @Test
  public void testDefaultSerializationDoesNotThrow() {
    this.mapper.getInputType().getArguments(new GncChangeControlMode());
  }
}
