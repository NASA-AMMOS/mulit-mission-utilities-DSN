# Instructions for Building Aerie Mission Model Template and DSN Multi-Mission Utilities and Using DSN Scripts

Click [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN#aerie-mission-model-template-installation-building-and-testing-instructions) for Aerie Mission Model Template Installation, Building, and Testing Instructions.

Click [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN#dsn-multi-mission-utilities-installation-building-and-testing-instructions) for DSN Multi Mission Utilities Installation, Building, and Testing Instructions. 

Click [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN#running-dsn-multi-mission-utilities-import_activitiespy) for DSN Multi-Mission Utilities SAF and VP Export and Import Python script instructions.

Click [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN#computing-aziumuth-and-elevation-using-dsn-multi-mission-utilities) for DSN Multi-Mission Utilities azimuth and elevation Python script instructions. 

# Aerie Mission Model Template Installation, Building, and Testing Instructions

This repo provides an Aerie mission model template for a fictitious mission called [FireSat](http://www.sme-smad.com/). It is meant as a starting point for building a new mission model in Aerie.

### Prerequisites for Aerie Mission Model Template

- Install [OpenJDK Temurin LTS](https://adoptium.net/temurin/releases/?version=19). If you're on macOS, you can install [brew](https://brew.sh/) instead and then use the following command to install JDK 19:

  ```sh
  brew install --cask temurin19
  ```

  Make sure you update your `JAVA_HOME` environment variable. For example with [Zsh](https://www.zsh.org/) you can update your `.zshrc` with:

  ```sh
  export JAVA_HOME="/Library/Java/JavaVirtualMachines/temurin-19.jdk/Contents/Home"
  ```

- Set `GITHUB_USER` and `GITHUB_TOKEN` environment variables to your credentials (first you need to create a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic) in your GitHub account) so you can download the Aerie Maven packages from the [GitHub Maven package registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry). For example with Zsh you can update your `.zshrc` to set the variables with:

  ```sh
  export GITHUB_USER=""
  export GITHUB_TOKEN=""
  ```

### Building Aerie Mission Model Template

To build a mission model JAR you can do:

```sh
./gradlew build --refresh-dependencies # Outputs 'build/libs/dsn.jar'
```

You can then upload the JAR to Aerie using either the UI or API. If you want to just try the model without building it yourself you can [download it here](./firesat.jar).

### Testing Aerie Mission Model Template

To run unit tests under [./src/test](./src/test) against your mission model you can do:

```sh
./gradlew test
```

# DSN Multi Mission Utilities Installation, Building, and Testing Instructions
This repo provides DSN multi-mission utilities. It provides a prototype of geometric computations for View Periods, and the ingestion and export of SAF and VP files. 

### Prerequisites for DSN Multi-Mission Utilities Development
- Install venv for Python 3.9+ and setup a new virtual enviornment in this directory.

```sh
cd mulit-mission-utilities-DSN/python_scripts
python3 -m venv .venv
```

- Activate Virtual Environment for Python project

```sh
source .venv/bin/activate
```

- Install project dependencies

```sh
pip3 install -r requirements.txt
```

### Running DSN Multi-Mission Utilities Tests

- Activate Virtual Environment

```sh
source .venv/bin/activate
```

- Run PyTests to automatically setup tests in ./tests directory

```sh
pytest
```

### Installing and packaging DSN Multi-Mission Utilities libraries
- PIP can be used with the setup.py script to install libaerie system-wide.
- Python build can be used to create a PyPi compliant package for upload to a python mirror

### Installation of DSN Multi-Mission Utilities libraries scripts

```sh
pip3 install -e
```

### Packaging of DSN Multi-Mission Utilities 

```sh
python3 -m build
```

# Running DSN Multi-Mission Utilities import_activities.py

import_activities.py can scan DSN View Period and DSN Station Allocation files and add them activities in an existing Aerie Installation.

```sh
python3 import_activities.py --help
usage: import_activities.py [-h] [-p VP] [-s SA] [-a CONNECTION_STRING] [-b BUFFER] [-v VERBOSE] plan_id

positional arguments:
  plan_id               plan ID to ingest activity directives into

options:
  -h, --help            show this help message and exit
  -p VP, --vp_file VP   Filepath to a DSN View Period file
  -s SA, --sa_file SA   Filepath to a DSN Station Allocation file
  -a CONNECTION_STRING, --connection_string CONNECTION_STRING
                        http://<ip_address>:<port> connection string to graphql database
  -b BUFFER, --buffer_length BUFFER
                        Integer length of the buffer used to parse products, use if parsing large files
  -v VERBOSE, --verbose VERBOSE
                        Increased debug output
```

### Example runs:
- ```python3 import_activities.py 25 -p INPUT.VP -s INPUT.SAF # Ingesting one file of each type```
- ```python3 import_activities.py 25 -p INPUT1.VP -p INPUT2.VP # Ingesting multiple files of one type```
- ```python3 import_activities.py 25 -p ./INPUT1.VP -p ./INPUT2.VP -s ./INPUT1.SAF -s ./INPUT2.SAF -b 500 # Ingesting multiple files of both types inserting 500 activities at a time```

It's recommended to set the -b option to a value less then 1000 as a large amount of event data can stress GraphQL


### Running DSN Multi-Mission Utilities export_activities.py

export_activities.py can read an Aerie plan and will write the activities to a single DSN View Period and DSN Station Allocation files.

```sh
python3 export_activities.py --help
usage: export_activities.py [-h] [-p VP] [-s SA] [-m MISSION_NAME] [-S SPACECRAFT_NAME] [-d DSN_ID] [-a CONNECTION_STRING] [-b BUFFER] [-v VERBOSE] plan_id

positional arguments:
  plan_id               plan ID to ingest activity directives into

options:
  -h, --help            show this help message and exit
  -p VP, --vp_file VP   Filepath to export target DSN View Period file
  -s SA, --sa_file SA   Filepath to export target DSN Station Allocation file
  -m MISSION_NAME, --mission_name MISSION_NAME
                        Mission Name for VP and SAF header
  -S SPACECRAFT_NAME, --spacecraft_name SPACECRAFT_NAME
                        Spacecraft Name for VP and SAF header
  -d DSN_ID, --dsn_id DSN_ID
                        Integer DSN spacecraft number for VP and SAF header
  -a CONNECTION_STRING, --connection_string CONNECTION_STRING
                        http://<ip_address>:<port> connection string to graphql database
  -b BUFFER, --buffer_length BUFFER
                        Integer length of the buffer used to parse products, use if parsing large files
  -v VERBOSE, --verbose VERBOSE
                        Increased debug output
```

### Example runs:
- ```python3 export_activities.py 25 -p EXPORT..VP -s EXPORT.SAF # Export files for plan ID 25```

# Computing Aziumuth and Elevation using DSN Multi-Mission Utilities
Use the [az_el.py script](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN/blob/793ec1f0da746009ae4002a0ffa191baf65d40e4/python_scripts/libaerie/spice_calcs/az_el.py) to calculate the azimuth and elevation of DSSs from the p.o.v. of your spacecraft. This script is currently set up to compute the azimuth, elevation, and view periods for multiple DSSs from the point of view of the spacecraft Europa-Clipper, between May 2nd, 2028 and May 5th, 2028.

### Computing Azimuth and Elevation for Multiple DSS and Viewing in the Aerie UI
1. Update the `al_el_vp.py` script as needed (see below).
2. Run the `al_el_vp.py` script. Comment out the `view_pr_driver(config)` line. (Running the script as is will result in both azimuth and elevation values being computed for DSN antennas, as well as View Periods being computed. For now, we only want to compute azimuth and elevation.) 
3. Build the jar.
4. Load jar into Aerie UI.
5. Simulate the plan in the UI.
6. View the azimuth and elevation resources in the timeline to ensure the data was computed and included in the jar.

### Computing View Period windows for Multiple DSS and Viewing View Period Activity Instances in the Aerie UI 
(This should be done after loading a jar into the UI.)
1. Comment out the `el_az_driver(config)` line in the script.
2. Update the script with the plan id. Make any configuration updates as needed (see below).
3. Run the `el_az_driver(config)` script
4. Simulate the plan in the UI.
5. View the View Period Activity instances to ensure the data was computed and posted.

### Configuration for Elevation and Azimuth Calculations
1. Update the `al_el_vp.py` script to reflect your mission's time format, plan start, and plan end.
2. Update the step size, which reflects the seconds between time steps for computations.
3. Update the `chosen_dss` list to reflect the stations for which you want to compute azimuth, elevation, or view periods.
4. Update the spacecraft ID
5. Update the plan ID (this can be determined using the UI).
6. Update the specific kernels for your mission [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN/tree/main/python_scripts/libaerie/spice_calcs/kernels).

### Additional Configuration for View Period Spice Geometry Finder
The Geometry Finder Spice functions compute the View Period for the specified DSSs and spacecraft. The parameters that can be updated are Spice parameters. The definitions and usage of the Spice functions in this script can be found here (note the python library, SpiceyPy was used in this script):
* [wninsd](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wninsd.html)
* [gfposc](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/gfposc)
* [wncard](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wncard)
* [wnfetd](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/wnfetd)
* [timout](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/spicelib/timout.html)
* [SPICEDOUBLE_CELL](https://spiceypy.readthedocs.io/en/v2.3.1/documentation.html#spiceypy.utils.support_types.SPICEDOUBLE_CELL)

### Kernels Needed
You can use the provided [Meta-Kernel](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN/blob/main/python_scripts/libaerie/spice_calcs/erotat.tm) and kernels in this repository, or you can use your own. There are the kernels needed for the geometric computations.
* Leap Seconds (.tls)
* Solar System Ephemeris (.bsp)
* Spacecraft Ephemeris (.bsp)
* DSN Ephemeris (.bsp)
* Earth Topocentric Frame Kernel (.tf)
* NAIF PCK (Planetary Constants Kernel) (.tpc)
* Earth binary PCK (Earth orientation data) (.bpc)
* Meta-Kernel (.tm)
