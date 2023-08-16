import io
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from libaerie.products.product_parser import DsnViewPeriodPredLegacyDecoder, DsnStationAllocationFileDecoder, DsnViewPeriodPredLegacyEncoder,DsnStationAllocationFileEncoder, GqlInterface


def test_saf_decoder_encoder(saf_content):

    saf_file = DsnStationAllocationFileDecoder(io.StringIO(saf_content))
    saf_header = saf_file.read_header()
    saf_iter = saf_file.parse()

    saf_out = io.StringIO()
    close = saf_out.close
    saf_out.close = lambda: None

    saf_encoder = DsnStationAllocationFileEncoder(saf_out, saf_header)
    saf_encoder.cast(saf_iter)

    try:
        assert(saf_out.getvalue() == saf_content)
    finally:
        close()


def test_vp_decoder_encoder(vp_content):

    vp_file = DsnViewPeriodPredLegacyDecoder(io.StringIO(vp_content))
    vp_header = vp_file.read_header()
    vp_iter = vp_file.parse()

    vp_out = io.StringIO()
    close = vp_out.close
    vp_out.close = lambda: None

    vp_encoder = DsnViewPeriodPredLegacyEncoder(vp_out, vp_header)
    vp_encoder.cast(vp_iter)

    try:
        assert(vp_out.getvalue() == vp_content)
    finally:
        close()
