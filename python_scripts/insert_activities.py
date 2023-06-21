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

# Positional argument
parser.add_argument('plan_id', type=int, help="plan ID to ingest activity directives into")
parser.add_argument('plan_start_date', help="Start date of plan in 'YYYY-DOY/HH:MM:SS'")

# Optional arguments
parser.add_argument('-p', '--vp_file', action='append', dest='vp', default=[], help="Filepath to a DSN View Period file")
parser.add_argument('-s', '--sa_file', action='append', dest='sa', default=[], help="Filepath to a DSN Station Allocation file")
parser.add_argument('-a', '--connection_string', default=GqlInterface.DEFAULT_CONNECTION_STRING, help="http://<ip_address>:<port> connection string to graphql database")
parser.add_argument('-b', '--buffer_length', default=None, dest='buffer', type=int, help="Integer length of the buffer used to parse products, use if parsing large files")

args = parser.parse_args()

plan_id = int(args.plan_id)

# Logging to console
logging.basicConfig()
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

# Check inputs
try:
    plan_start_formatted = datetime.datetime.strptime(args.plan_start_date, date_format)
except Exception as e:
    logger.fatal("Invalid date: expected format '%s', got '%s'", date_format, args.plan_start_date)
    exit(1)

decoders = []

for file in args.sa:
    try:
        decoders.append(DsnStationAllocationFileDecoder(file))
    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
        exit(1)
for file in args.vp:
    try:
        decoders.append(DsnViewPeriodPredLegacyDecoder(file))
    except FileNotFoundError as fnfe:
        logger.fatal(str(fnfe))
        exit(1)

# Setup GQL
gql = GqlInterface(plan_id, plan_start_formatted, connection_string=args.connection_string)

buffer_len = args.buffer
activities = []

for activity in gql.mux_files(decoders):
    activities.append(activity)

    # Check if Buffer is filled
    if buffer_len is not None and len(activities) >= buffer_len:
        logger.debug("Buffer filled with %s records", len(activities))
        gql.create_activities(activities)

        # Remove items from buffer
        activities.clear()

gql.create_activities(activities)
