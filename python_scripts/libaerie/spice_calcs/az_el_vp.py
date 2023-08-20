import spiceypy
import spiceypy.utils.support_types as stypes
from datetime import datetime, timedelta
import numpy as np
import json
import requests

spiceypy.furnsh("erotat.tm")

class python_dss_configuration:
	def __init__(self, time_format, start, end, step, chosen_dss, spacecraft, plan_id):
		self.time_format = time_format
		self.start = start
		self.end = end
		self.step = step
		self.chosen_dss = chosen_dss
		self.spacecraft = spacecraft
		self.dss_data = {}
		self.plan_id = plan_id

		for antenna in chosen_dss:
			self.dss_data[antenna] = dss_az_el_data()

	def print_az_el_data(self):
		for antenna in self.chosen_dss:
			file_name = "../../../src/main/resources/az_el_" + antenna + ".txt"

			data = self.dss_data[antenna]
			data_array = np.transpose(np.array([data.elapsed_seconds, data.az, data.el]))
			np.savetxt(file_name, data_array, fmt='%1.6f')

class dss_az_el_data:
	def __init__(self):
		self.elapsed_seconds = []
		self.az = []
		self.el = []

	def add_data(self, elapsed_seconds, el, az):
		self.elapsed_seconds.append(elapsed_seconds)
		self.el.append(el)
		self.az.append(az)

def el_az_computer(utc_timestr: str, stations: list, spacecraft: str, dss_data, elapsed_seconds:float):
	'''Computes azimuth and elevation of DSN from S/C p.o.v. for a given UTC time

	Args:
		utc_timestr: UTC time in string format
		stations: List of DSN antennas
	Returns:
		List containing time stamp, and azimuth and elevation data for every DSS
	Raises:
		Nothing
	'''

	# 1. Convert time string in UTC to double precision seconds past J2000 (Ephemeris Time -> ET)
	et = spiceypy.str2et(utc_timestr)

	# 2. Find azimuth and elevation of Europa-Clipper in local topocentric reference frame at DSN station DSS-13
	for antenna in stations:
		[topov, ltime] = spiceypy.spkpos(spacecraft, et, antenna+'_TOPO','lt+s', antenna)

		# 3.Express the station-Clipper direction in terms of longitude and latitude in the DSS-13_TOPO frame.
		[r, lon, lat] = spiceypy.reclat(topov)

		# 4. Convert to azimuth-elevation.
		az = -lon
		if  az < 0.0:
		  az += spiceypy.twopi()

		el = lat

		# 5. Append data to object
		dss_data[antenna].add_data(elapsed_seconds,el*spiceypy.dpr(), az*spiceypy.dpr())

		#result.extend([el*spiceypy.dpr(), az*spiceypy.dpr()])

	return

def el_az_driver(config):
	''' Prints azimuth and elevation data out to file

	Args:
		start: UTC start time
		end: UTC end time
		step_size: Desired time-step between az and el calcs in seconds
		stations: List of DSN antennas
	Returns:
		Nothing

	Raises:
		Nothing
	'''

	# Convert to datetime
	start_time = datetime.strptime(config.start, config.time_format)
	end_time = datetime.strptime(config.end, config.time_format)
	this_step = start_time

	while (this_step < end_time):
		elapsed_seconds = (this_step - start_time).total_seconds()
		results = el_az_computer(this_step.strftime(time_format), config.chosen_dss, str(config.spacecraft), config.dss_data, elapsed_seconds)
		this_step += timedelta(seconds = config.step)
	return

def view_pr_driver(config):
	view_pr(config)

def post_view_pr(view_pr_acts):
	'''
	Posts VP activities generated to the plan UI
	'''
	api_url = 'http://localhost:8080/v1/graphql' # https://aerie-dev.jpl.nasa.gov:8080/v1/graphql
	query = '''mutation InsertActivities($activities: [activity_directive_insert_input!]!) {insert_activity_directive(objects: $activities) {returning {id name } } } '''

	response = requests.post(
		url=api_url,
		json={
		'query': query,
		 'variables': { "activities": view_pr_acts },
		},
		verify=False
		)

	print("SENT:")
	print(view_pr_acts)

	print("RESPONSE")
	print(json.dumps(response.json(), indent=2))
	
def view_pr(config):
	'''
	Computes View Periods using Spice geometry finder
	Tutorial on geometry finder and view periods: https://spiceypy.readthedocs.io/en/main/event_finding.html#find-view-periods
	'''

	# Configuration Params
	plan_start = datetime.strptime(config.start, config.time_format)
	plan_id = config.plan_id


	# Variables related to Spce
	stations = config.dss_data
	MAXIVL = 10
	MAXWIN = 2 * MAXIVL
	target =  '-159'
	abcorr = 'CN+S'
	start  = '2028 MAY 2'
	stop   = '2028 MAY 6'
	elvlim =  6.0
	revlim = spiceypy.rpd() * elvlim
	TDBFMT = 'YYYY MM DD HR:MN:SC.###'
	date_format = '%Y %m %d %H:%M:%S.%f'
	crdsys = 'LATITUDINAL'
	coord  = 'LATITUDE'
	relate = '>'
	adjust = 0.0
	stepsz = 300.0
	etbeg = spiceypy.str2et(start)
	etend = spiceypy.str2et(stop)

	cnfine = stypes.SPICEDOUBLE_CELL(2)
	view_pr_acts = []

	for antenna in stations:

		srfpt  = antenna
		obsfrm = antenna+'_TOPO'

		spiceypy.wninsd( etbeg, etend, cnfine )
		riswin = stypes.SPICEDOUBLE_CELL( MAXWIN )
		spiceypy.gfposc( target, obsfrm, abcorr, srfpt,
		crdsys, coord,  relate, revlim,
		adjust, stepsz, MAXIVL, cnfine, riswin )

		result = spiceypy.gfposc(target, obsfrm, abcorr, srfpt,crdsys, coord,  
			relate, revlim,adjust, stepsz, MAXIVL, cnfine, riswin )

		winsiz = spiceypy.wncard(riswin)

		if winsiz == 0:
			print( 'No events were found.' )
		else:
			print('Visibility times of {0:s} as seen from {1:s}:\n'.format(target,srfpt))

		for i in range(winsiz):
			# Fetch the start and stop times of
			# the ith interval from the search result
			# window riswin.
			[intbeg, intend] = spiceypy.wnfetd(riswin, i)

			#
			# Convert the rise time to a TDB calendar string.
			#
			timestr1 = spiceypy.timout(intbeg, TDBFMT)
			timestr2 = spiceypy.timout(intend, TDBFMT)
			activity_start = datetime.strptime(timestr1, date_format)
			activity_end = datetime.strptime(timestr2, date_format)

			elapsed_seconds_since_activity_start = timedelta.total_seconds(activity_start-plan_start)
	

			activity_duration = timedelta.total_seconds(activity_end-activity_start)
			activity_duration = activity_duration*1000000;
			activity_duration = int(activity_duration)
			activity_name = antenna + " View Period"

			print(activity_duration)

			print(f"start: {timestr1}")
			print(f"end: {timestr2}\n")
			activity_data = {
				'arguments' : {'spacecraft_ID':-159, 'station_identifier':int(antenna[4:]), 'duration': activity_duration},
				'plan_id' : 114,
				'name' : activity_name,
				'start_offset': str(elapsed_seconds_since_activity_start),
				'type': 'DSN_View_Period_Duration'
			}
			view_pr_acts.append(activity_data)

	post_view_pr(view_pr_acts)


time_format = "%Y-%m-%dT%H:%M:%S.%f"
start = "2028-05-02T00:00:00.00"
end = "2028-05-06T00:00:00.00"
step_size = 60
chosen_dss = ['DSS-13','DSS-14', 'DSS-25', 'DSS-26', 'DSS-34', 'DSS-65']
spacecraft = -159 	# -159 is Clipper
plan_id = 114

config = python_dss_configuration(time_format, start, end, step_size, chosen_dss, spacecraft, plan_id)

# FOR ELEVATION AND AZIMUTH
el_az_driver(config)
config.print_az_el_data()

# FOR VIEW PERIODS
view_pr_driver(config)



