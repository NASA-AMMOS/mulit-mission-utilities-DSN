# Instructions for Aerie Mission Model Template and DSN Multi-Mission Utilities

Click [here](https://github.com/NASA-AMMOS/multi-mission-utilities-DSN/edit/main/README.md#aerie-mission-model-template) for Aerie Mission Model Template.

Click [here](DSN Multi-Mission Utilities) for DSN Multi-Mission Utilities. 

## Aerie Mission Model Template

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

## DSN Multi Mission Utilities
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

### Running DSN Multi-Mission Utilities import_activities.py

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


