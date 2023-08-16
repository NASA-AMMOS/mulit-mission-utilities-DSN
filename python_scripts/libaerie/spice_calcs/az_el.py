import spiceypy
import spiceypy.utils.support_types as stypes
from datetime import datetime, timedelta
import numpy as np

spiceypy.furnsh("erotat.tm")

class python_dss_configuration:
	def __init__(self, time_format, start, end, step, chosen_dss, spacecraft):
		self.time_format = time_format
		self.start = start
		self.end = end
		self.step = step
		self.chosen_dss = chosen_dss
		self.spacecraft = spacecraft
		self.dss_data = {}

		for antenna in chosen_dss:
			self.dss_data[antenna] = dss_az_el_data()

	def print_az_el_data(self):
		for antenna in self.chosen_dss:
			file_name = "../../../src/main/resources/az_el_" + antenna + ".txt"
			#file = open(file_name, "w")

			data = self.dss_data[antenna]
			data_array = np.transpose(np.array([data.elapsed_seconds, data.az, data.el]))
			np.savetxt(file_name, data_array, fmt='%d')


class dss_az_el_data:
	def __init__(self):
		self.elapsed_seconds = []
		self.az = []
		self.el = []

	def add_data(self, elapsed_seconds, el, az):
		self.elapsed_seconds.append(elapsed_seconds)
		self.el.append(el)
		self.az.append(az)

# returns el and az of station as seen by Clipper in degrees
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

# takes the start and end UTC time as string as well as the step in seconds
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
	
def view_pr():
	MAXIVL = 1000
	MAXWIN = 2 * MAXIVL
	srfpt  = 'DSS-14'
	obsfrm = 'DSS-14_TOPO'
	target =  '-159'
	abcorr = 'CN+S'
	start  = '2028 MAY 2 TDB'
	stop   = '2028 MAY 6 TDB'
	elvlim =  6.0
	revlim = spiceypy.rpd() * elvlim
	crdsys = 'LATITUDINAL'
	coord  = 'LATITUDE'
	relate = '>'
	adjust = 0.0
	stepsz = 300.0
	etbeg = spiceypy.str2et( start )
	etend = spiceypy.str2et( stop  )

	cnfine = stypes.SPICEDOUBLE_CELL(2)
	spiceypy.wninsd( etbeg, etend, cnfine )
	riswin = stypes.SPICEDOUBLE_CELL( MAXWIN )
	spiceypy.gfposc( target, obsfrm, abcorr, srfpt,
	crdsys, coord,  relate, revlim,
	adjust, stepsz, MAXIVL, cnfine, riswin )

	result = spiceypy.gfposc(target, obsfrm, abcorr, srfpt,crdsys, coord,  
		relate, revlim,adjust, stepsz, MAXIVL, cnfine, riswin )
	print(riswin)

time_format = "%Y-%m-%dT%H:%M:%S.%f"
start = "2025-08-18T00:00:00.00"
end = "2026-08-18T00:00:00.00"
step_size = 3600
chosen_dss = ['DSS-13','DSS-14', 'DSS-25', 'DSS-26', 'DSS-34', 'DSS-65']
spacecraft = -159 	# -159 is Clipper

config = python_dss_configuration(time_format, start, end, step_size, chosen_dss, spacecraft)
#el_az_driver(config)
#config.print_az_el_data()
view_pr()