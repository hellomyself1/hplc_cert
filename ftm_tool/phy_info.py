# -*- coding: utf-8 -*-
from macro_const import RoboCopyMarco, ModulationMarco, PbNumMarco, CodingRateMarco
from macro_const import TmiMarco, PbSizeMarco, ExtmiMarco, ProtoMarco, InterMarco, RoboMarco
from macro_const import ValidToneMarco, FcSymNumMarco, RateMarco, StartValidToneMarco, EndValidToneMarco, FdRmsMaxMarco


class TmiPbNum:
    def __init__(self):
        pass

    def tmi_get_pb_num(self, tmi, extmi=0):
        if tmi == TmiMarco.TMI_0 or tmi == TmiMarco.TMI_1 or (TmiMarco.TMI_7 <= tmi <= TmiMarco.TMI_10):
            return PbSizeMarco.PB_NUM_520
        elif TmiMarco.TMI_2 <= tmi <= TmiMarco.TMI_6:
            return PbSizeMarco.PB_NUM_136
        elif tmi == TmiMarco.TMI_11 or tmi == TmiMarco.TMI_12:
            return PbSizeMarco.PB_NUM_264
        elif tmi == TmiMarco.TMI_13 or tmi == TmiMarco.TMI_14:
            return PbSizeMarco.PB_NUM_72
        elif tmi == TmiMarco.TMI_MAX:
            if ExtmiMarco.EXTMI_1 <= extmi <= ExtmiMarco.EXTMI_6:
                return PbSizeMarco.PB_NUM_520
            elif ExtmiMarco.EXTMI_10 <= extmi <= ExtmiMarco.EXTMI_14:
                return PbSizeMarco.PB_NUM_136
            else:
                return 0
        else:
            return 0


class ToneMap:
    def __init__(self):
        self.pb_size, self.robo_cnt, self.modulation, self.coding_rate_idx, self.max_pb_num = 0, 0, 0, 0, 0

    def tone_table(self, pb_size, robo_cnt, modulation, coding_rate_idx, max_pb_num):
        self.pb_size = pb_size
        self.robo_cnt = robo_cnt
        self.modulation = modulation
        self.coding_rate_idx = coding_rate_idx
        self.max_pb_num = max_pb_num


class PlcBandInfo:
    def __init__(self):
        self.valid_tone_number, self.fc_sym_num, self.rate_type = 0, 0, 0
        self.fd_rms_max, self.start_tone, self.end_tone = 0, 0, 0
        self.band_id = 0

    def band_info(self, valid_tone_num, fc_sym_num, rate_type, fd_rms_max, start_tone, end_tone):
        self.valid_tone_number = valid_tone_num
        self.fc_sym_num = fc_sym_num
        self.rate_type = rate_type
        self.fd_rms_max = fd_rms_max
        self.start_tone = start_tone
        self.end_tone = end_tone


class RoboInter:
    def __init__(self):
        self.robo_cpy, self.inter_num = 0, 0

    def robo_inter(self, robo_cpy, inter_num):
        self.robo_cpy = robo_cpy
        self.inter_num = inter_num


class PhyDataInfo:
    def __init__(self):
        # sg tonemap table
        self.sg_tonemap_tbl = []
        self.sg_ext_tonemap_tbl = []
        self.sg_hwband_tbl = []
        self.sg_robo_inter_tbl = []

        self.init_hwband_info()
        self.init_sg_tone_table()
        self.init_sg_ext_tone_table()
        self.init_robo_inter_table()

    def init_robo_inter_table(self):
        for i in range(6):
            self.sg_robo_inter_tbl.append(RoboInter())

        # idx 0
        self.sg_robo_inter_tbl[0].robo_num = RoboCopyMarco.ROBO_COPY_1
        self.sg_robo_inter_tbl[0].inter_num = InterMarco.INTER_1

        # idx 1
        self.sg_robo_inter_tbl[1].robo_num = RoboCopyMarco.ROBO_COPY_2
        self.sg_robo_inter_tbl[1].inter_num = InterMarco.INTER_8

        # idx 2
        self.sg_robo_inter_tbl[2].robo_num = RoboCopyMarco.ROBO_COPY_4
        self.sg_robo_inter_tbl[2].inter_num = InterMarco.INTER_8

        # idx 3
        self.sg_robo_inter_tbl[3].robo_num = RoboCopyMarco.ROBO_COPY_5
        self.sg_robo_inter_tbl[3].inter_num = InterMarco.INTER_10

        # idx 4
        self.sg_robo_inter_tbl[4].robo_num = RoboCopyMarco.ROBO_COPY_7
        self.sg_robo_inter_tbl[4].inter_num = InterMarco.INTER_14

        # idx 5
        self.sg_robo_inter_tbl[5].robo_num = RoboCopyMarco.ROBO_COPY_11
        self.sg_robo_inter_tbl[5].inter_num = InterMarco.INTER_11

    def init_hwband_info(self):
        for i in range(TmiMarco.TMI_MAX):
            self.sg_hwband_tbl.append(PlcBandInfo())

        # full band
        self.sg_hwband_tbl[0].valid_tone_number = ValidToneMarco.VALID_TONE_BAND_0
        self.sg_hwband_tbl[0].fc_sym_num = FcSymNumMarco.FC_SYM_NUM_4
        self.sg_hwband_tbl[0].rate_type = RateMarco.RATE_0
        self.sg_hwband_tbl[0].fd_rms_max = FdRmsMaxMarco.RMS_MAX_58
        self.sg_hwband_tbl[0].start_tone = StartValidToneMarco.START_VALID_TONE_BAND_0
        self.sg_hwband_tbl[0].end_tone = EndValidToneMarco.END_VALID_TONE_BAND_0

        # low band
        self.sg_hwband_tbl[1].valid_tone_number = ValidToneMarco.VALID_TONE_BAND_1
        self.sg_hwband_tbl[1].fc_sym_num = FcSymNumMarco.FC_SYM_NUM_12
        self.sg_hwband_tbl[1].rate_type = RateMarco.RATE_0
        self.sg_hwband_tbl[1].fd_rms_max = FdRmsMaxMarco.RMS_MAX_63
        self.sg_hwband_tbl[1].start_tone = StartValidToneMarco.START_VALID_TONE_BAND_1
        self.sg_hwband_tbl[1].end_tone = EndValidToneMarco.END_VALID_TONE_BAND_1

        # high band
        self.sg_hwband_tbl[2].valid_tone_number = ValidToneMarco.VALID_TONE_BAND_4
        self.sg_hwband_tbl[2].fc_sym_num = FcSymNumMarco.FC_SYM_NUM_4
        self.sg_hwband_tbl[2].rate_type = RateMarco.RATE_0
        self.sg_hwband_tbl[2].fd_rms_max = FdRmsMaxMarco.RMS_MAX_60
        self.sg_hwband_tbl[2].start_tone = StartValidToneMarco.START_VALID_TONE_BAND_4
        self.sg_hwband_tbl[2].end_tone = EndValidToneMarco.END_VALID_TONE_BAND_4

    def init_sg_tone_table(self):
        for i in range(TmiMarco.TMI_MAX):
            self.sg_tonemap_tbl.append(ToneMap())
        # idx 0
        self.sg_tonemap_tbl[0].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[0].robo_cnt = RoboCopyMarco.ROBO_COPY_4
        self.sg_tonemap_tbl[0].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[0].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[0].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 1
        self.sg_tonemap_tbl[1].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[1].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_tonemap_tbl[1].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[1].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[1].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 2
        self.sg_tonemap_tbl[2].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_tonemap_tbl[2].robo_cnt = RoboCopyMarco.ROBO_COPY_5
        self.sg_tonemap_tbl[2].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[2].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[2].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 3
        self.sg_tonemap_tbl[3].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_tonemap_tbl[3].robo_cnt = RoboCopyMarco.ROBO_COPY_11
        self.sg_tonemap_tbl[3].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[3].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[3].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 4
        self.sg_tonemap_tbl[4].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_tonemap_tbl[4].robo_cnt = RoboCopyMarco.ROBO_COPY_11
        self.sg_tonemap_tbl[4].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[4].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[4].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 5
        self.sg_tonemap_tbl[5].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_tonemap_tbl[5].robo_cnt = RoboCopyMarco.ROBO_COPY_11
        self.sg_tonemap_tbl[5].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[5].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[5].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 6
        self.sg_tonemap_tbl[6].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_tonemap_tbl[6].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[6].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[6].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[6].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 7
        self.sg_tonemap_tbl[7].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[7].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[7].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[7].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[7].max_pb_num = PbNumMarco.MAX_PB_NUM_3

        # idx 8
        self.sg_tonemap_tbl[8].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[8].robo_cnt = RoboCopyMarco.ROBO_COPY_4
        self.sg_tonemap_tbl[8].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[8].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[8].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 9
        self.sg_tonemap_tbl[9].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[9].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[9].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[9].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[9].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 10
        self.sg_tonemap_tbl[10].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_tonemap_tbl[10].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_tonemap_tbl[10].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[10].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[10].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 11
        self.sg_tonemap_tbl[11].pb_size = PbSizeMarco.PB_NUM_264
        self.sg_tonemap_tbl[11].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[11].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[11].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[11].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 12
        self.sg_tonemap_tbl[12].pb_size = PbSizeMarco.PB_NUM_264
        self.sg_tonemap_tbl[12].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[12].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[12].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[12].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 13
        self.sg_tonemap_tbl[13].pb_size = PbSizeMarco.PB_NUM_72
        self.sg_tonemap_tbl[13].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[13].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_tonemap_tbl[13].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[13].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 14
        self.sg_tonemap_tbl[14].pb_size = PbSizeMarco.PB_NUM_72
        self.sg_tonemap_tbl[14].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_tonemap_tbl[14].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_tonemap_tbl[14].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_tonemap_tbl[14].max_pb_num = PbNumMarco.MAX_PB_NUM_4

    def init_sg_ext_tone_table(self):
        for i in range(ExtmiMarco.EXTMI_MAX):
            self.sg_ext_tonemap_tbl.append(ToneMap())
        # idx 0
        self.sg_ext_tonemap_tbl[0].pb_size = PbSizeMarco.PB_SIZE_INV
        self.sg_ext_tonemap_tbl[0].robo_cnt = RoboCopyMarco.ROBO_COPY_4
        self.sg_ext_tonemap_tbl[0].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_ext_tonemap_tbl[0].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[0].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 1
        self.sg_ext_tonemap_tbl[1].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[1].robo_cnt = RoboCopyMarco.ROBO_COPY_1
        self.sg_ext_tonemap_tbl[1].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[1].coding_rate_idx = CodingRateMarco.CODING_RATE_16_18
        self.sg_ext_tonemap_tbl[1].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 2
        self.sg_ext_tonemap_tbl[2].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[2].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_ext_tonemap_tbl[2].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[2].coding_rate_idx = CodingRateMarco.CODING_RATE_16_18
        self.sg_ext_tonemap_tbl[2].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 3
        self.sg_ext_tonemap_tbl[3].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[3].robo_cnt = RoboCopyMarco.ROBO_COPY_1
        self.sg_ext_tonemap_tbl[3].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[3].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[3].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 4
        self.sg_ext_tonemap_tbl[4].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[4].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_ext_tonemap_tbl[4].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[4].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[4].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 5
        self.sg_ext_tonemap_tbl[5].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[5].robo_cnt = RoboCopyMarco.ROBO_COPY_4
        self.sg_ext_tonemap_tbl[5].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[5].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[5].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 6
        self.sg_ext_tonemap_tbl[6].pb_size = PbSizeMarco.PB_NUM_520
        self.sg_ext_tonemap_tbl[6].robo_cnt = RoboCopyMarco.ROBO_COPY_1
        self.sg_ext_tonemap_tbl[6].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_ext_tonemap_tbl[6].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[6].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 7
        self.sg_ext_tonemap_tbl[7].pb_size = PbSizeMarco.PB_SIZE_INV
        self.sg_ext_tonemap_tbl[7].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_ext_tonemap_tbl[7].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_ext_tonemap_tbl[7].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[7].max_pb_num = PbNumMarco.MAX_PB_NUM_3

        # idx 8
        self.sg_ext_tonemap_tbl[8].pb_size = PbSizeMarco.PB_SIZE_INV
        self.sg_ext_tonemap_tbl[8].robo_cnt = RoboCopyMarco.ROBO_COPY_4
        self.sg_ext_tonemap_tbl[8].modulation = ModulationMarco.MODULATION_BPSK
        self.sg_ext_tonemap_tbl[8].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[8].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 9
        self.sg_ext_tonemap_tbl[9].pb_size = PbSizeMarco.PB_SIZE_INV
        self.sg_ext_tonemap_tbl[9].robo_cnt = RoboCopyMarco.ROBO_COPY_7
        self.sg_ext_tonemap_tbl[9].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_ext_tonemap_tbl[9].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[9].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 10
        self.sg_ext_tonemap_tbl[10].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_ext_tonemap_tbl[10].robo_cnt = RoboCopyMarco.ROBO_COPY_5
        self.sg_ext_tonemap_tbl[10].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[10].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[10].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 11
        self.sg_ext_tonemap_tbl[11].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_ext_tonemap_tbl[11].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_ext_tonemap_tbl[11].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_ext_tonemap_tbl[11].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[11].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 12
        self.sg_ext_tonemap_tbl[12].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_ext_tonemap_tbl[12].robo_cnt = RoboCopyMarco.ROBO_COPY_2
        self.sg_ext_tonemap_tbl[12].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[12].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[12].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 13
        self.sg_ext_tonemap_tbl[13].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_ext_tonemap_tbl[13].robo_cnt = RoboCopyMarco.ROBO_COPY_1
        self.sg_ext_tonemap_tbl[13].modulation = ModulationMarco.MODULATION_QPSK
        self.sg_ext_tonemap_tbl[13].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[13].max_pb_num = PbNumMarco.MAX_PB_NUM_4

        # idx 14
        self.sg_ext_tonemap_tbl[14].pb_size = PbSizeMarco.PB_NUM_136
        self.sg_ext_tonemap_tbl[14].robo_cnt = RoboCopyMarco.ROBO_COPY_1
        self.sg_ext_tonemap_tbl[14].modulation = ModulationMarco.MODULATION_16QAM
        self.sg_ext_tonemap_tbl[14].coding_rate_idx = CodingRateMarco.CODING_RATE_1_2
        self.sg_ext_tonemap_tbl[14].max_pb_num = PbNumMarco.MAX_PB_NUM_4

    def phy_get_tmi_param(self, proto, tmi, extmi):
        if proto == ProtoMarco.PROTO_SG:
            if tmi == TmiMarco.TMI_MAX and extmi < ExtmiMarco.EXTMI_MAX:
                return self.sg_ext_tonemap_tbl[extmi]
            elif tmi < TmiMarco.TMI_MAX:
                return self.sg_tonemap_tbl[tmi]
            else:
                return None
        else:
            print("proto %d is not support" % proto)
            return None

    def phy_get_robo_inter(self, robo_cnt):
        for i in range(6):
            if self.sg_robo_inter_tbl[i].robo_cpy == robo_cnt:
                return self.sg_robo_inter_tbl[i].inter_num
        return 'error'

    @staticmethod
    def phy_get_coding_rate(coding_rate_idx):
        if coding_rate_idx == CodingRateMarco.CODING_RATE_1_2:
            return 0.5
        elif coding_rate_idx == CodingRateMarco.CODING_RATE_16_18:
            return 16/18
        else:
            assert 0

    @staticmethod
    def iot_ceil(numerator, denumerator):
        return (numerator + (denumerator - 1)) / denumerator

    ''''
    / * expression:
      * carrier_num: band0, 411. band1, 131.
      * valid_carrier_num = floor(carrier_num / internum, 1) * internum
      * symbol_num =
      * (pbsize * 8 * copy_num) / modulation_bits / turborate / valid_carrier_num
      * /
    '''

    def phy_calu_symbol_num_per_pb(self, pbsize, robo, turborate, modulation, valid_tone_num, internum):
        if valid_tone_num / internum * internum != 0:
            t1 = valid_tone_num / internum * internum
        else:
            t1 = valid_tone_num
        return self.iot_ceil(pbsize * 8 * robo, turborate * modulation * t1)

    def phy_get_symbol_num(self, proto, hw_band_id, tmi, extmi=0):
        tmi_param = self.phy_get_tmi_param(proto, tmi, extmi)
        pb_size = TmiPbNum.tmi_get_pb_num(tmi, extmi)
        inter_num = self.phy_get_robo_inter(tmi_param.robo_cnt)
        coding_rate = self.phy_get_coding_rate(tmi_param.coding_rate_idx)
        symbol_num = self.phy_calu_symbol_num_per_pb(pb_size, tmi_param.robo_cnt, coding_rate, tmi_param.modulation,
                                                     self.sg_hwband_tbl[hw_band_id].valid_tone_num, inter_num)
        if symbol_num > 511:
            symbol_num = 0
        return symbol_num

    """"
    / *expression:
    *fl = (symnum * 1024 + GI * (symnum - 2) + 2 * 458) / 25
    * /
    """

    @staticmethod
    def frame_length_per_pb_sg(symbol_num, gi):
        fl_ppb = ((symbol_num * 1024 + gi * (symbol_num - 2) + 2 * RoboMarco.GI_SG_ROBO_LONG) / 25)
        return fl_ppb

    def phy_calu_fl_per_pb(self, proto, hw_band_id, tmi, extmi=0):
        symbol_num = self.phy_get_symbol_num(proto, hw_band_id, tmi, extmi)
        fl_ppb = self.frame_length_per_pb_sg(symbol_num, RoboMarco.GI_SG_ROBO_SHORT)
        return fl_ppb



