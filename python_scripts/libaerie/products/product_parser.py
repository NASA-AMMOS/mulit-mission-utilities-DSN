import re
import datetime
import os
import logging
import requests
import json

from collections.abc import Iterable
from abc import ABC, abstractmethod


class Decoder(ABC):

    @abstractmethod
    def parse(self):
        pass


class DsnViewPeriodPredLegacyDecoder(Decoder):

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j/%H:%M:%S"

    EVENT_RECORD_REGEX = "(?P<Time>.{15}).(?P<Event>.{16}).(?P<Spacecraft_identifier>.{3}).(?P<Station_identifier>.{2}).(?P<Pass>.{4}).(?P<Azimuth>.{5}).(?P<Elevation>.{5}).(?P<AZ_LHA_X>.{5}).(?P<EL_DEC_Y>.{5}).(?P<RTLT>.{10})"

    def __init__(self, filename: str):
        logger = logging.getLogger(__name__)

        if not os.path.isfile(filename):
            logging.error("DSN Viewperiod file not found: '%s'", filename)
            raise FileNotFoundError("DSN Viewperiod file not found: %s" % filename)

        logger.info("Opening DSN Viewperiod file for Decoding: %s", filename)
        try:
            self._fh = open(filename, "r")
        except Exception as e:
            logger.exception(e)

        self.header_hash = None

    @classmethod
    def chop_header_line(cls, line: str):
        logger = logging.getLogger(__name__)

        seg, value = line.split(" = ")
        value = value[:-1]

        logger.debug("Header segment '%s'(%s)", value, seg)

        return seg, value

    @classmethod
    def parse_header(cls, header_lines_arr: list):

        header_segs = {}
        for line in header_lines_arr[1:-1]:
            k, v = cls.chop_header_line(line[:-1])
            header_segs[k] = v

        header_segs["DSN_SPACECRAFT_NUM"] = int(header_segs["DSN_SPACECRAFT_NUM"])
        header_segs["USER_PRODUCT_ID"] = float(header_segs["USER_PRODUCT_ID"])
        header_segs["APPLICABLE_START_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_START_TIME"], cls.HEADER_TIME_FORMAT)
        header_segs["APPLICABLE_STOP_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_STOP_TIME"], cls.HEADER_TIME_FORMAT)
        header_segs["PRODUCT_CREATION_TIME"] = datetime.datetime.strptime(header_segs["PRODUCT_CREATION_TIME"], cls.HEADER_TIME_FORMAT)

        return header_segs

    @classmethod
    def parse_line(cls, line: str):

        logger = logging.getLogger(__name__)

        result = re.search(cls.EVENT_RECORD_REGEX, line)

        if not result:
            logger.error("Got misformatted event line in DSN_VIEWPERIOD: %s", line)
            raise ValueError("Misformatted line")

        return result.groupdict()

    def read_header(self) -> dict:

        if self.header_hash is not None:
            return self.header_hash

        header = self.parse_header([next(self._fh) for _ in range(11)])
        self.header_hash = header

        return header

    def parse(self):

        logger = logging.getLogger(__name__)
        logger.info("Parsing DSN View Period File: %s", self._fh.name)

        self.read_header()

        num_r = 0

        for line in self._fh:
            r = self.parse_line(line)

            r["Time"] = datetime.datetime.strptime(r["Time"], self.EVENT_TIME_FORMAT)
            r["Event"] = r["Event"].strip()
            r["Spacecraft_identifier"] = int(r["Spacecraft_identifier"])
            r["Station_identifier"] = int(r["Station_identifier"])
            r["Pass"] = int(r["Pass"])
            r["Azimuth"] = float(r["Azimuth"])
            r["Elevation"] = float(r["Elevation"])
            r["AZ_LHA_X"] = float(r["AZ_LHA_X"])
            r["EL_DEC_Y"] = float(r["EL_DEC_Y"])
            r["RTLT"] = self.rtlt_to_timedelta(r["RTLT"])
            logger.debug("Parsed DSN Viewperiod event: %s", r)
            num_r+=1
            yield r

        logger.info("Got %s activites from %s", num_r, self._fh.name)

    @classmethod
    def rtlt_to_timedelta(cls, rtlt_dur_str: str) -> datetime.timedelta:

        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


class DsnStationAllocationFileDecoder(Decoder):

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j%H%M"

    EVENT_RECORD_REGEX = "(?P<CHANGE_INDICATOR>.)(?P<YY>.{2}).(?P<DOY>.{3}).(?P<SOA>.{4}).(?P<BOT>.{4}).(?P<EOT>.{4}).(?P<EOA>.{4}).(?P<ANTENNA_ID>.{6}).(?P<PROJECT_ID>.{5}).(?P<DESCRIPTION>.{16}).(?P<PASS>.{4}).(?P<CONFIG_CODE>.{6})(?P<SOE_FLAG>.).(?P<WORK_CODE_CAT>.{3}).(?P<RELATE>.)."

    def __init__(self, filename: str):
        logger = logging.getLogger(__name__)

        if not os.path.isfile(filename):
            logging.error("DSN Station Allocation file not found: '%s'", filename)
            raise FileNotFoundError("DSN Station Allocation file not found: %s" % filename)

        logger.info("Opening DSN Station Allocation file for Decoding: %s", filename)
        try:
            self._fh = open(filename, "r")
        except Exception as e:
            logger.exception(e)

        self.header_hash = None

    @classmethod
    def chop_header_line(cls, line: str):
        logger = logging.getLogger(__name__)

        seg, value = line.split(" = ")
        value = value[:-1]

        logger.debug("Header segment '%s'(%s)", value, seg)

        return seg, value

    @classmethod
    def parse_header(cls, header_lines_arr: list):

        header_segs = {}
        for line in header_lines_arr[1:-1]:
            k, v = cls.chop_header_line(line[:-1])
            header_segs[k] = v

        header_segs["DSN_SPACECRAFT_NUM"] = int(header_segs["DSN_SPACECRAFT_NUM"])
        header_segs["PRODUCT_VERSION_ID"] = float(header_segs["PRODUCT_VERSION_ID"])
        header_segs["APPLICABLE_START_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_START_TIME"], cls.HEADER_TIME_FORMAT)
        header_segs["APPLICABLE_STOP_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_STOP_TIME"], cls.HEADER_TIME_FORMAT)
        header_segs["PRODUCT_CREATION_TIME"] = datetime.datetime.strptime(header_segs["PRODUCT_CREATION_TIME"], cls.HEADER_TIME_FORMAT)

        return header_segs

    @classmethod
    def parse_line(cls, line: str):

        logger = logging.getLogger(__name__)

        result = re.search(cls.EVENT_RECORD_REGEX, line)

        if not result:
            logger.error("Got misformatted event line in DSN Station Allocation File: %s", line)
            raise ValueError("Misformatted line")

        return result.groupdict()

    def read_header(self) -> dict:

        if self.header_hash is not None:
            return self.header_hash

        header = self.parse_header([next(self._fh) for _ in range(11)])
        self.header_hash = header

        return header

    def parse(self):

        logger = logging.getLogger(__name__)
        logger.info("Parsing DSN Station Allocation File: %s", self._fh.name)

        self.read_header()

        num_r = 0

        for line in self._fh:
            r = self.parse_line(line)

            # We need to do a check here, End of Track and End of Activity can roll over to the end of the day

            if r["SOA"] > r["EOT"]:
                r["EOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOT"], self.EVENT_TIME_FORMAT) + datetime.timedelta(days=1)
            else:
                r["EOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOT"], self.EVENT_TIME_FORMAT)

            if r["SOA"] > r["EOA"]:
                r["EOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOA"], self.EVENT_TIME_FORMAT) + datetime.timedelta(days=1)
            else:
                r["EOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOA"], self.EVENT_TIME_FORMAT)

            r["SOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["SOA"], self.EVENT_TIME_FORMAT)
            r["BOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["BOT"], self.EVENT_TIME_FORMAT)

            r["PROJECT_ID"] = r["PROJECT_ID"].strip()
            r["DESCRIPTION"] = r["DESCRIPTION"].strip()
            r["PASS"] = int(r["PASS"])
            r["CONFIG_CODE"] = r["CONFIG_CODE"].strip()

            logger.debug("Parsed DSN Viewperiod event: %s", r)
            num_r += 1
            yield r

        logger.info("Got %s activites from %s", num_r, self._fh.name)

    @classmethod
    def rtlt_to_timedelta(cls, rtlt_dur_str: str) -> datetime.timedelta:

        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


class Encoder(ABC):

    @abstractmethod
    def cast(cls, filename: str, header_hash: dict, event_hashs: Iterable[dict]) -> None:
        pass


class DsnViewPeriodPredLegacyEncoder(Encoder):

    def __init__(self):
        pass


class DsnStationAllocationFileEncoder(Encoder):

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    HEADER_KEYS = [("MISSION_NAME", str),
                   ("SPACECRAFT_NAME", str),
                   ("DSN_SPACECRAFT_NUM", int),
                   ("DATA_SET_ID", str),
                   ("FILE_NAME", str),
                   ("PRODUCT_VERSION_ID", float),
                   ("APPLICABLE_START_TIME", datetime.datetime),
                   ("APPLICABLE_STOP_TIME", datetime.datetime),
                   ("PRODUCT_CREATION_TIME", datetime.datetime)]

    YY_FORMAT = "%y"
    DOY_FORMAT = "%j"
    HHMM_FORMAT = "%H%M"
    EVENT_KEYS = [("CHANGE_INDICATOR", str, 1),
                  ("YY", str, 2),
                  ("DOY", str, 3),
                  ("SOA", datetime.datetime, 4),
                  ("BOT", datetime.datetime, 4),
                  ("EOT", datetime.datetime, 4),
                  ("EOA", datetime.datetime, 4),
                  ("ANTENNA_ID", str, 6),
                  ("PROJECT_ID", str, 5),
                  ("DESCRIPTION", str, 16),
                  ("PASS", int, 4),
                  ("CONFIG_CODE", str, 6),
                  ("SOE_FLAG", str, 1),
                  ("WORK_CODE_CAT", str, 3),
                  ("RELATE", str, 1)]

    @classmethod
    def check_header(cls, header_hash: dict) -> bool:

        assert(isinstance(header_hash, dict))
        logger = logging.getLogger(__name__)

        for key, data_type in cls.HEADER_KEYS:
            if key not in header_hash:
                logger.error("Missing header value for '%s' in Station Allocation encoding", key)
                return False

            if not isinstance(header_hash[key], data_type):
                logger.error("Expected datatype '%s' for header value '%s' in Station Allocation encoding, got '%s'", data_type, key, type(header_hash[key]))
                return False

        return True

    @classmethod
    def cast_header(cls, header_hash: dict) -> str:

      assert(isinstance(header_hash, dict))

      if not cls.check_header(header_hash):
          raise ValueError("Malformed header_hash")

      r = ""

      # TODO Write top string here
      r += "CCSD3ZF0000100000001NJPL3KS0L015$$MARK$$\n"

      for key, data_type in cls.HEADER_KEYS:

          if key in ("APPLICABLE_START_TIME", "APPLICABLE_STOP_TIME", "PRODUCT_CREATION_TIME"):
              r += "%s = %s;\n" % (key, header_hash[key].strftime(cls.HEADER_TIME_FORMAT))
          else:
              r += "%s = %s;\n" % (key, data_type(header_hash[key]))

      # TODO Write bottom string here
      r += "CCSD3RE00000$$MARK$$NJPL3IF0M00200000001\n"

      return r

    @classmethod
    def check_event(cls, event_hash: dict) -> bool:

        assert(isinstance(event_hash, dict))
        logger = logging.getLogger(__name__)

        for key, data_type, max_length in cls.EVENT_KEYS:
            if key not in event_hash:
                logger.error("Missing event value for '%s' in Station Allocation encoding", key)
                return False

            if not isinstance(event_hash[key], data_type):
                logger.error("Expected datatype '%s' for event value '%s' in Station Allocation encoding, got '%s'", data_type, key, type(event_hash[key]))
                return False

            if data_type == str and len(event_hash[key]) > max_length:
                logger.error("Event value field '%s' -> '%s' is too long", key, event_hash[key])
                return False
            elif data_type == int and event_hash[key] > 10 ** (max_length - 1):
                val = 10 ** (max_length - 1)
                logger.error("Event value field '%s' -> '%s' is too long", key, event_hash[key])
                return False

        return True

    @classmethod
    def cast_event(cls, event_hash: dict) -> str:

        assert(isinstance(event_hash, dict))

        if not cls.check_event(event_hash):
            raise ValueError("Malformed event_hash")

        translated_event = event_hash

        translated_event["SOA"] = translated_event["SOA"].strftime(cls.HHMM_FORMAT)
        translated_event["BOT"] = translated_event["BOT"].strftime(cls.HHMM_FORMAT)
        translated_event["EOT"] = translated_event["EOT"].strftime(cls.HHMM_FORMAT)
        translated_event["EOA"] = translated_event["EOA"].strftime(cls.HHMM_FORMAT)
        translated_event["PASS"] = str(translated_event["PASS"]).zfill(4)

        r = ""
        looper = iter(cls.EVENT_KEYS)

        # Change indicator
        key, data_type, length = next(looper)
        r += translated_event[key].ljust(length)

        for key, data_type, length in looper:
            r += translated_event[key].ljust(length)

            # No space after CONFIG_CODE
            if key == "CONFIG_CODE":
                next
            r += " "

        r += "  \n"
        return r

    @classmethod
    def cast(cls, filename: str, header_hash: dict, event_hashs: Iterable[dict]) -> None:

        assert(isinstance(filename, str))

        logger = logging.getLogger(__name__)

        logger.info("Opening DSN Station Allocation file for Encoding: %s", filename)
        try:
            fh = open(filename, "w")
        except Exception as e:
            logger.exception(e)
            raise

        num_r = 0
        # Write contents of file
        fh.write(cls.cast_header(header_hash))
        for event_hash in event_hashs:
            fh.write(cls.cast_event(event_hash))
            num_r += 1

        logger.info("Encoded %s activities to %s", num_r, filename)

        logger.debug("Closing file: %s", filename)
        fh.close()


class GqlInterface(object):

    INSERT_ACTIVITY_QUERY = '''mutation InsertActivities($activities: [activity_directive_insert_input!]!) {insert_activity_directive(objects: $activities) {returning {id name } } } '''
    DEFAULT_CONNECTION_STRING = 'http://localhost:8080/v1/graphql'

    def __init__(self, plan_id: int, plan_start: datetime.datetime, connection_string: str=DEFAULT_CONNECTION_STRING):

        assert(isinstance(plan_id, int))
        assert(isinstance(plan_start, datetime.datetime))

        logger = logging.getLogger(__name__)

        self.__plan_id = plan_id
        self.__plan_start = plan_start
        self.__connection_string = connection_string

        logger.info("GraphQL Config: plan_id: %s, api_conn: %s", plan_id, connection_string)

    def mux_files(self, decoders: list) -> dict:

        assert(isinstance(decoders, list))
        logger = logging.getLogger(__name__)

        for decoder in decoders:

            if isinstance(decoder, DsnViewPeriodPredLegacyDecoder):
                for record in decoder.parse():
                    yield self.convert_dsn_viewperiod_to_gql(self.__plan_id, self.__plan_start, decoder.header_hash, record)

            elif isinstance(decoder, DsnStationAllocationFileDecoder):
                for record in decoder.parse():
                    yield self.convert_dsn_stationallocation_to_gql(self.__plan_id, self.__plan_start, decoder.header_hash, record)

            else:
                logger.error("Aborting, Got invalid Decoder type: %s", type(decoder).__name__)
                raise ValueError("Invalid Decoder type: %s", type(decoder).__name__)

    def create_activities(self, activities: list):

        assert isinstance(activities, list)

        logger = logging.getLogger(__name__)

        logger.debug("Sending activities: %s", json.dumps(activities, indent=2))
        response = requests.post(
            url=self.__connection_string,
            json={
                'query': self.INSERT_ACTIVITY_QUERY,
                'variables': {"activities": activities},
            },
            verify=False
        )
        logger.debug(json.dumps(response.json(), indent=2))

    @classmethod
    def convert_to_aerie_offset(cls, plan_start_time: datetime.datetime, activity_start_time: datetime.datetime) -> str:

        start_offset_seconds = datetime.timedelta.total_seconds(activity_start_time - plan_start_time)
        hours_offset = start_offset_seconds // 3600
        start_offset_seconds -= hours_offset * 3600
        minutes_offset = start_offset_seconds // 60
        start_offset_seconds -= minutes_offset * 60

        start_offset = '{}:{}:{}'.format(int(hours_offset), int(minutes_offset), start_offset_seconds)

        return start_offset

    @classmethod
    def convert_to_aerie_duration(cls, activity_start_time: datetime.datetime, activity_end_time: datetime.datetime) -> int:
        return int((activity_end_time - activity_start_time).total_seconds() * 1e6)

    @classmethod
    def convert_dsn_viewperiod_to_gql(cls, plan_id: int, plan_start_time: datetime.datetime, header_segs: dict, event_segs: dict) -> dict:

        # Get event fields
        start_offset = cls.convert_to_aerie_offset(plan_start_time, event_segs["Time"])
        mission_name = header_segs["MISSION_NAME"]
        spacecraft_name = header_segs["SPACECRAFT_NAME"]
        naif_spacecraft_id = -header_segs["DSN_SPACECRAFT_NUM"]
        dsn_spacecraft_id = header_segs["DSN_SPACECRAFT_NUM"]
        station_receive_time_utc = event_segs["Time"].isoformat()
        viewperiod_event = event_segs["Event"]
        station_identifier = event_segs["Station_identifier"]
        pass_number = event_segs["Pass"]
        azimuth_degrees = event_segs["Azimuth"]
        elevation_degrees = event_segs["Elevation"]
        lha_x_degrees = event_segs["AZ_LHA_X"]
        dec_y_degrees = event_segs["EL_DEC_Y"]
        duration = event_segs["RTLT"].total_seconds() * 1e6

        return {
        'arguments': {
                'mission_name': mission_name,
                'spacecraft_name': spacecraft_name,
                'NAIF_spacecraft_ID': naif_spacecraft_id,
                'dsn_spacecraft_ID': dsn_spacecraft_id,
                'station_receive_time_UTC': station_receive_time_utc,
                'viewperiod_event': viewperiod_event,
                'station_identifier': station_identifier,
                'pass_number': pass_number,
                'azimuth_degrees': azimuth_degrees,
                'elevation_degrees': elevation_degrees,
                'lha_X_degrees': lha_x_degrees,
                'dec_Y_degrees': dec_y_degrees,
                'duration': duration
            },
            'plan_id': plan_id,
            'name': 'DSN View Period',
            'start_offset': start_offset,
            'type': 'DSN_View_Period'
        }

    @classmethod
    def convert_dsn_stationallocation_to_gql(cls, plan_id: int, plan_start_time: datetime.datetime, header_segs: dict, event_segs: dict) -> dict:

        # Get event fields
        start_offset = cls.convert_to_aerie_offset(plan_start_time, event_segs["SOA"])
        mission_name = header_segs["MISSION_NAME"]
        spacecraft_name = header_segs["SPACECRAFT_NAME"]
        naif_spacecraft_id = -header_segs["DSN_SPACECRAFT_NUM"]
        dsn_spacecraft_id = header_segs["DSN_SPACECRAFT_NUM"]
        pass_type = event_segs["DESCRIPTION"]
        soa = event_segs["SOA"].isoformat()
        bot = event_segs["BOT"].isoformat()
        eot = event_segs["EOT"].isoformat()
        eoa = event_segs["EOA"].isoformat()
        antenna_id = event_segs["ANTENNA_ID"]
        duration_of_activity = cls.convert_to_aerie_duration(event_segs["SOA"], event_segs["EOA"])
        start_of_track = event_segs["BOT"].isoformat()
        duration_of_track = cls.convert_to_aerie_duration(event_segs["BOT"], event_segs["EOT"])

        return {
        'arguments': {
                'mission_name': mission_name,
                'spacecraft_name': spacecraft_name,
                'NAIF_spacecraft_ID': naif_spacecraft_id,
                'dsn_spacecraft_ID': dsn_spacecraft_id,
                'pass_type': pass_type,
                'SOA': soa,
                'BOT': bot,
                'EOT': eot,
                'EOA': eoa,
                'antenna_ID': antenna_id,
                'duration_of_activity': duration_of_activity,
                'start_of_track': start_of_track,
                'duration_of_track': duration_of_track
                },
            'plan_id': plan_id,
            'name': 'DSN Track',
            'start_offset': start_offset,
            'type': 'DSN_Track'
        }


if __name__ == "__main__":
    logging.basicConfig()
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    vp_file = DsnViewPeriodPredLegacyDecoder("../../M20_20223_20284_TEST.VP")
    saf_file = DsnStationAllocationFileDecoder("../../M20_20230_20272_TEST.SAF")

    saf_header = saf_file.read_header()
    saf_iter = saf_file.parse()

    DsnStationAllocationFileEncoder.cast("./outtest", saf_header, saf_iter)

    #GqlInterface(0, datetime.datetime.now()).mux_files([vp_file, saf_file])
