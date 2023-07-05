#!env python3
import argparse
import logging
from libaerie.products.product_parser import GqlInterface, DsnStationAllocationFileDecoder, DsnViewPeriodPredLegacyDecoder

date_format = '%Y-%j/%H:%M:%S'
parser = argparse.ArgumentParser()

# Positional argument
parser.add_argument('plan_id', type=int, help="plan ID to ingest activity directives into")

# Optional arguments
parser.add_argument('-p', '--vp_file', action='append', dest='vp', default=[], help="Filepath to a DSN View Period file")
parser.add_argument('-s', '--sa_file', action='append', dest='sa', default=[], help="Filepath to a DSN Station Allocation file")
parser.add_argument('-a', '--connection_string', default=GqlInterface.DEFAULT_CONNECTION_STRING, help="http://<ip_address>:<port> connection string to graphql database")
parser.add_argument('-b', '--buffer_length', default=None, dest='buffer', type=int, help="Integer length of the buffer used to parse products, use if parsing large files")
parser.add_argument('-v', '--verbose', default=False, dest='verbose', type=bool, help="Increased debug output")

args = parser.parse_args()

plan_id = int(args.plan_id)

# Logging to console
logging.basicConfig()
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

if args.verbose is True:
    root_logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

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
gql = GqlInterface(connection_string=args.connection_string)

buffer_len = args.buffer
activities = []

for activity in gql.mux_files(decoders, plan_id):
    activities.append(activity)

    # Check if Buffer is filled
    if buffer_len is not None and len(activities) >= buffer_len:
        logger.debug("Buffer filled with %s records", len(activities))
        gql.create_activities(activities)

        # Remove items from buffer
        activities.clear()

gql.create_activities(activities)
