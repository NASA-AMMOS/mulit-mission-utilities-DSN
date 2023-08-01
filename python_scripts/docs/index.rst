.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/libaerie>

Usage
=====================================================

Prerequisites for Development
-----------------------------------------------------
- Install venv for Python 3.9+ and setup a new virtual environment in this directory.

.. code-block:: bash

  cd mulit-mission-utilities-DSN/python_scripts
  python3 -m venv .venv

- Activate Virtual Environment for Python project

.. code-block:: bash

  source .venv/bin/activate

- Install project dependencies

.. code-block:: bash

  pip3 install -r requirements.txt

Running Tests
----------------------------

- Activate Virtual Environment

.. code-block:: bash

  source .venv/bin/activate

- Run PyTests to automatically setup tests in ./tests directory

.. code-block:: bash

  pytest

Installing and packaging libraries
---------------------------------------------


- PIP can be used with the setup.py script to install libaerie system-wide.
- Python build can be used to create a PyPi compliant package for upload to a python mirror

Installation
------------------------------------------

.. code-block:: bash

  pip3 install -e

Packaging
----------------------------------

.. code-block:: bash

  python3 -m build

Running import_activities.py
----------------------------

.. code-block:: bash

  import_activities.py can scan DSN View Period and DSN Station Allocation files and add them activities in an existing Aerie Installation.

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

Example runs
----------------------------------

.. code-block:: bash

  python3 import_activities.py 25 -p INPUT.VP -s INPUT.SAF # Ingesting one file of each type

.. code-block:: bash

  python3 import_activities.py 25 -p INPUT1.VP -p INPUT2.VP # Ingesting multiple files of one type

.. code-block:: bash

  python3 import_activities.py 25 -p ./INPUT1.VP -p ./INPUT2.VP -s ./INPUT1.SAF -s ./INPUT2.SAF -b 500 # Ingesting multiple files of both types inserting 500 activities at a time

It's recommended to set the -b option to a value less then 1000 as a large amount of event data can stress GraphQL


Running export_activities.py
----------------------------

.. code-block:: bash

  export_activities.py can read a Aerie plan and will write the activities to a single DSN View Period and DSN Station Allocation files.

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

Example runs:
---------------

.. code-block:: bash

  python3 export_activities.py 25 -p EXPORT..VP -s EXPORT.SAF # Export files for plan ID 25
