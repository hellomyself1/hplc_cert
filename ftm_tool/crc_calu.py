#coding=utf-8

iot_crc24_table = [
    0x00000000, 0x00848401, 0x00850801, 0x00018c00, 0x00861001, 0x00029400,
    0x00031800, 0x00879c01, 0x00802001, 0x0004a400, 0x00052800, 0x0081ac01,
    0x00063000, 0x0082b401, 0x00833801, 0x0007bc00, 0x008c4001, 0x0008c400,
    0x00094800, 0x008dcc01, 0x000a5000, 0x008ed401, 0x008f5801, 0x000bdc00,
    0x000c6000, 0x0088e401, 0x00896801, 0x000dec00, 0x008a7001, 0x000ef400,
    0x000f7800, 0x008bfc01, 0x00948001, 0x00100400, 0x00118800, 0x00950c01,
    0x00129000, 0x00961401, 0x00979801, 0x00131c00, 0x0014a000, 0x00902401,
    0x0091a801, 0x00152c00, 0x0092b001, 0x00163400, 0x0017b800, 0x00933c01,
    0x0018c000, 0x009c4401, 0x009dc801, 0x00194c00, 0x009ed001, 0x001a5400,
    0x001bd800, 0x009f5c01, 0x0098e001, 0x001c6400, 0x001de800, 0x00996c01,
    0x001ef000, 0x009a7401, 0x009bf801, 0x001f7c00, 0x00a50001, 0x00218400,
    0x00200800, 0x00a48c01, 0x00231000, 0x00a79401, 0x00a61801, 0x00229c00,
    0x00252000, 0x00a1a401, 0x00a02801, 0x0024ac00, 0x00a33001, 0x0027b400,
    0x00263800, 0x00a2bc01, 0x00294000, 0x00adc401, 0x00ac4801, 0x0028cc00,
    0x00af5001, 0x002bd400, 0x002a5800, 0x00aedc01, 0x00a96001, 0x002de400,
    0x002c6800, 0x00a8ec01, 0x002f7000, 0x00abf401, 0x00aa7801, 0x002efc00,
    0x00318000, 0x00b50401, 0x00b48801, 0x00300c00, 0x00b79001, 0x00331400,
    0x00329800, 0x00b61c01, 0x00b1a001, 0x00352400, 0x0034a800, 0x00b02c01,
    0x0037b000, 0x00b33401, 0x00b2b801, 0x00363c00, 0x00bdc001, 0x00394400,
    0x0038c800, 0x00bc4c01, 0x003bd000, 0x00bf5401, 0x00bed801, 0x003a5c00,
    0x003de000, 0x00b96401, 0x00b8e801, 0x003c6c00, 0x00bbf001, 0x003f7400,
    0x003ef800, 0x00ba7c01, 0x00c60001, 0x00428400, 0x00430800, 0x00c78c01,
    0x00401000, 0x00c49401, 0x00c51801, 0x00419c00, 0x00462000, 0x00c2a401,
    0x00c32801, 0x0047ac00, 0x00c03001, 0x0044b400, 0x00453800, 0x00c1bc01,
    0x004a4000, 0x00cec401, 0x00cf4801, 0x004bcc00, 0x00cc5001, 0x0048d400,
    0x00495800, 0x00cddc01, 0x00ca6001, 0x004ee400, 0x004f6800, 0x00cbec01,
    0x004c7000, 0x00c8f401, 0x00c97801, 0x004dfc00, 0x00528000, 0x00d60401,
    0x00d78801, 0x00530c00, 0x00d49001, 0x00501400, 0x00519800, 0x00d51c01,
    0x00d2a001, 0x00562400, 0x0057a800, 0x00d32c01, 0x0054b000, 0x00d03401,
    0x00d1b801, 0x00553c00, 0x00dec001, 0x005a4400, 0x005bc800, 0x00df4c01,
    0x0058d000, 0x00dc5401, 0x00ddd801, 0x00595c00, 0x005ee000, 0x00da6401,
    0x00dbe801, 0x005f6c00, 0x00d8f001, 0x005c7400, 0x005df800, 0x00d97c01,
    0x00630000, 0x00e78401, 0x00e60801, 0x00628c00, 0x00e51001, 0x00619400,
    0x00601800, 0x00e49c01, 0x00e32001, 0x0067a400, 0x00662800, 0x00e2ac01,
    0x00653000, 0x00e1b401, 0x00e03801, 0x0064bc00, 0x00ef4001, 0x006bc400,
    0x006a4800, 0x00eecc01, 0x00695000, 0x00edd401, 0x00ec5801, 0x0068dc00,
    0x006f6000, 0x00ebe401, 0x00ea6801, 0x006eec00, 0x00e97001, 0x006df400,
    0x006c7800, 0x00e8fc01, 0x00f78001, 0x00730400, 0x00728800, 0x00f60c01,
    0x00719000, 0x00f51401, 0x00f49801, 0x00701c00, 0x0077a000, 0x00f32401,
    0x00f2a801, 0x00762c00, 0x00f1b001, 0x00753400, 0x0074b800, 0x00f03c01,
    0x007bc000, 0x00ff4401, 0x00fec801, 0x007a4c00, 0x00fdd001, 0x00795400,
    0x0078d800, 0x00fc5c01, 0x00fbe001, 0x007f6400, 0x007ee800, 0x00fa6c01,
    0x007df000, 0x00f97401, 0x00f8f801, 0x007c7c00
]

class crc_calu:
    def crc24(self, octets):
        crc = 0 & 0x00FFFFFF
        for octet in octets:
            crc = crc ^ octet
            crc = (crc >> 8) ^ iot_crc24_table[crc & 0x0FF]
        return crc & 0x00FFFFFF
