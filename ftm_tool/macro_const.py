# -*- coding: utf-8 -*-

class all_cert_case_value:
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

    #通信性能测试
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
    ROOT_PERFORMANCE_STA_RATE = 93
    # white noise
    ROOT_PERFORMANCE_CCO_WN_B1 = 94
    ROOT_PERFORMANCE_CCO_WN_B2 = 95
    # anti-ppm
    ROOT_PERFORMANCE_CCO_ANTIPPM_B1 = 96
    ROOT_PERFORMANCE_CCO_ANTIPPM_B2 = 97
    # anti-attenuation
    ROOT_PERFORMANCE_CCO_ANTIATT_B1 = 98
    ROOT_PERFORMANCE_CCO_ANTIATT_B2 = 99
    # anti-narrowband
    ROOT_PERFORMANCE_CCO_ANTINARROW_B1 = 100
    ROOT_PERFORMANCE_CCO_ANTINARROW_B2 = 101
    # anti-pulse
    ROOT_PERFORMANCE_CCO_ANTIPULSE_B1 = 102
    ROOT_PERFORMANCE_CCO_ANTIPULSE_B2 = 103
    # psd
    ROOT_PERFORMANCE_CCO_PSD_B1 = 104
    ROOT_PERFORMANCE_CCO_PSD_B2 = 105
    # CCO rate
    ROOT_PERFORMANCE_CCO_RATE = 106
    ROOT_PERFORMANCE_MAX = ROOT_PERFORMANCE_CCO_RATE + 1


    #max
    TREE_MAX = ROOT_PERFORMANCE_MAX + 1

DictCommandInfo = {
    "协议一致性": all_cert_case_value.ROOT_PROTOCON,
    # STA test case
    "STA测试项": all_cert_case_value.ROOT_PROTOCON_STA_CHILD, "TMI遍历 STA band0": all_cert_case_value.ROOT_PROTOCON_STA_TMISCAN_B0,
    "TMI遍历 STA band1": all_cert_case_value.ROOT_PROTOCON_STA_TMISCAN_B1, "TMI遍历 STA band2": all_cert_case_value.ROOT_PROTOCON_STA_TMISCAN_B2,
    "TMI遍历 STA band3": all_cert_case_value.ROOT_PROTOCON_STA_TMISCAN_B3, "ToneMask测试 STA band0": all_cert_case_value.ROOT_PROTOCON_STA_TM_B0,
    "ToneMask测试 STA band1": all_cert_case_value.ROOT_PROTOCON_STA_TM_B1, "ToneMask测试 STA band2": all_cert_case_value.ROOT_PROTOCON_STA_TM_B2,
    "ToneMask测试 STA band3": all_cert_case_value.ROOT_PROTOCON_STA_TM_B3,

    # CCO test case
    "CCO测试项": all_cert_case_value.ROOT_PROTOCON_CCO_CHILD, "TMI遍历 CCO band0": all_cert_case_value.ROOT_PROTOCON_CCO_TMISCAN_B0,
    "TMI遍历 CCO band1": all_cert_case_value.ROOT_PROTOCON_CCO_TMISCAN_B1, "TMI遍历 CCO band2": all_cert_case_value.ROOT_PROTOCON_CCO_TMISCAN_B2,
    "TMI遍历 CCO band3": all_cert_case_value.ROOT_PROTOCON_CCO_TMISCAN_B3, "ToneMask测试 CCO band0": all_cert_case_value.ROOT_PROTOCON_CCO_TM_B0,
    "ToneMask测试 CCO band1": all_cert_case_value.ROOT_PROTOCON_CCO_TM_B1, "ToneMask测试 CCO band2": all_cert_case_value.ROOT_PROTOCON_CCO_TM_B2,
    "ToneMask测试 CCO band3": all_cert_case_value.ROOT_PROTOCON_CCO_TM_B3,

    # communication performance
    "通信性能测试": all_cert_case_value.ROOT_PERFORMANCE_CHILD,
    "白噪性能 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_WN_B1, "白噪性能 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_WN_B2,
    "抗频偏性能 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIPPM_B1, "抗频偏性能 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIPPM_B2,
    "抗衰减性能 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIATT_B1, "抗衰减性能 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIATT_B2,
    "抗窄带性能 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTINARROW_B1, "抗窄带性能 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTINARROW_B2,
    "抗脉冲性能 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIPULSE_B1, "抗脉冲性能 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_ANTIPULSE_B2,
    "功率频谱密度 STA band1": all_cert_case_value.ROOT_PERFORMANCE_STA_PSD_B1, "功率频谱密度 STA band2": all_cert_case_value.ROOT_PERFORMANCE_STA_PSD_B2,
    "STA 速率测试": all_cert_case_value.ROOT_PERFORMANCE_STA_RATE,
    "白噪性能 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_WN_B1, "白噪性能 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_WN_B2,
    "抗频偏性能 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIPPM_B1, "抗频偏性能 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIPPM_B2,
    "抗衰减性能 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIATT_B1, "抗衰减性能 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIATT_B2,
    "抗窄带性能 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTINARROW_B1, "抗窄带性能 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTINARROW_B2,
    "抗脉冲性能 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIPULSE_B1, "抗脉冲性能 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_ANTIPULSE_B2,
    "功率频谱密度 CCO band1": all_cert_case_value.ROOT_PERFORMANCE_CCO_PSD_B1, "功率频谱密度 CCO band2": all_cert_case_value.ROOT_PERFORMANCE_CCO_PSD_B2,
    "CCO 速率测试": all_cert_case_value.ROOT_PERFORMANCE_CCO_RATE,
}
