@MissionModel(model = Mission.class)
@WithMappers(BasicValueMappers.class)
@WithConfiguration(Configuration.class)
@WithActivityType(DSN_Track.class)
@WithActivityType(DSN_View_Period.class)
package firesat;


import firesat.activities.gnc.DSN_Track;
import firesat.activities.gnc.DSN_View_Period;
import gov.nasa.jpl.aerie.contrib.serialization.rulesets.BasicValueMappers;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithActivityType;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithConfiguration;
import gov.nasa.jpl.aerie.merlin.framework.annotations.MissionModel.WithMappers;
