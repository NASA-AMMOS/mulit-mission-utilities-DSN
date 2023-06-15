import re
import datetime
import os
import logging


class DsnViewPeriodPredLegacyDecoder(object):

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j/%H:%M:%S"

    EVENT_RECORD_REGEX = "(?P<Time>.{15}).(?P<Event>.{16}).(?P<Spacecraft_identifier>.{3}).(?P<Station_identifier>.{2}).(?P<Pass>.{4}).(?P<Azimuth>.{5}).(?P<Elevation>.{5}).(?P<AZ_LHA_X>.{5}).(?P<EL_DEC_Y>.{5}).(?P<RTLT>.{10})"

    def __init__(self, filename: str):
        logger = logging.getLogger(__name__)

        if not os.path.isfile(filename):
            logging.error("DSN Viewperiod file not found: '%s'", filename)
            raise FileNotFoundError("DSN Viewperiod file not found: %s" % filename)

        logger.info("Opening DSN Viewperiod file: %s", filename)
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

    def parse(self):

        logger = logging.getLogger(__name__)

        self.header_hash = self.parse_header([next(self._fh) for _ in range(11)])

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
            yield r

    @classmethod
    def rtlt_to_timedelta(cls, rtlt_dur_str: str) -> datetime.timedelta:

        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


class DsnStationAllocationFileDecoder(object):

    HEADER_TIME_FORMAT = "%Y-%jT%H:%M:%S"
    EVENT_TIME_FORMAT = "%y %j%H%M"

    EVENT_RECORD_REGEX = "(?P<Change_indictor>.)(?P<YYDOY>.{6}).(?P<SOA>.{4}).(?P<BOT>.{4}).(?P<EOT>.{4}).(?P<EOA>.{4}).(?P<Antenna_id>.{6}).(?P<Project_id>.{5}).(?P<Description>.{16}).(?P<Pass>.{4}).(?P<Config_code>.{6})(?P<SOE_flag>.).(?P<Work_code_cat>.{3}).(?P<Relate>.)."

    def __init__(self, filename: str):
        logger = logging.getLogger(__name__)

        if not os.path.isfile(filename):
            logging.error("DSN Station Allocation file not found: '%s'", filename)
            raise FileNotFoundError("DSN Station Allocation file not found: %s" % filename)

        logger.info("Opening DSN Station Allocation file: %s", filename)
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

    def parse(self):

        logger = logging.getLogger(__name__)

        self.header_hash = self.parse_header([next(self._fh) for _ in range(11)])

        for line in self._fh:
            r = self.parse_line(line)


            # We need to do a check here, End of Track and End of Activity can roll over to the end of the day

            if r["SOA"] > r["EOT"]:
                r["EOT"] = datetime.datetime.strptime(r["YYDOY"] + r["EOT"], self.EVENT_TIME_FORMAT) + datetime.timedelta(days=1)
            else:
                r["EOT"] = datetime.datetime.strptime(r["YYDOY"] + r["EOT"], self.EVENT_TIME_FORMAT)

            if r["SOA"] > r["EOA"]:
                r["EOA"] = datetime.datetime.strptime(r["YYDOY"] + r["EOA"], self.EVENT_TIME_FORMAT) + datetime.timedelta(days=1)
            else:
                r["EOA"] = datetime.datetime.strptime(r["YYDOY"] + r["EOA"], self.EVENT_TIME_FORMAT)

            r["SOA"] = datetime.datetime.strptime(r["YYDOY"]+r["SOA"], self.EVENT_TIME_FORMAT)
            r["BOT"] = datetime.datetime.strptime(r["YYDOY"]+r["BOT"], self.EVENT_TIME_FORMAT)

            r["Project_id"] = r["Project_id"].strip()
            r["Description"] = r["Description"].strip()
            r["Pass"] = int(r["Pass"])
            r["Config_code"] = r["Config_code"].strip()

            logger.debug("Parsed DSN Viewperiod event: %s", r)
            yield r

    @classmethod
    def rtlt_to_timedelta(cls, rtlt_dur_str: str) -> datetime.timedelta:

        hh, mm, ssz = rtlt_dur_str.split(":", 3)
        hh, mm, ssz = int(hh), int(mm), float(ssz)

        return datetime.timedelta(hours=hh, minutes=mm, seconds=ssz)


def parse_shadow_line(plan_start_formatted, line):
    date_format = '%Y-%j/%H:%M:%S'

    start_time, stop_time = re.findall("\d{4}[-]\d{3}[/]\d{2}[:]\d{2}[:]\d{2}", line)
    activity_start_formatted = datetime.datetime.strptime(start_time, date_format)
    start_offset_seconds = datetime.timedelta.total_seconds(activity_start_formatted - plan_start_formatted)
    hours_offset = start_offset_seconds // 3600
    start_offset_seconds -= hours_offset * 3600
    minutes_offset = start_offset_seconds // 60
    start_offset_seconds -= minutes_offset * 60

    start_offset = '{}:{}:{}'.format(int(hours_offset), int(minutes_offset), start_offset_seconds)
    # duration is in microseconds in Aerie UI, in min in shadow file
    duration = re.findall("\d{1,}[.]\d{3}", line)[0]
    duration = float(duration) * 6e7
    duration = int(duration)

    if "Penumbra" in line:
        shadow_type = "PENUMBRA"
    else:
        shadow_type = "UMBRA"

    return shadow_type, start_offset, duration


def parse_shadows(plan_start_formatted, plan_id=None, shadow_file_names=[]):
    shadow_activities = []

    for file_name in shadow_file_names:
        sc_id = re.findall("(MMS\d{1})", file_name)[0]
        name = "IN_SHADOW"

        with open(file_name) as f:
            for i in range(12):
                next(f)
            j = 0

            last_type, start_offset_total, duration_total = parse_shadow_line(plan_start_formatted, f.readline())

            for line in f:

                shadow_type, start_offset, duration = parse_shadow_line(plan_start_formatted, line)

                if last_type != shadow_type:
                    last_type = shadow_type
                    duration_total += duration
                    if start_offset_total is None:
                        start_offset_total = start_offset
                else:
                    shadow_activities.append({
                        'arguments': {
                            'scId': sc_id,
                            'in_shadow_duration': duration_total,
                            'shadowType': "IN_SHADOW"
                        },
                        'plan_id': plan_id,
                        'name': name,
                        'start_offset': start_offset_total,
                        'type': 'InShadow'
                    })
                    start_offset_total = None
                    duration_total = 0

            shadow_activities.append({
                'arguments': {
                    'scId': sc_id,
                    'in_shadow_duration': duration_total,
                    'shadowType': "IN_SHADOW"
                },
                'plan_id': plan_id,
                'name': name,
                'start_offset': start_offset_total,
                'type': 'InShadow'
            })

    return shadow_activities


if __name__ == "__main__":
    logging.basicConfig()
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for record in DsnViewPeriodPredLegacyDecoder("../../M20_20223_20284_TEST.VP").parse():
        pass

    for record in DsnStationAllocationFileDecoder("../../M20_20230_20272_TEST.SAF").parse():
        pass