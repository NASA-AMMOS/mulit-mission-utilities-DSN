@MissionModel(model = Mission.class)
@WithMappers(BasicValueMappers.class)
@WithConfiguration(Configuration.class)
@WithActivityType(DSN_Track.class)
@WithActivityType(DSN_View_Period.class)
@WithActivityType(DSN_View_Period_Duration.class)
package dsn;


import dsn.activities.DSN_Track;
import dsn.activities.DSN_View_Period;
import dsn.activities.DSN_View_Period_Duration;
import gov.nasa.jpl.aerie.contrib.serialization.rulesets.BasicValueMappers;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithActivityType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithConfiguration;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithMappers;
