#!env python3

import json
import requests
import argparse
import os
import datetime
import logging

from libaerie.products.product_parser import GqlInterface, DsnStationAllocationFileDecoder, DsnViewPeriodPredLegacyDecoder

date_format = '%Y-%j/%H:%M:%S'
parser = argparse.ArgumentParser()

parser.add_argument('plan_id', help="plan ID to ingest activity directives into") # positional argument
parser.add_argument('plan_start_date', help="Start date of plan in 'YYYY-DOY/HH:MM:SS'")
parser.add_argument('-p', '--vp_file', action='append', dest='vp', default=[], help="Filepath to a DSN View Period file")
parser.add_argument('-s', '--sa_file', action='append', dest='sa', default=[], help="Filepath to a DSN Station Allocation file")
parser.add_argument('-a', '--connection_string', default=GqlInterface.DEFAULT_CONNECTION_STRING, help="http://<ip_address>:<port> connection string to graphql database")

args = parser.parse_args()

view_period_files = args.vp
station_allocation_files = args.sa
plan_id = int(args.plan_id)

# Logging to console
logging.basicConfig()
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Check inputs
try:
    plan_start_formatted = datetime.datetime.strptime(args.plan_start_date, date_format)
except Exception as e:
    logger.fatal("Invalid date: expected format '%s', got '%s'", date_format, args.plan_start_date)
    exit(1)

for file in station_allocation_files:
    if not os.path.isfile(file):
        logger.fatal("File '%s' does not exist", file)

for file in view_period_files:
    if not os.path.isfile(file):
        logger.fatal("File '%s' does not exist", file)

api_url = args.connection_string

decoders = []

for file in station_allocation_files:
    decoders.append(DsnStationAllocationFileDecoder(file))
for file in view_period_files:
    decoders.append(DsnViewPeriodPredLegacyDecoder(file))

gql = GqlInterface(plan_id, plan_start_formatted, connection_string=api_url)
activities = gql.mux_files(decoders)
gql.insert_activities(activities)
