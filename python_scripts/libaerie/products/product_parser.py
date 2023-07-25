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
    """
    Manages state for decoding a DSN View Period Legacy report file

    :ivar _fh: Private file handler used for reading data from the report
    :vartype _fh: file object
    :ivar header_hash: key / value store of the data contained in the header
    :vartype header_hash: dict
    "cvar HEADER_TIME_FORMAT: Format of the datetimes in the header
    :vartype HEADER_TIME_FORMAT: str
    "cvar EVENT_TIME_FORMAT: Format of the datetimes in the events
    :vartype EVENT_TIME_FORMAT: str
    """

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j/%H:%M:%S"

    EVENT_RECORD_REGEX = "(?P<TIME>.{15}).(?P<EVENT>.{16}).(?P<SPACECRAFT_IDENTIFIER>.{3}).(?P<STATION_IDENTIFIER>.{2}).(?P<PASS>.{4}).(?P<AZIMUTH>.{5}).(?P<ELEVATION>.{5}).(?P<AZ_LHA_X>.{5}).(?P<EL_DEC_Y>.{5}).(?P<RTLT>.{10})"

    def __init__(self, filename: str):
        """
        Initialize a DsnViewPeriodPredLegacyDecoder which reads information from DSN View Period files.

        :param filename: Filepath to View Period file.
        :type filename: str
        """
        logger = logging.getLogger(__name__)

        # Check if filepath is valid
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
    def chop_header_line(cls, line: str) -> tuple:
        """
        Converts a line from the View Period header into a key / value format

        :param line: Line from the View Period file header
        :type line: str
        :return: key, value tuple of the header field and its value
        :rtype: tuple
        """

        logger = logging.getLogger(__name__)

        # Left of "=" is the key, right is the value
        seg, value = line.split(" = ")
        value = value[:-1]

        logger.debug("Header segment '%s'(%s)", value, seg)

        return seg, value

    @classmethod
    def parse_header(cls, header_lines_arr: list):
        """
        Converts the full header into a dictionary of keys / values

        :param header_lines_arr: collection of lines from the header
        :type header_lines_arr: list
        :return: key, value dict of the header dicts and its value
        :rtype: dict
        """

        # Loop through header lines, call chop header line to parse individual lines
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
        """
        Converts an event line from the view period file to dictionary like object of key / values

        :param line: line containing event data from the View Period file
        :type line: str
        :return: key, value dict containing data from the event line
        :rtype: dict
        """

        logger = logging.getLogger(__name__)

        # Parse View Period line using Regex
        result = re.search(cls.EVENT_RECORD_REGEX, line)

        if not result:
            logger.error("Got misformatted event line in DSN_VIEWPERIOD: %s", line)
            raise ValueError("Misformatted line")

        return result.groupdict()

    def read_header(self) -> dict:
        """
        Read the View Period header and call parse_header to get the values from it

        :return: key, value dict containing data from the header
        :rtype: dict
        """

        if self.header_hash is not None:
            return self.header_hash

        header = self.parse_header([next(self._fh) for _ in range(11)])
        self.header_hash = header

        return header

    def parse(self):
        """
        Parse entire DSN View Period file, header will be placed into self.header_hash, uses a pythonic
        generator design pattern.  This function should be called in some iterative process such as a for loop.

        :return: generator returning key / value dicts of events
        :rtype: dict
        """

        logger = logging.getLogger(__name__)
        logger.info("Parsing DSN View Period File: %s", self._fh.name)

        # Parse the Viewperiod header
        self.read_header()

        num_r = 0

        # Parse Viewperiod events
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
        """
        Converts the formatted duration from the Viewperiod RTLT field into a python timedelta

        :param rtlt_dur_str: str containing the duration of rtlt
        :type rtlt_dur_str: str
        :return: timedelta object of the formatted duration
        :rtype: datetime.timedelta
        """

        # Split duration string into hour, minutes, seconds components and type convert them
        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


class DsnStationAllocationFileDecoder(Decoder):
    """
    Manages state for decoding a DSN Station Allocation report file

    :ivar _fh: Private file handler used for reading data from the report
    :vartype _fh: file object
    :ivar header_hash: key / value store of the data contained in the header
    :vartype header_hash: dict
    "cvar HEADER_TIME_FORMAT: Format of the datetimes in the header
    :vartype HEADER_TIME_FORMAT: str
    "cvar EVENT_TIME_FORMAT: Format of the datetimes in the events
    :vartype EVENT_TIME_FORMAT: str
    """

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j%H%M"

    EVENT_RECORD_REGEX = "(?P<CHANGE_INDICATOR>.)(?P<YY>.{2}).(?P<DOY>.{3}).(?P<SOA>.{4}).(?P<BOT>.{4}).(?P<EOT>.{4}).(?P<EOA>.{4}).(?P<ANTENNA_ID>.{6}).(?P<PROJECT_ID>.{5}).(?P<DESCRIPTION>.{16}).(?P<PASS>.{4}).(?P<CONFIG_CODE>.{6})(?P<SOE_FLAG>.).(?P<WORK_CODE_CAT>.{3}).(?P<RELATE>.)."

    def __init__(self, filename: str):
        """
        Initialize a DsnStationAllocationFileDecoder which reads information from DSN Station Allocation files.

        :param filename: Filepath to Station Allocation file.
        :type filename: str
        """

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
        """
        Converts a line from the Station Allocation header into a key / value format

        :param line: Line from the file header
        :type line: str
        :return: key, value tuple of the header field and its value
        :rtype: tuple
        """
        logger = logging.getLogger(__name__)

        seg, value = line.split(" = ")
        value = value[:-1]

        logger.debug("Header segment '%s'(%s)", value, seg)

        return seg, value

    @classmethod
    def parse_header(cls, header_lines_arr: list):
        """
        Converts the full header into a dictionary of keys / values

        :param header_lines_arr: collection of lines from the header
        :type header_lines_arr: list
        :return: key, value dict of the header dicts and its value
        :rtype: dict
        """

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
        """
        Converts an event line from the view period file to dictionary like object of key / values

        :param line: line containing event data from the View Period file
        :type line: str
        :return: key, value dict containing data from the event line
        :rtype: dict
        """

        logger = logging.getLogger(__name__)

        result = re.search(cls.EVENT_RECORD_REGEX, line)

        if not result:
            logger.error("Got misformatted event line in DSN Station Allocation File: %s", line)
            raise ValueError("Misformatted line")

        return result.groupdict()

    def read_header(self) -> dict:
        """
        Read the View Period header and call parse_header to get the values from it

        :return: key, value dict containing data from the header
        :rtype: dict
        """

        if self.header_hash is not None:
            return self.header_hash

        header = self.parse_header([next(self._fh) for _ in range(11)])
        self.header_hash = header

        return header

    def parse(self):
        """
        Parse entire DSN Station Allocation file, header will be placed into self.header_hash, uses a pythonic
        generator design pattern.  This function should be called in some iterative process such as a for loop.

        :return: generator returning key / value dicts of events
        :rtype: dict
        """

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
        """
        Converts the formatted duration from the Viewperiod RTLT field into a python timedelta

        :param rtlt_dur_str: str containing the duration of rtlt
        :type rtlt_dur_str: str
        :return: timedelta object of the formatted duration
        :rtype: datetime.timedelta
        """

        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


class Encoder(object):
  """
  Manages state for encoding a report file

  :ivar _fh: Private file handler used for writing data to the report
  :vartype _fh: file object
  :ivar header_hash: key / value store of the data that should be written to the header
  :vartype header_hash: dict
  "cvar HEADER_TIME_FORMAT: Format of the datetimes in the header
  :vartype HEADER_TIME_FORMAT: str
  "cvar HEADER_KEYS: List of tuples containing key / types for checking proper formatting of self.header_hash
  :vartype HEADER_KEYS: list
  "cvar EVENT_KEYS: List of tuples containing key / types for checking proper formatting of event hashes
  :vartype EVENT_KEYS: list
  "cvar SFDU_HEADER: Tuple containing the static content of the top and bottom of the header
  :vartype SFDU_KEYS: tuple
  """

  HEADER_TIME_FORMAT = ""
  HEADER_KEYS = []
  EVENT_KEYS = []
  SFDU_HEADER = ()

  def __init__(self, filename: str, header_hash:dict=None):
    """
    Initialize a Encoder which is meant to read output from the AERIE database and encode it into a report file.

    :param filename: Filepath to Encoded file.
    :type filename: str
    :param header_hash: Dictionary of header values
    :type header_hash: dict
    """

    logger = logging.getLogger(__name__)
    try:
      self._fh = open(filename, "w")
    except Exception as e:
      logger.exception(e)

    self.header_hash = header_hash
    self.header_flag = False

  @classmethod
  def check_header(cls, header_hash: dict) -> bool:

    """
    Checks the validity of the formatting of a user inputted header dictionary

    :param header_hash: Contains field information for the report header
    :type header_hash: dict
    :return: True on valid, False on non valid
    :rtype: bool
    """
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
    """
    Construct the file header, return it as a string

    :param header_hash: Contains field information for the report header
    :type header_hash: dict
    :return: Constructed header ready to be written to the report
    :rtype: str
    """

    assert(isinstance(header_hash, dict))

    # Quality check the formatting of the header_hash using cls.HEADER_KEYS
    if not cls.check_header(header_hash):
      raise ValueError("Malformed header_hash")

    r = ""

    r += "%s\n" % (cls.SFDU_HEADER[0],)

    # Construct header
    for key, data_type in cls.HEADER_KEYS:

      if key in ("APPLICABLE_START_TIME", "APPLICABLE_STOP_TIME", "PRODUCT_CREATION_TIME"):
        r += "%s = %s;\n" % (key, header_hash[key].strftime(cls.HEADER_TIME_FORMAT))
      else:
        r += "%s = %s;\n" % (key, data_type(header_hash[key]))

    r += "%s\n" % (cls.SFDU_HEADER[1],)

    return r

  @classmethod
  def check_event(cls, event_hash: dict) -> bool:
    """
    Checks the validity of the formatting of a user inputted event dictionary

    :param event_hash: Contains field information for the event
    :type event_hash: dict
    :return: True on valid, False on non valid
    :rtype: bool
    """

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
    """
    Construct the event line, return it as a string, this function is implemented in subclasses

    :param event_hash: Contains field information for the report event line
    :type event_hash: dict
    :return: None
    :rtype: None
    """

    assert(isinstance(event_hash, dict))

    if not cls.check_event(event_hash):
      raise ValueError("Malformed event_hash")

  def cast(self, event_hashs: Iterable[dict]) -> None:
    """
    Write the report file to the filepath, call class functions to check the validity of information and construct the
    report.

    :param event_hashs: Iterable object providing event_hashs which contain the information that should be written to
    the report.
    :type event_hashs: Iterable[dict]
    :return: None
    :rtype: None
    """

    logger = logging.getLogger(__name__)

    num_r = 0
    if self.check_header(self.header_hash) and not self.header_flag:
      # Write contents of file
      self._fh.write(self.cast_header(self.header_hash))
      self.header_flag = True

    for event_hash in event_hashs:
      self._fh.write(self.cast_event(event_hash))
      num_r += 1

    logger.info("Encoded %s activities to %s", num_r, self._fh.name)

    logger.debug("Closing file: %s", self._fh.name)
    self._fh.close()


class DsnViewPeriodPredLegacyEncoder(Encoder):
  """
  Manages state for encoding a DSN View Period report file

  :ivar _fh: Private file handler used for writing data to the report
  :vartype _fh: file object
  :ivar header_hash: key / value store of the data that should be written to the header
  :vartype header_hash: dict
  "cvar HEADER_TIME_FORMAT: Format of the datetimes in the header
  :vartype HEADER_TIME_FORMAT: str
  "cvar HEADER_KEYS: List of tuples containing key / types for checking proper formatting of self.header_hash
  :vartype HEADER_KEYS: list
  "cvar EVENT_KEYS: List of tuples containing key / types for checking proper formatting of event hashes
  :vartype EVENT_KEYS: list
  :cvar EVENT_TIME_FORMAT: Format of the datetimes in the Event lines
  :vartype EVENT_TIME_FORMAT: str
  "cvar SFDU_HEADER: Tuple containing the static content of the top and bottom of the header
  :vartype SFDU_HEADER: tuple
  """

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

  def __init__(self, filename: str, header_hash: dict=None):
    """
    Initialize an DsnViewPeriodPredLegacyEncoder which is meant to read output from the AERIE database and encode it
    into a report file.

    :param filename: Filepath to Encoded file.
    :type filename: str
    :param header_hash: Dictionary of header values
    :type header_hash: dict
    """
    logger = logging.getLogger(__name__)
    logger.info("Opening DSN Viewperiod file for Encoding: %s", filename)
    super(DsnViewPeriodPredLegacyEncoder, self).__init__(filename, header_hash)

  @classmethod
  def check_event(cls, event_hash: dict) -> bool:
    """
    Checks the validity of the formatting of a user inputted event dictionary

    :param event_hash: Contains field information for the event
    :type event_hash: dict
    :return: True on valid, False on non valid
    :rtype: bool
    """

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

  def cast_event(self, event_hash: dict) -> str:
    """
    Construct the event line, return it as a string, this function is implemented in subclasses

    :param event_hash: Contains field information for the report event line
    :type event_hash: dict
    :return: None
    :rtype: None
    """

    super(DsnViewPeriodPredLegacyEncoder, self).cast_event(event_hash)

    translated_event = event_hash

    # Format the fields and type convert all of the fields to str for writing to the report
    translated_event["TIME"] = translated_event["TIME"].strftime(self.EVENT_TIME_FORMAT)
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

    # Use cls.EVENT_KEYS as a blueprint for writing each line
    r = ""
    looper = iter(self.EVENT_KEYS)

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
    """
    Manages state for encoding a DSN Station Allocaation report file

    :ivar _fh: Private file handler used for writing data to the report
    :vartype _fh: file object
    :ivar header_hash: key / value store of the data that should be written to the header
    :vartype header_hash: dict
    "cvar HEADER_TIME_FORMAT: Format of the datetimes in the header
    :vartype HEADER_TIME_FORMAT: str
    "cvar HEADER_KEYS: List of tuples containing key / types for checking proper formatting of self.header_hash
    :vartype HEADER_KEYS: list
    "cvar EVENT_KEYS: List of tuples containing key / types for checking proper formatting of event hashes
    :vartype EVENT_KEYS: list
    "cvar SFDU_HEADER: Tuple containing the static content of the top and bottom of the header
    :vartype SFDU_HEADER: tuple
    :cvar YY_FORMAT: Format of the datetimes for the YY field of the event line
    :vartype YY_FORMAT: str
    :cvar DOY_FORMAT: Format of the datetimes for the DOY field of the event line
    :vartype DOY_FORMAT: str
    :cvar HHMM_FORMAT: Format of the datetimes for the HHMM field of the event line
    :vartype HHMM_FORMAT: str
    """

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

    def __init__(self, filename: str, header_hash: dict=None):
      """
      Initialize an DsnStationAllocationFileEncoder which is meant to read output from the AERIE database and encode it into a report file.

      :param filename: Filepath to Encoded file.
      :type filename: str
      :param header_hash: Dictionary of header values
      :type header_hash: dict
      """

      logger = logging.getLogger(__name__)
      logger.info("Opening DSN Station Allocation file for Encoding: %s", filename)
      super(DsnStationAllocationFileEncoder, self).__init__(filename, header_hash)

    def cast_event(self, event_hash: dict) -> str:
        """
        Checks the validity of the formatting of a user inputted event dictionary

        :param event_hash: Contains field information for the event
        :type event_hash: dict
        :return: True on valid, False on non valid
        :rtype: bool
        """

        super(DsnStationAllocationFileEncoder, self).cast_event(event_hash)

        translated_event = event_hash

        translated_event["SOA"] = translated_event["SOA"].strftime(self.HHMM_FORMAT)
        translated_event["BOT"] = translated_event["BOT"].strftime(self.HHMM_FORMAT)
        translated_event["EOT"] = translated_event["EOT"].strftime(self.HHMM_FORMAT)
        translated_event["EOA"] = translated_event["EOA"].strftime(self.HHMM_FORMAT)
        translated_event["PASS"] = str(translated_event["PASS"]).zfill(4)

        r = ""
        looper = iter(self.EVENT_KEYS)

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

    """
    Manages state for encoding a DSN Station Allocaation report file

    :ivar __connection_string: URL to the Hasura database
    :vartype __connection_string:
    "cvar INSERT_ACTIVITY_QUERY: Template query for inserting activities into AERIE
    :vartype INSERT_ACTIVITY_QUERY: str
    "cvar READ_PLAN_QUERY: Template query for reading plan information from AERIE
    :vartype READ_PLAN_QUERY: str
    "cvar READ_ACTIVITY_QUERY: Template query for reading activies from AERIE plan
    :vartype READ_ACTIVITY_QUERY: str
    "cvar DEFAULT_CONNECTION_STRING: Default connection string of Localhost if an alternate is not provided
    :vartype DEFAULT_CONNECTION_STRING: str
    """

    INSERT_ACTIVITY_QUERY = 'mutation InsertActivities($activities: [activity_directive_insert_input!]!) {insert_activity_directive(objects: $activities) {returning {id name } } }'
    READ_PLAN_QUERY = 'query getPlan($id: Int) {plan(where: {id: {_eq: $id}}) {id name model_id start_time duration} }'
    READ_ACTIVITY_QUERY = 'query getActivity($type: String, $plan_id: Int) {activity_directive(where: {type: {_like: $type}, plan_id: {_eq: $plan_id}}) {start_offset id tags type name metadata arguments} }'

    DEFAULT_CONNECTION_STRING = 'http://localhost:8080/v1/graphql'

    def __init__(self, connection_string: str=DEFAULT_CONNECTION_STRING):
        """
        Initialize an GqlInterface which retreives and inserts information into the AERIE DB.

        :param connection_string: Connection string to Hasura GraphQL DB
        :type connection_string: str
        """

        logger = logging.getLogger(__name__)

        self.__connection_string = connection_string

        logger.info("GraphQL Config: api_conn: %s", connection_string)

    def get_plan_info_from_id(self, plan_id: int) -> tuple[datetime.datetime, datetime.datetime]:
        """
        Retreives the start and end times of an AERIE plan

        :param plan_id: plan_id for the AERIE plan to read
        :type plan_id: int
        :return: tuple of the plan start and plan end times in python datetime objects
        :rtype: tuple
        """
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

        # Convert AERIE Duration string to end time using the start time
        H, MM, SSZ = plan["duration"].split(":")
        plan_end = plan_start + datetime.timedelta(hours=int(H), minutes=int(MM), seconds=float(SSZ))

        logger.info("Found plan \"%s\", starting at %s, ending at %s", plan_name, plan_start.isoformat(), plan_end.isoformat())

        return plan_start, plan_end

    def mux_files(self, decoders: list, plan_id) -> dict:
        """
        Accepts a list of decoders and retreives activity information from them. This information is then constructed
        into AERIE activities and returned in pythonic generator fashion.

        :param decoders: list of Decoder types that will be parsed for information
        :type decoders: list
        :param plan_id: plan_id for the AERIE plan to insert into
        :type plan_id: int
        :return: None
        :rtype: None
        """

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

    def demux_files(self, saf_encoder: DsnStationAllocationFileEncoder, vp_encoder: DsnViewPeriodPredLegacyEncoder, plan_id: int) -> None:
      """
      Accepts two Encoders and writes activity information to them from the AERIE DB.

      :param saf_encoder: list of Decoder types that will be parsed for information
      :type saf_encoder: DsnStationAllocationFileEncoder
      :param vp_encoder: plan_id for the AERIE plan to insert into
      :type vp_encoder: DsnViewPeriodPredLegacyEncoder
      :param plan_id: plan_id for the AERIE plan to read from
      :type plan_id: int
      :return: None
      :rtype: None
      """

      logger = logging.getLogger(__name__)

      plan_start, plan_end = self.get_plan_info_from_id(plan_id)
      activities = self.read_activities(plan_id, "DSN_Track")

      c = []
      for dsn_track_activity in activities["data"]["activity_directive"]:
        c.append(self.convert_gql_to_dsn_stationallocation(dsn_track_activity))
      c = sorted(c, key=lambda event: event['SOA'])
      saf_encoder.cast(c)

      activities = self.read_activities(plan_id, "DSN_View_Period")

      c = []
      for dsn_view_activity in activities["data"]["activity_directive"]:
        c.append(self.convert_gql_to_dsn_viewperiod(plan_start, dsn_view_activity))
      c = sorted(c, key=lambda event: event['TIME'])
      vp_encoder.cast(c)

    def create_activities(self, activities: list) -> None:
        """
        Inserts a list of activities into the AERIE DB

        :param activities: List of activities to insert into AERIE
        :type activities: list
        :return: None
        :rtype: None
        """

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

    def read_activities(self, plan_id: int, activity_type: str=None) -> dict:
      """
      Read activities of a certain type from AERIE DB

      :param plan_id: plan_id for the AERIE plan to read activities from
      :type plan_id: int
      :param activity_type: Name of the activity to filter for
      :type activity_type: str
      :return: Response object from Hasura DB
      :rtype: dict
      """

      assert isinstance(plan_id, (type(None), int))
      assert isinstance(activity_type, (type(None), str))

      logger = logging.getLogger(__name__)
      logger.debug("Reading activities for: plan_id %s, activity_type %s", plan_id, activity_type)

      response = requests.post(
        url=self.__connection_string,
        json={
          'query': self.READ_ACTIVITY_QUERY,
          'variables': {
            'plan_id': plan_id,
            'type': activity_type
          },
        },
        verify=False
      )
      r = response.json()
      logger.debug("read_activities: %s", json.dumps(r, indent=2))
      return r

    def read_plan(self, id: int):
      """
      Read plan metadata from AERIE for a plan id

      :param id: plan id for the AERIE plan to read plan metadata from
      :type id: int
      :return: Response object from Hasura DB
      :rtype: dict
      """

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
        """
        Convert an absolute event time to an AERIE plan offset so it can be displayed properly.

        :param plan_start_time: Start time of the plan
        :type plan_start_time: datetime
        :param activity_start_time: Start time of the activity
        :type activity_start_time: datetime
        :return: Formatted string for AERIE of the duration from the start time of the plan
        :rtype: str
        """

        start_offset_seconds = datetime.timedelta.total_seconds(activity_start_time - plan_start_time)
        hours_offset = start_offset_seconds // 3600
        start_offset_seconds -= hours_offset * 3600
        minutes_offset = start_offset_seconds // 60
        start_offset_seconds -= minutes_offset * 60

        start_offset = '{}:{}:{}'.format(int(hours_offset), int(minutes_offset), start_offset_seconds)

        return start_offset

    @classmethod
    def convert_to_aerie_duration(cls, activity_start_time: datetime.datetime, activity_end_time: datetime.datetime) -> int:
        """
        Convert a start and end datetime to duration in microseconds which the AERIE Misison Model simulator uses.

        :param activity_start_time: Start time of the activity
        :type activity_start_time: datetime
        :param activity_end_time: End time of the activity
        :type activity_end_time: datetime
        :return: Duration in microseconds
        :rtype: int
        """
        return int((activity_end_time - activity_start_time).total_seconds() * 1e6)

    @classmethod
    def convert_dsn_viewperiod_to_gql(cls, plan_id: int, plan_start_time: datetime.datetime, header_segs: dict, event_segs: dict) -> dict:
        """
        Convert the output of the DsnViewPeriodPredDecoder event and header dictionary to a GQL query

        :param plan_id: plan_id for the AERIE plan to insert into
        :type plan_id: int
        :param plan_start_time: Start time of the plan
        :type plan_start_time: datetime
        :param header_segs: Header key / value dictionary from the Decoder object, this is used to populate activity fields
        :type header_segs: dict
        :param event_segs: Event key / value dictionary from the Decoder object, this is used to populate activity fields
        :type event_segs: dict
        :return: GQL Query object to send to AERIE Hasura DB
        :rtype: dict
        """

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
        rtlt = int(event_segs["RTLT"].total_seconds()) * 1e6

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
                'rtlt': rtlt
            },
            'plan_id': plan_id,
            'name': 'DSN View Period',
            'start_offset': start_offset,
            'type': 'DSN_View_Period'
        }

    @classmethod
    def convert_dsn_stationallocation_to_gql(cls, plan_id: int, plan_start_time: datetime.datetime, header_segs: dict, event_segs: dict) -> dict:
        """
        Convert the output of the DsnStationAllocationFileDecoder event and header dictionary to a GQL query
    
        :param plan_id: plan_id for the AERIE plan to insert into
        :type plan_id: int
        :param plan_start_time: Start time of the plan
        :type plan_start_time: datetime
        :param header_segs: Header key / value dictionary from the Decoder object, this is used to populate activity fields
        :type header_segs: dict
        :param event_segs: Event key / value dictionary from the Decoder object, this is used to populate activity fields
        :type event_segs: dict
        :return: GQL Query object to send to AERIE Hasura DB
        :rtype: dict
        """

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
        project_id = event_segs["PROJECT_ID"]
        pass_number = int(event_segs["PASS"])
        config_code = event_segs["CONFIG_CODE"]
        soe_flag = event_segs["SOE_FLAG"]
        work_code_catagory = event_segs["WORK_CODE_CAT"]
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
                'project_ID': project_id,
                'pass_number': pass_number,
                'config_code': config_code,
                'soe_flag': soe_flag,
                'work_code_catagory': work_code_catagory,
                'duration_of_activity': duration_of_activity,
                'start_of_track': start_of_track,
                'duration_of_track': duration_of_track
                },
            'plan_id': plan_id,
            'name': 'DSN Track',
            'start_offset': start_offset,
            'type': 'DSN_Track'
        }

    @classmethod
    def convert_gql_to_dsn_stationallocation(cls, dsn_track_activity: dict) -> dict:
      """
      Convert the output of a GQL Query to a StationAllocationEncoder key / value dict

      :param dsn_track_activity: GQL response object from self.read_activities
      :type dsn_track_activity: dict
      :return: Event key / value dict for station allocation encoders
      :rtype: dict
      """

      start_offset = dsn_track_activity["start_offset"]
      arguments = dsn_track_activity["arguments"]

      soa = datetime.datetime.fromisoformat(arguments["SOA"])
      change_indicator = ""
      yy = soa.strftime(DsnStationAllocationFileEncoder.YY_FORMAT)
      doy = soa.strftime(DsnStationAllocationFileEncoder.DOY_FORMAT)
      bot = datetime.datetime.fromisoformat(arguments["BOT"])
      eot = datetime.datetime.fromisoformat(arguments["EOT"])
      eoa = datetime.datetime.fromisoformat(arguments["EOA"])
      antenna_id = arguments["antenna_ID"]
      project_id = arguments["project_ID"]
      description = arguments["pass_type"]
      pass_num = arguments["pass_number"]
      config_code = arguments["config_code"]
      soe_flag = arguments["soe_flag"]
      work_code_cat = arguments["work_code_catagory"]
      relate = ""

      return {
        "CHANGE_INDICATOR": change_indicator,
        "YY": yy,
        "DOY": doy,
        "SOA": soa,
        "BOT": bot,
        "EOT": eot,
        "EOA": eoa,
        "ANTENNA_ID": antenna_id,
        "PROJECT_ID": project_id,
        "DESCRIPTION": description,
        "PASS": pass_num,
        "CONFIG_CODE": config_code,
        "SOE_FLAG": soe_flag,
        "WORK_CODE_CAT": work_code_cat,
        "RELATE": relate
      }

    @classmethod
    def convert_gql_to_dsn_viewperiod(cls, plan_start_time: datetime.datetime, dsn_view_activity: dict) -> dict:
      """
      Convert the output of a GQL Query to a ViewPeriodEncoder key / value dict

      :param dsn_track_activity: GQL response object from self.read_activities
      :type dsn_track_activity: dict
      :return: Event key / value dict for station allocation encoders
      :rtype: dict
      """

      start_offset = dsn_view_activity["start_offset"]
      hours, minutes, seconds = start_offset.split(":")
      time = plan_start_time + datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=float(seconds))

      arguments = dsn_view_activity["arguments"]
      event = arguments["viewperiod_event"]
      spacecraft_identifier = arguments["dsn_spacecraft_ID"]
      station_identifier = arguments["station_identifier"]
      pass_number = arguments["pass_number"]
      azimuth = arguments["azimuth_degrees"]
      elevation = arguments["elevation_degrees"]
      az_lha_x = arguments["lha_X_degrees"]
      el_dec_y = arguments["dec_Y_degrees"]
      rtlt = datetime.timedelta(microseconds=arguments["rtlt"])

      return {
        "TIME": time,
        "EVENT": event,
        "SPACECRAFT_IDENTIFIER": spacecraft_identifier,
        "STATION_IDENTIFIER": station_identifier,
        "PASS": pass_number,
        "AZIMUTH": azimuth,
        "ELEVATION": elevation,
        "AZ_LHA_X": az_lha_x,
        "EL_DEC_Y": el_dec_y,
        "RTLT": rtlt
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



    #GqlInterface(0, datetime.datetime.now()).read_plan(id=9)
    #print(GqlInterface().read_activities(23, "DSN_View_Period"))
    #GqlInterface(0, datetime.datetime.now()).mux_files([vp_file, saf_file])
