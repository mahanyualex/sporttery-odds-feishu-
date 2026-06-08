from typing import TypedDict


class OddsLine(TypedDict):
    updated_at: str


class MnlOdds(OddsLine):
    home: float
    away: float


class HdcOdds(OddsLine):
    goal_line: float
    home: float
    away: float


class HiloOdds(OddsLine):
    goal_line: float
    high: float
    low: float


class HadOdds(OddsLine):
    win: float
    draw: float
    lose: float


class HhadOdds(HadOdds):
    goal_line: float


class FootballMatch(TypedDict):
    business_date: str
    match_id: int
    match_num: str
    league: str
    home_team: str
    away_team: str
    match_date: str
    match_time: str
    match_status: str
    had: HadOdds
    hhad: HhadOdds
