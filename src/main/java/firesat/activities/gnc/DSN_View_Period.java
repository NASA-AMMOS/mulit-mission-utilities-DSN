package firesat.activities.gnc;

import firesat.Mission;
import firesat.models.gnc.PassType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.ActivityType.EffectModel;
import gov.nasa.jpl.aerie.merlin.framework.annotations.Export.Parameter;

import gov.nasa.jpl.aerie.merlin.protocol.types.Duration;
import static gov.nasa.jpl.aerie.merlin.framework.ModelActions.delay;

@ActivityType("DSN_View_Period")
public class DSN_View_Period {
  @Parameter
  public String mission_name = "";

  @Parameter
  public String spacecraft_name = "";

  @Parameter
  public Integer NAIF_spacecraft_ID = 0;

  @Parameter
  public Integer dsn_spacecraft_ID = 0;

  @Parameter
  public String station_receive_time_UTC = "";

  @Parameter
  public Integer viewperiod_event  = 0;

  @Parameter
  public Integer station_identifier  = 0;

  @Parameter
  public Integer pass_number  = 0;

  @Parameter
  public Float azimuth_degrees  = 0f;

  @Parameter
  public Float elevation_degrees  = 0f;

  @Parameter
  public Float lha_X_degrees  = 0f;

  @Parameter
  public Float dec_Y_degrees  = 0f;

  @Parameter
  public Duration rtlt = Duration.HOUR;

  @EffectModel
  @ActivityType.ControllableDuration(parameterName = "rtlt")
  public void run(final Mission mission) {
    delay(rtlt);
  }
}
