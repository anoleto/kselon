# TODO: use osu-tools or rosu instead of akatsuki-pp-py
#       maybe add calculate_pp request too and finally use config.TOKEN?

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypedDict

# placeholder
from refx_pp_py import Beatmap
from refx_pp_py import Calculator

from utils.OsuMapping import Mods


@dataclass
class ScoreParams:
    mode: int

    mods: int | None = None
    combo: int | None = None
    acc: float | None = None

    n300: int | None = None
    n100: int | None = None
    n50: int | None = None
    ngeki: int | None = None
    nkatu: int | None = None
    nmiss: int | None = None

    # NOTE: only for refx
    AC: int | None = None
    AR: float | None = None
    TW: int | None = None
    CS: bool | None = None
    HD: bool | None = None

class Performance(TypedDict):
    pp: float
    pp_acc: float | None
    pp_aim: float | None
    pp_speed: float | None
    pp_flashlight: float | None
    effective_miss_count: float | None
    pp_difficulty: float | None

class Difficulty(TypedDict):
    stars: float
    aim: float | None
    speed: float | None
    flashlight: float | None
    slider_factor: float | None
    speed_note_count: float | None
    stamina: float | None
    color: float | None
    rhythm: float | None
    peak: float | None

class PerformanceResult(TypedDict):
    performance: Performance
    difficulty: Difficulty

def calculate_performances(osu_file_path: str, scores: Iterable[ScoreParams]) -> list[PerformanceResult]:
    calc_ = Beatmap(path=osu_file_path)

    results: list[PerformanceResult] = []

    for score in scores:
        if score.acc and (
            score.n300 or score.n100 or score.n50 or score.ngeki or score.nkatu
        ):
            raise ValueError(
                "Must not specify accuracy AND 300/100/50/geki/katu. Only one or the other.",
            )

        if score.mods is not None:
            if score.mods & Mods.NIGHTCORE.value:
                score.mods |= Mods.DOUBLETIME.value

        calculator = Calculator(
            mode=score.mode % 4,
            mods=score.mods or 0,
            combo=score.combo,
            acc=score.acc,
            n300=score.n300,
            n100=score.n100,
            n50=score.n50,
            n_geki=score.ngeki,
            n_katu=score.nkatu,
            n_misses=score.nmiss,
            # NOTE: for refx
            shaymi_mode=True if score.mode > 3 else False
        )

        # NOTE: for refx
        if score.mode > 3:
            calculator.cheat_ac(0 if score.AC is None or score.AC < 1 else score.AC)
            calculator.cheat_arc(score.AR if score.AR is not None else 0)
            calculator.cheat_tw(int(150 if score.TW < 1 else score.TW))
            calculator.cheat_cs(bool(score.CS))
            calculator.cheat_hdr(bool(score.HD))
        else:
            calculator.cheat_ac(0 if score.AC is None or score.AC < 1 else score.AC)
            calculator.cheat_arc(score.AR if score.AR is not None else 0)
            calculator.cheat_hdr(bool(score.HD))

        result = calculator.performance(calc_)

        pp = result.pp

        if math.isnan(pp) or math.isinf(pp):
            pp = 0.0
        else:
            pp = round(pp, 3)

        results.append(
            {
                "performance": {
                    "pp": pp,
                    "pp_acc": result.pp_acc,
                    "pp_aim": result.pp_aim,
                    "pp_speed": result.pp_speed,
                    "pp_flashlight": result.pp_flashlight,
                    "effective_miss_count": result.effective_miss_count,
                    "pp_difficulty": result.pp_difficulty,
                },
                "difficulty": {
                    "stars": result.difficulty.stars,
                    "aim": result.difficulty.aim,
                    "speed": result.difficulty.speed,
                    "flashlight": result.difficulty.flashlight,
                    "slider_factor": result.difficulty.slider_factor,
                    "speed_note_count": result.difficulty.speed_note_count,
                    "stamina": result.difficulty.stamina,
                    "color": result.difficulty.color,
                    "rhythm": result.difficulty.rhythm,
                    "peak": result.difficulty.peak,
                },
            },
        )

    return results
