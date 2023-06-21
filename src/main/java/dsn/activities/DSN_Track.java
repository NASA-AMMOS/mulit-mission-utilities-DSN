package dsn.activities;

import dsn.Mission;
import dsn.models.PassType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType.EffectModel;
import gov.nasa.jpl.aerie.merlin.framework.annotations.Export.Parameter;

import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.delay;

@ActivityType("DSN_Track")
public class DSN_Track {
  @Parameter
  public String mission_name = "";

  @Parameter
  public String spacecraft_name = "";

  @Parameter
  public Integer NAIF_spacecraft_ID = 0;

  @Parameter
  public Integer dsn_spacecraft_ID = 0;

  @Parameter
  public PassType pass_type = PassType.TKG_PASS;

  @Parameter
  public String SOA = "";

  @Parameter
  public String BOT = "";

  @Parameter
  public String EOT = "";

  @Parameter
  public String EOA = "";

  @Parameter
  public String antenna_ID = "";

  @Parameter
  public Duration duration_of_activity = Duration.HOUR;

  @Parameter
  public String start_of_track = "";

  @Parameter
  public Duration duration_of_track = Duration.HOUR;

  @EffectModel
  @ActivityType.ControllableDuration(parameterName = "duration_of_activity")
  public void run(final Mission mission) {
    delay(duration_of_activity);
  }
}
