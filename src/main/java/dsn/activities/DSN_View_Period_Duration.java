package dsn.activities;

import dsn.Mission;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.Export.Parameter;
import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;

import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.delay;

@ActivityType("DSN_View_Period_Duration")
public class DSN_View_Period_Duration {

  @Parameter
  public String mission_name = "";

  @Parameter
  public String spacecraft_name = "";

  @Parameter
  public Integer NAIF_spacecraft_ID = 0;

  @Parameter
  public Integer dsn_spacecraft_ID = 0;

  @Parameter
  public Integer station_identifier  = 0;

  @Parameter
  public Integer pass_number  = 0;

  @Parameter
  public Duration duration;

  @ActivityType.EffectModel
  @ActivityType.ControllableDuration(parameterName = "duration")
  public void run(final Mission mission) {
    delay(duration);
  }
}
