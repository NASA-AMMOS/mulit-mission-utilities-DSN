#!env python3
import argparse
import logging
import os
import datetime
from libaerie.products.product_parser import GqlInterface, DsnStationAllocationFileEncoder, DsnViewPeriodPredLegacyEncoder


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_FILE_BASE = os.path.join(SCRIPT_DIR, datetime.datetime.utcnow().strftime("%Y%j%H%M%S"))

date_format = '%Y-%j/%H:%M:%S'
parser = argparse.ArgumentParser()

# Positional argument
parser.add_argument('plan_id', type=int, help="plan ID to ingest activity directives into")

# Optional arguments
parser.add_argument('-p', '--vp_file', dest='vp', default=DEFAULT_FILE_BASE + ".VP", type=str, help="Filepath to export target DSN View Period file")
parser.add_argument('-s', '--sa_file', dest='sa', default=DEFAULT_FILE_BASE + ".SAF", type=str, help="Filepath to export target DSN Station Allocation file")
parser.add_argument('-m', '--mission_name', dest='mission_name', default="", type=str, help="Mission Name for VP and SAF header")
parser.add_argument('-S', '--spacecraft_name', dest='spacecraft_name', default="", type=str, help="Spacecraft Name for VP and SAF header")
parser.add_argument('-d', '--dsn_id', dest='dsn_id', default=0, type=int, help="Integer DSN spacecraft number for VP and SAF header")
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

# Setup GQL
gql = GqlInterface(connection_string=args.connection_string)
plan_start, plan_end = gql.get_plan_info_from_id(plan_id)

saf_header = {
  "MISSION_NAME": args.mission_name,
  "SPACECRAFT_NAME": args.spacecraft_name,
  "DSN_SPACECRAFT_NUM": args.dsn_id,
  "DATA_SET_ID": "AERIE_PLAN_EXPORT",
  "FILE_NAME": os.path.basename(args.sa),
  "PRODUCT_VERSION_ID": 1.0,
  "APPLICABLE_START_TIME": plan_start,
  "APPLICABLE_STOP_TIME": plan_end,
  "PRODUCT_CREATION_TIME": datetime.datetime.utcnow()
}
try:
  saf_encoder = DsnStationAllocationFileEncoder(args.sa, saf_header)
except FileNotFoundError as fnfe:
  logger.fatal(str(fnfe))
  exit(1)

vp_header = {
  "MISSION_NAME": args.mission_name,
  "SPACECRAFT_NAME": args.spacecraft_name,
  "DSN_SPACECRAFT_NUM": args.dsn_id,
  "FILE_NAME": os.path.basename(args.vp),
  "DATA_SET_ID": "AERIE_PLAN_EXPORT",
  "USER_PRODUCT_ID": 1.0,
  "APPLICABLE_START_TIME": plan_start.strftime(DsnViewPeriodPredLegacyEncoder.HEADER_TIME_FORMAT),
  "APPLICABLE_STOP_TIME": plan_end.strftime(DsnViewPeriodPredLegacyEncoder.HEADER_TIME_FORMAT),
  "PRODUCT_CREATION_TIME": datetime.datetime.utcnow().strftime(DsnViewPeriodPredLegacyEncoder.HEADER_TIME_FORMAT)
}
try:
  vp_encoder = DsnViewPeriodPredLegacyEncoder(args.vp, vp_header)
except FileNotFoundError as fnfe:
  logger.fatal(str(fnfe))
  exit(1)

gql.demux_files(saf_encoder, vp_encoder, plan_id)
