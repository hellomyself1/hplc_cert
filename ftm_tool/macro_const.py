# -*- coding: utf-8 -*-

##########################################################
#                   protocol/bandid                      #
##########################################################


class ProtoMarco:
    PROTO_SG = 0
    PROTO_SPG = 3


class BandIdMarco:
    PROTO_BAND_ID_0 = 0
    PROTO_BAND_ID_1 = 1
    PROTO_BAND_ID_2 = 2
    PROTO_BAND_ID_3 = 3

##########################################################
#                    cert mode/all case                  #
##########################################################


class ModeMarco:
    # cert test command enter app layer transparent transfer tx mode, in this
    # mode, will send MSDU to uart.
    CERT_TEST_CMD_ENTER_APP_T_T = 0x01

    # cert test command enter app layer transparent transfer rx mode, in this
    # mode, will packing data received from the UART, sent to the PLC network
    # as a MSDU.
    CERT_TEST_CMD_ENTER_APP_T_R = 0x02

    # cert test command enter physical layer transparent transfer mode */
    CERT_TEST_CMD_ENTER_PHY_T = 0x03

    # cert test command for enter physical layer loopback mode */
    CERT_TEST_CMD_ENTER_PHY_LP = 0x04

    # cert test command for enter MAC layer transparent transfer mode */
    CERT_TEST_CMD_ENTER_MAC_T = 0x05

    # cert test command for set frequency band */
    CERT_TEST_CMD_SET_FB = 0x06

    # cert test command for set tonemask */
    CERT_TEST_CMD_SET_TM = 0x07


class AllCertCaseValue:
    ROOT_PROTOCON = 0
    # STA 协议一致性所有case
    ROOT_PROTOCON_STA_CHILD = 1
    # sta scan tmi band0/1/2/3
    ROOT_PROTOCON_STA_TMISCAN_B0 = 2
    ROOT_PROTOCON_STA_TMISCAN_B1 = 3
    ROOT_PROTOCON_STA_TMISCAN_B2 = 4
    ROOT_PROTOCON_STA_TMISCAN_B3 = 5
    # sta tonemask band0/1/2/3
    ROOT_PROTOCON_STA_TM_B0 = 6
    ROOT_PROTOCON_STA_TM_B1 = 7
    ROOT_PROTOCON_STA_TM_B2 = 8
    ROOT_PROTOCON_STA_TM_B3 = 9

    ROOT_PROTOCON_STA_MAX = ROOT_PROTOCON_STA_TM_B3 + 1

    # CCO 协议一致性所有case
    ROOT_PROTOCON_CCO_CHILD = 40
    # cco scan tmi band0/1/2/3
    ROOT_PROTOCON_CCO_TMISCAN_B0 = 41
    ROOT_PROTOCON_CCO_TMISCAN_B1 = 42
    ROOT_PROTOCON_CCO_TMISCAN_B2 = 43
    ROOT_PROTOCON_CCO_TMISCAN_B3 = 44
    # sta tonemask band0/1/2/3
    ROOT_PROTOCON_CCO_TM_B0 = 45
    ROOT_PROTOCON_CCO_TM_B1 = 46
    ROOT_PROTOCON_CCO_TM_B2 = 47
    ROOT_PROTOCON_CCO_TM_B3 = 48

    ROOT_PROTOCON_CCO_MAX = ROOT_PROTOCON_CCO_TM_B3 + 1

    # 通信性能测试
    ROOT_PERFORMANCE_CHILD = 80
    # white noise
    ROOT_PERFORMANCE_STA_WN_B1 = 81
    ROOT_PERFORMANCE_STA_WN_B2 = 82
    # anti-ppm
    ROOT_PERFORMANCE_STA_ANTIPPM_B1 = 83
    ROOT_PERFORMANCE_STA_ANTIPPM_B2 = 84
    # anti-attenuation
    ROOT_PERFORMANCE_STA_ANTIATT_B1 = 85
    ROOT_PERFORMANCE_STA_ANTIATT_B2 = 86
    # anti-narrowband
    ROOT_PERFORMANCE_STA_ANTINARROW_B1 = 87
    ROOT_PERFORMANCE_STA_ANTINARROW_B2 = 88
    # anti-pulse
    ROOT_PERFORMANCE_STA_ANTIPULSE_B1 = 89
    ROOT_PERFORMANCE_STA_ANTIPULSE_B2 = 90
    # psd
    ROOT_PERFORMANCE_STA_PSD_B1 = 91
    ROOT_PERFORMANCE_STA_PSD_B2 = 92
    # sta rate
    ROOT_PERFORMANCE_STA_RATE_B1 = 93
    ROOT_PERFORMANCE_STA_RATE_B2 = 94
    # white noise
    ROOT_PERFORMANCE_CCO_WN_B1 = 95
    ROOT_PERFORMANCE_CCO_WN_B2 = 96
    # anti-ppm
    ROOT_PERFORMANCE_CCO_ANTIPPM_B1 = 97
    ROOT_PERFORMANCE_CCO_ANTIPPM_B2 = 98
    # anti-attenuation
    ROOT_PERFORMANCE_CCO_ANTIATT_B1 = 99
    ROOT_PERFORMANCE_CCO_ANTIATT_B2 = 100
    # anti-narrowband
    ROOT_PERFORMANCE_CCO_ANTINARROW_B1 = 101
    ROOT_PERFORMANCE_CCO_ANTINARROW_B2 = 102
    # anti-pulse
    ROOT_PERFORMANCE_CCO_ANTIPULSE_B1 = 103
    ROOT_PERFORMANCE_CCO_ANTIPULSE_B2 = 104
    # psd
    ROOT_PERFORMANCE_CCO_PSD_B1 = 105
    ROOT_PERFORMANCE_CCO_PSD_B2 = 106
    # CCO rate
    ROOT_PERFORMANCE_CCO_RATE_B1 = 107
    ROOT_PERFORMANCE_CCO_RATE_B2 = 108
    ROOT_PERFORMANCE_MAX = ROOT_PERFORMANCE_CCO_RATE_B2 + 1

    # max
    TREE_MAX = ROOT_PERFORMANCE_MAX + 1


DictCommandInfo = {
    "协议一致性": AllCertCaseValue.ROOT_PROTOCON,
    # STA test case
    "STA测试项": AllCertCaseValue.ROOT_PROTOCON_STA_CHILD,
    "TMI遍历 STA band0": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B0,
    "TMI遍历 STA band1": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B1,
    "TMI遍历 STA band2": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B2,
    "TMI遍历 STA band3": AllCertCaseValue.ROOT_PROTOCON_STA_TMISCAN_B3,
    "ToneMask测试 STA band0": AllCertCaseValue.ROOT_PROTOCON_STA_TM_B0,
    "ToneMask测试 STA band1": AllCertCaseValue.ROOT_PROTOCON_STA_TM_B1,
    "ToneMask测试 STA band2": AllCertCaseValue.ROOT_PROTOCON_STA_TM_B2,
    "ToneMask测试 STA band3": AllCertCaseValue.ROOT_PROTOCON_STA_TM_B3,

    # CCO test case
    "CCO测试项": AllCertCaseValue.ROOT_PROTOCON_CCO_CHILD,
    "TMI遍历 CCO band0": AllCertCaseValue.ROOT_PROTOCON_CCO_TMISCAN_B0,
    "TMI遍历 CCO band1": AllCertCaseValue.ROOT_PROTOCON_CCO_TMISCAN_B1,
    "TMI遍历 CCO band2": AllCertCaseValue.ROOT_PROTOCON_CCO_TMISCAN_B2,
    "TMI遍历 CCO band3": AllCertCaseValue.ROOT_PROTOCON_CCO_TMISCAN_B3,
    "ToneMask测试 CCO band0": AllCertCaseValue.ROOT_PROTOCON_CCO_TM_B0,
    "ToneMask测试 CCO band1": AllCertCaseValue.ROOT_PROTOCON_CCO_TM_B1,
    "ToneMask测试 CCO band2": AllCertCaseValue.ROOT_PROTOCON_CCO_TM_B2,
    "ToneMask测试 CCO band3": AllCertCaseValue.ROOT_PROTOCON_CCO_TM_B3,

    # communication performance
    "通信性能测试": AllCertCaseValue.ROOT_PERFORMANCE_CHILD,
    "白噪性能 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_WN_B1,
    "白噪性能 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_WN_B2,
    "抗频偏性能 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIPPM_B1,
    "抗频偏性能 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIPPM_B2,
    "抗衰减性能 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIATT_B1,
    "抗衰减性能 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIATT_B2,
    "抗窄带性能 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTINARROW_B1,
    "抗窄带性能 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTINARROW_B2,
    "抗脉冲性能 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIPULSE_B1,
    "抗脉冲性能 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_ANTIPULSE_B2,
    "功率频谱密度 STA band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_PSD_B1,
    "功率频谱密度 STA band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_PSD_B2,
    "STA 速率测试 band1": AllCertCaseValue.ROOT_PERFORMANCE_STA_RATE_B1,
    "STA 速率测试 band2": AllCertCaseValue.ROOT_PERFORMANCE_STA_RATE_B2,
    "白噪性能 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_WN_B1,
    "白噪性能 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_WN_B2,
    "抗频偏性能 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIPPM_B1,
    "抗频偏性能 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIPPM_B2,
    "抗衰减性能 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIATT_B1,
    "抗衰减性能 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIATT_B2,
    "抗窄带性能 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTINARROW_B1,
    "抗窄带性能 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTINARROW_B2,
    "抗脉冲性能 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIPULSE_B1,
    "抗脉冲性能 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_ANTIPULSE_B2,
    "功率频谱密度 CCO band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_PSD_B1,
    "功率频谱密度 CCO band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_PSD_B2,
    "CCO 速率测试 band1": AllCertCaseValue.ROOT_PERFORMANCE_CCO_RATE_B1,
    "CCO 速率测试 band2": AllCertCaseValue.ROOT_PERFORMANCE_CCO_RATE_B2,
}

##########################################################
#                    power                               #
##########################################################


class PowerMarco:
    POWER_ON = 'aa'
    POWER_DOWN = 'bb'

##########################################################
#                    tmi/extmi/pb                        #
##########################################################


class TmiMarco:
    TMI_0 = 0
    TMI_1 = 1
    TMI_2 = 2
    TMI_3 = 3
    TMI_4 = 4
    TMI_5 = 5
    TMI_6 = 6
    TMI_7 = 7
    TMI_8 = 8
    TMI_9 = 9
    TMI_10 = 10
    TMI_11 = 11
    TMI_12 = 12
    TMI_13 = 13
    TMI_14 = 14
    TMI_MAX = 15


class ExtmiMarco:
    EXTMI_1 = 1
    EXTMI_2 = 2
    EXTMI_3 = 3
    EXTMI_4 = 4
    EXTMI_5 = 5
    EXTMI_6 = 6
    EXTMI_10 = 10
    EXTMI_11 = 11
    EXTMI_12 = 12
    EXTMI_13 = 13
    EXTMI_14 = 14
    EXTMI_MAX = 15


class PbSizeMarco:
    PB_NUM_72 = 72
    PB_NUM_136 = 136
    PB_NUM_264 = 264
    PB_NUM_520 = 520
    PB_SIZE_INV = 0


class RoboCopyMarco:
    ROBO_COPY_1 = 1
    ROBO_COPY_2 = 2
    ROBO_COPY_4 = 4
    ROBO_COPY_5 = 5
    ROBO_COPY_7 = 7
    ROBO_COPY_11 = 11


class InterMarco:
    INTER_1 = 1
    INTER_8 = 8
    INTER_10 = 10
    INTER_11 = 11
    INTER_14 = 14


""""
/* Modulation has a relation to BPC
 * Mapping for BPSK, QPSK, 8-QAM, 16-QAM,
 * 64-QAM, 256-QAM, 1024-QAM, The Mapper
 * takes 1, 2, 3, 4, 6, 8, or 10 bits
 */
"""


class ModulationMarco:
    MODULATION_BPSK = 1
    MODULATION_QPSK = 2
    MODULATION_8QAM = 3
    MODULATION_16QAM = 4


class PbNumMarco:
    MAX_PB_NUM_1 = 1
    MAX_PB_NUM_2 = 2
    MAX_PB_NUM_3 = 3
    MAX_PB_NUM_4 = 4


class CodingRateMarco:
    CODING_RATE_1_2 = 0
    CODING_RATE_16_18 = 1


class ValidToneMarco:
    VALID_TONE_BAND_0 = 411       # band0   80   -   490
    VALID_TONE_BAND_1 = 131       # band1   100  -   230
    VALID_TONE_BAND_2 = 89        # band2   32   -   120
    VALID_TONE_BAND_3 = 49        # band3   72   -   120
    VALID_TONE_BAND_4 = 260       # band4   231  -   490
    VALID_TONE_BAND_8 = 131       # band8   240  -   370
    VALID_TONE_BAND_9 = 801       # band9   200  -   1000
    VALID_TONE_BAND_10 = 256      # band10  1160 -   1415
    VALID_TONE_BAND_11 = 301      # band11  200  -   500


class FcSymNumMarco:
    FC_SYM_NUM_4 = 4
    FC_SYM_NUM_12 = 12


class RateMarco:
    RATE_0 = 0
    RATE_1 = 1


class StartValidToneMarco:
    START_VALID_TONE_BAND_0 = 80
    START_VALID_TONE_BAND_1 = 100
    START_VALID_TONE_BAND_2 = 32
    START_VALID_TONE_BAND_3 = 72
    START_VALID_TONE_BAND_4 = 231
    START_VALID_TONE_BAND_8 = 240
    START_VALID_TONE_BAND_9 = 200
    START_VALID_TONE_BAND_10 = 1160
    START_VALID_TONE_BAND_11 = 200


class EndValidToneMarco:
    END_VALID_TONE_BAND_0 = 490
    END_VALID_TONE_BAND_1 = 230
    END_VALID_TONE_BAND_2 = 120
    END_VALID_TONE_BAND_3 = 120
    END_VALID_TONE_BAND_4 = 490
    END_VALID_TONE_BAND_8 = 370
    END_VALID_TONE_BAND_9 = 1000
    END_VALID_TONE_BAND_10 = 1415
    END_VALID_TONE_BAND_11 = 500


class FdRmsMaxMarco:
    RMS_MAX_58 = 58
    RMS_MAX_63 = 63
    RMS_MAX_60 = 60


class RoboMarco:
    GI_MINI_ROBO = 567
    GI_HS_ROBO = 417
    GI_STD_ROBO = 417
    GI_SG_ROBO_LONG = 458
    GI_SG_ROBO_SHORT = 264

##########################################################
#                    debug leave                         #
##########################################################


class DebugLeave:
    LOG_DEBUG = 1
    LOG_INFO = 2
    LOG_WARNING = 3
    LOG_ERROR = 4
    LOG_CRITICAL = 5

##########################################################
#                    performance                         #
##########################################################


'''
narrow
频段0：（1MHz，-20dBm）、（8MHz，-30dBm）、（15MHz，-20dBm）
频段1：（1MHz，-20dBm）、（3MHz，-30dBm）、（6MHz，-30dBm）
频段1：（0.5MHz，-20dBm）、（2MHz，-30dBm）、（5MHz，-30dBm）
'''


class NarrowMarco:
    # band0
    NARROW_8M = 8
    NARROW_15M = 15
    # band1
    NARROW_1M = 1
    NARROW_3M = 3
    NARROW_6M = 6
    # band2
    NARROW_500K = 500
    NARROW_2M = 2
    NARROW_5M = 5


class SignolMarco:
    WHITE_TEST = 1
    PULSE_TEST = 2
    SIN_TEST = 3
    ATT_TEST = 4


class AttValueMarco:
    # the min value of attenuator
    ATT_VALUE_MIN = 0
    # the max value of attenuator
    ATT_VALUE_MAX = 95
    # the coarse step of attenuator
    ATT_COARSE_STEP = 10
    # the fine step of attenuator
    ATT_FINE_STEP = 1


class ResultMarco:
    PASS_THRESHOLD = 90


class OtherMarco:
    ATT_TEST_TIMES = 40
    PPM_TEST_TIMES = 40


class PpmMarco:
    PPM_MIN = 0
    PPM_MAX = 500
    PPM_LARGE_STEP = 50
    PPM_MIDDLE_STEP = 10
    PPM_SMALL_STEP = 1
    # 30PPM
    PPM_THRESHOLD = 30
    # positive and negative frequency offset
    PPM_POSITIVE = 1
    PPM_NEGATIVE = -1

