package dsn.activities;

import dsn.Mission;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.delay;

@ActivityType("Scheduled_Activity")
public class Scheduled_Activity {

  @ActivityType.EffectModel
  public void run(final Mission mission) {
    delay(Duration.HOUR);
  }
}
