from __future__ import annotations

from enum import Enum

class Mode(Enum):
    VN_STD = 0
    VN_TAIKO = 1
    VN_CATCH = 2
    VN_MANIA = 3
    RX_STD = 4
    RX_TAIKO = 5
    RX_CATCH = 6
    AP_STD = 8

    @classmethod
    def from_string(cls, mode_str: str) -> int:
        mode_mapping = {
            "vn!std": cls.VN_STD,
            "vn!taiko": cls.VN_TAIKO,
            "vn!catch": cls.VN_CATCH,
            "vn!mania": cls.VN_MANIA,
            "rx!std": cls.RX_STD,
            "rx!taiko": cls.RX_TAIKO,
            "rx!catch": cls.RX_CATCH,
            "ap!std": cls.AP_STD
        }

        return mode_mapping.get(mode_str.lower(), cls.VN_STD).value

    @classmethod
    def to_string(cls, mode_id: int) -> str:
        int2mode = {mode.value: mode.name.lower().replace('_', '!') for mode in cls}
        
        return int2mode.get(mode_id, "vn!std")
    
class Mods(Enum):
    NOMOD = 0
    NOFAIL = 1 << 0
    EASY = 1 << 1
    TOUCHSCREEN = 1 << 2
    HIDDEN = 1 << 3
    HARDROCK = 1 << 4
    SUDDENDEATH = 1 << 5
    DOUBLETIME = 1 << 6
    RELAX = 1 << 7
    HALFTIME = 1 << 8
    NIGHTCORE = 1 << 9
    FLASHLIGHT = 1 << 10
    AUTOPLAY = 1 << 11
    SPUNOUT = 1 << 12
    AUTOPILOT = 1 << 13
    PERFECT = 1 << 14
    KEY4 = 1 << 15
    KEY5 = 1 << 16
    KEY6 = 1 << 17
    KEY7 = 1 << 18
    KEY8 = 1 << 19
    FADEIN = 1 << 20
    RANDOM = 1 << 21
    CINEMA = 1 << 22
    TARGET = 1 << 23
    KEY9 = 1 << 24
    KEYCOOP = 1 << 25
    KEY1 = 1 << 26
    KEY3 = 1 << 27
    KEY2 = 1 << 28
    SCOREV2 = 1 << 29
    MIRROR = 1 << 30
    
    @classmethod
    def from_modstr(cls, s: str) -> Mods:
        mods = cls.NOMOD
        mod_strs = [s[idx:idx + 2].upper() for idx in range(0, len(s), 2)]
        
        for mod in mod_strs:
            mods |= modstr2mod_dict.get(mod, cls.NOMOD)

        return mods
    
modstr2mod_dict = {
    "NF": Mods.NOFAIL,
    "EZ": Mods.EASY,
    "TD": Mods.TOUCHSCREEN,
    "HD": Mods.HIDDEN,
    "HR": Mods.HARDROCK,
    "SD": Mods.SUDDENDEATH,
    "DT": Mods.DOUBLETIME,
    "RX": Mods.RELAX,
    "HT": Mods.HALFTIME,
    "NC": Mods.NIGHTCORE,
    "FL": Mods.FLASHLIGHT,
    "AU": Mods.AUTOPLAY,
    "SO": Mods.SPUNOUT,
    "AP": Mods.AUTOPILOT,
    "PF": Mods.PERFECT,
    "FI": Mods.FADEIN,
    "RN": Mods.RANDOM,
    "CN": Mods.CINEMA,
    "TP": Mods.TARGET,
    "V2": Mods.SCOREV2,
    "MR": Mods.MIRROR,
    "1K": Mods.KEY1,
    "2K": Mods.KEY2,
    "3K": Mods.KEY3,
    "4K": Mods.KEY4,
    "5K": Mods.KEY5,
    "6K": Mods.KEY6,
    "7K": Mods.KEY7,
    "8K": Mods.KEY8,
    "9K": Mods.KEY9,
    "CO": Mods.KEYCOOP,
}