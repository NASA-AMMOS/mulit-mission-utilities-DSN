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

    EVENT_RECORD_REGEX = "(?P<TIME>.{15}).(?P<EVENT>.{16}).(?P<SPACECRAFT_IDENTIFIER>.{3}).(?P<STATION_IDENTIFIER>.{2}).(?P<PASS>.{4}).(?P<AZIMUTH>.{5}).(?P<ELEVATION>.{5}).(?P<AZ_LHA_X>.{5}).(?P<EL_DEC_Y>.{5}).(?P<RTLT>.{10})"

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
        header_segs["APPLICABLE_START_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_START_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
        header_segs["APPLICABLE_STOP_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_STOP_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
        header_segs["PRODUCT_CREATION_TIME"] = datetime.datetime.strptime(header_segs["PRODUCT_CREATION_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)

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

            r["TIME"] = datetime.datetime.strptime(r["TIME"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
            r["EVENT"] = r["EVENT"].strip()
            r["SPACECRAFT_IDENTIFIER"] = int(r["SPACECRAFT_IDENTIFIER"])
            r["STATION_IDENTIFIER"] = int(r["STATION_IDENTIFIER"])
            r["PASS"] = int(r["PASS"])
            r["AZIMUTH"] = float(r["AZIMUTH"])
            r["ELEVATION"] = float(r["ELEVATION"])
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
        header_segs["APPLICABLE_START_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_START_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
        header_segs["APPLICABLE_STOP_TIME"] = datetime.datetime.strptime(header_segs["APPLICABLE_STOP_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
        header_segs["PRODUCT_CREATION_TIME"] = datetime.datetime.strptime(header_segs["PRODUCT_CREATION_TIME"], cls.HEADER_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)

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
                r["EOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOT"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=1)
            else:
                r["EOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOT"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)

            if r["SOA"] > r["EOA"]:
                r["EOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOA"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=1)
            else:
                r["EOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["EOA"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)

            r["SOA"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["SOA"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)
            r["BOT"] = datetime.datetime.strptime(r["YY"] + " " + r["DOY"] + r["BOT"], self.EVENT_TIME_FORMAT).replace(tzinfo=datetime.timezone.utc)

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


class Encoder(object):

  HEADER_TIME_FORMAT = ""
  HEADER_KEYS = []
  EVENT_KEYS = []
  SFDU_HEADER = ()

  @classmethod
  def check_header(cls, header_hash: dict) -> bool:

    assert(isinstance(header_hash, dict))
    logger = logging.getLogger(__name__)

    for key, data_type in cls.HEADER_KEYS:
      if key not in header_hash:
        logger.error("Missing header value for '%s' in encoding", key)
        return False

      if not isinstance(header_hash[key], data_type):
        logger.error("Expected datatype '%s' for header value '%s', got '%s'", data_type, key, type(header_hash[key]))
        return False

    return True

  @classmethod
  def cast_header(cls, header_hash: dict) -> str:

    assert(isinstance(header_hash, dict))

    if not cls.check_header(header_hash):
      raise ValueError("Malformed header_hash")

    r = ""

    r += "%s\n" % (cls.SFDU_HEADER[0],)

    for key, data_type in cls.HEADER_KEYS:

      if key in ("APPLICABLE_START_TIME", "APPLICABLE_STOP_TIME", "PRODUCT_CREATION_TIME"):
        r += "%s = %s;\n" % (key, header_hash[key].strftime(cls.HEADER_TIME_FORMAT))
      else:
        r += "%s = %s;\n" % (key, data_type(header_hash[key]))

    r += "%s\n" % (cls.SFDU_HEADER[1],)

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
      elif data_type == int and event_hash[key] >= 10 ** max_length:
        val = 10 ** (max_length)
        logger.error("Event value field '%s' -> '%s' is too long", key, event_hash[key])
        return False

    return True

  @classmethod
  def cast_event(cls, event_hash: dict) -> str:

    assert(isinstance(event_hash, dict))

    if not cls.check_event(event_hash):
      raise ValueError("Malformed event_hash")

  @classmethod
  def cast(cls, filename: str, header_hash: dict, event_hashs: Iterable[dict]) -> None:

    assert(isinstance(filename, str))
    logger = logging.getLogger(__name__)

    logger.info("Opening file for Encoding: %s", filename)
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


class DsnViewPeriodPredLegacyEncoder(Encoder):

  HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
  HEADER_KEYS = [("MISSION_NAME", str),
                 ("SPACECRAFT_NAME", str),
                 ("DSN_SPACECRAFT_NUM", int),
                 ("DATA_SET_ID", str),
                 ("FILE_NAME", str),
                 ("USER_PRODUCT_ID", float),
                 ("APPLICABLE_START_TIME", datetime.datetime),
                 ("APPLICABLE_STOP_TIME", datetime.datetime),
                 ("PRODUCT_CREATION_TIME", datetime.datetime)]
  SFDU_HEADER = ("CCSD3ZF0000100000001NJPL3KS0L015$$MARK$$",
                 "CCSD3RE00000$$MARK$$NJPL3IF0M00400000001")

  EVENT_TIME_FORMAT = "%y %j/%H:%M:%S"
  EVENT_KEYS = [("TIME", datetime.datetime, 15),
                ("EVENT", str, 16),
                ("SPACECRAFT_IDENTIFIER", int, 3),
                ("STATION_IDENTIFIER", int, 2),
                ("PASS", int, 4),
                ("AZIMUTH", float, 5),
                ("ELEVATION", float, 5),
                ("AZ_LHA_X", float, 5),
                ("EL_DEC_Y", float, 5),
                ("RTLT", datetime.timedelta, 10)]

  @classmethod
  def check_event(cls, event_hash: dict) -> bool:

    if super(DsnViewPeriodPredLegacyEncoder, cls).check_event(event_hash) is False:
      return False

    logger = logging.getLogger(__name__)

    if not (0 <= event_hash["SPACECRAFT_IDENTIFIER"] < 1000):
      logger.error("Event value field 'SPACECRAFT_IDENTIFIER' -> %s is not within proper range of 0 to 999", event_hash["SPACECRAFT_IDENTIFIER"])
      return False
    elif not (0 <= event_hash["AZIMUTH"] < 360):
      logger.error("Event value field 'AZIMUTH' -> %s is not within proper range of 0 to 360", event_hash["AZIMUTH"])
      return False
    elif not (-90 <= event_hash["ELEVATION"] <= 90):
      logger.error("Event value field 'ELEVATION' -> %s is not within proper range of -90 to 90", event_hash["ELEVATION"])
      return False
    elif not (0 <= event_hash["AZ_LHA_X"] < 360):
      logger.error("Event value field 'AZ_LHA_X' -> %s is not within proper range of 0 to 360", event_hash["AZ_LHA_X"])
      return False
    elif not (0 <= event_hash["EL_DEC_Y"] < 360):
      logger.error("Event value field 'EL_DEC_Y' -> %s is not within proper range of 0 to 360", event_hash["EL_DEC_Y"])
      return False

    return True

  @classmethod
  def cast_event(cls, event_hash: dict) -> str:

    super(DsnViewPeriodPredLegacyEncoder, cls).cast_event(event_hash)

    translated_event = event_hash

    translated_event["TIME"] = translated_event["TIME"].strftime(cls.EVENT_TIME_FORMAT)
    translated_event["SPACECRAFT_IDENTIFIER"] = str(translated_event["SPACECRAFT_IDENTIFIER"]).zfill(3)
    translated_event["STATION_IDENTIFIER"] = str(translated_event["STATION_IDENTIFIER"]).zfill(2)
    translated_event["PASS"] = str(translated_event["PASS"]).zfill(4)
    translated_event["AZIMUTH"] = str(round(translated_event["AZIMUTH"], 1))
    translated_event["ELEVATION"] = str(round(translated_event["ELEVATION"], 1))
    translated_event["AZ_LHA_X"] = str(round(translated_event["AZ_LHA_X"], 1))
    translated_event["EL_DEC_Y"] = str(round(translated_event["EL_DEC_Y"], 1))

    hours, remainder = divmod(translated_event["RTLT"].total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    translated_event["RTLT"] = '{:02}:{:02}:{:04}'.format(int(hours), int(minutes), round(seconds, 1))

    r = ""
    looper = iter(cls.EVENT_KEYS)

    for key, data_type, length in looper:

      if key in ("AZIMUTH", "ELEVATION", "AZ_LHA_X", "EL_DEC_Y"):
        r += translated_event[key].rjust(length)
      else:
        r += translated_event[key].ljust(length)

      # No space after RTLT
      if key == "RTLT":
        continue

      r += " "

    r += "\n"
    return r


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
    SFDU_HEADER = ("CCSD3ZF0000100000001NJPL3KS0L015$$MARK$$",
                   "CCSD3RE00000$$MARK$$NJPL3IF0M00200000001")

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
    def cast_event(cls, event_hash: dict) -> str:

        super(DsnStationAllocationFileEncoder, cls).cast_event(event_hash)

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
                continue
            r += " "

        r += "   \n"
        return r


class GqlInterface(object):

    INSERT_ACTIVITY_QUERY = 'mutation InsertActivities($activities: [activity_directive_insert_input!]!) {insert_activity_directive(objects: $activities) {returning {id name } } }'
    READ_PLAN_QUERY = 'query getPlan($id: Int) {plan(where: {id: {_eq: $id}}) {id name model_id start_time duration} }'

    DEFAULT_CONNECTION_STRING = 'http://localhost:8080/v1/graphql'

    def __init__(self, connection_string: str=DEFAULT_CONNECTION_STRING):

        logger = logging.getLogger(__name__)

        self.__connection_string = connection_string

        logger.info("GraphQL Config: api_conn: %s", connection_string)

    def get_plan_info_from_id(self, plan_id: int):
        logger = logging.getLogger(__name__)
        plans = self.read_plan(plan_id)["data"]["plan"]

        if len(plans) == 0:
            logger.error("Plan id %s is not found", plan_id)
            return None
        elif len(plans) > 1:
            logger.error("Multiple plans found for plan id %s", plan_id)
            return None

        plan = plans[0]

        plan_start = datetime.datetime.fromisoformat(plan["start_time"])
        plan_name = plan["name"]

        H, MM, SSZ = plan["duration"].split(":")
        plan_end = plan_start + datetime.timedelta(hours=int(H), minutes=int(MM), seconds=float(SSZ))

        logger.info("Found plan \"%s\", starting at %s, ending at %s", plan_name, plan_start.isoformat(), plan_end.isoformat())

        return plan_start, plan_end

    def mux_files(self, decoders: list, plan_id) -> dict:

        assert(isinstance(decoders, list))
        logger = logging.getLogger(__name__)

        plan_start, plan_end = self.get_plan_info_from_id(plan_id)

        for decoder in decoders:

            if isinstance(decoder, DsnViewPeriodPredLegacyDecoder):
                for record in decoder.parse():
                    if plan_start > record["TIME"] or record["TIME"] > plan_end:
                        logger.warning("Record %s is out of range for plan id %s, daterange %s to %s", record, plan_id, plan_start.isoformat(), plan_end.isoformat())
                    yield self.convert_dsn_viewperiod_to_gql(plan_id, plan_start, decoder.header_hash, record)

            elif isinstance(decoder, DsnStationAllocationFileDecoder):
                for record in decoder.parse():
                    if plan_start > record["SOA"] or record["SOA"] > plan_end:
                        logger.warning("Record %s is out of range for plan id %s, daterange %s to %s", record, plan_id, plan_start.isoformat(), plan_end.isoformat())
                    yield self.convert_dsn_stationallocation_to_gql(plan_id, plan_start, decoder.header_hash, record)

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
        logger.debug("create_activities: %s", json.dumps(response.json(), indent=2))

    def read_plan(self, id: int):

      assert isinstance(id, (type(None), int))
      logger = logging.getLogger(__name__)

      logger.debug("Reading plans for: id %s", id)
      response = requests.post(
        url=self.__connection_string,
        json={
          'query': self.READ_PLAN_QUERY,
          'variables': {
            'id': id
          },
        },
        verify=False
      )

      r = response.json()
      logger.debug("read_plan: %s", json.dumps(r, indent=2))
      return r

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
        start_offset = cls.convert_to_aerie_offset(plan_start_time, event_segs["TIME"])
        mission_name = header_segs["MISSION_NAME"]
        spacecraft_name = header_segs["SPACECRAFT_NAME"]
        naif_spacecraft_id = -header_segs["DSN_SPACECRAFT_NUM"]
        dsn_spacecraft_id = header_segs["DSN_SPACECRAFT_NUM"]
        station_receive_time_utc = event_segs["TIME"].isoformat()
        viewperiod_event = event_segs["EVENT"]
        station_identifier = event_segs["STATION_IDENTIFIER"]
        pass_number = event_segs["PASS"]
        azimuth_degrees = event_segs["AZIMUTH"]
        elevation_degrees = event_segs["ELEVATION"]
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
    root_logger.setLevel(logging.DEBUG)

    #saf_file = DsnStationAllocationFileDecoder("../../M20_20230_20272_TEST.SAF")
    #saf_header = saf_file.read_header()
    #saf_iter = saf_file.parse()
    #DsnStationAllocationFileEncoder.cast("./outtest.SAF", saf_header, saf_iter)

    #vp_file = DsnViewPeriodPredLegacyDecoder("../../M20_20223_20284_TEST.VP")
    #vp_header = vp_file.read_header()
    #vp_iter = vp_file.parse()
    #DsnViewPeriodPredLegacyEncoder.cast("./outtest.VP", vp_header, vp_iter)


    GqlInterface(0, datetime.datetime.now()).read_plan(id=9)
    #GqlInterface(0, datetime.datetime.now()).mux_files([vp_file, saf_file])
