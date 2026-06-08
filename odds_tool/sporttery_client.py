import json
import urllib.request
from typing import Any


class NoMatchSaleError(RuntimeError):
    pass


class SportteryClient:
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.sporttery.cn/",
    }
    FOOTBALL_MATCH_LIST_URL = (
        "https://webapi.sporttery.cn/gateway/uniform/football/"
        "getMatchCalculatorV1.qry?channel=web&poolCode=hhad,had"
    )
    FOOTBALL_MATCH_LIST_FALLBACK_URL = (
        "https://webapi.sporttery.cn/gateway/uniform/football/"
        "getMatchResultV1.qry?channel=web&poolCode=hhad,had"
    )
    NO_MATCHES_ON_SALE_MESSAGE = "今天暂无竞彩足球可售比赛"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def _fetch_json(self, url: str) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            headers=self.DEFAULT_HEADERS,
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if str(payload.get("errorCode")) != "0":
            raise RuntimeError(f"体彩接口返回失败：{payload.get('errorCode')} {payload.get('errorMessage', '')}")
        return payload

    def _has_match_info_list(self, payload: dict[str, Any]) -> bool:
        value = payload.get("value")
        return isinstance(value, dict) and isinstance(value.get("matchInfoList"), list)

    def fetch_fixed_bonus(self, match_id: int) -> dict[str, Any]:
        url = (
            "https://webapi.sporttery.cn/gateway/uniform/basketball/"
            f"getFixedBonusV3.qry?clientCode=3001&matchId={match_id}"
        )
        return self._fetch_json(url)

    def fetch_football_match_list(self) -> dict[str, Any]:
        payload = self._fetch_json(self.FOOTBALL_MATCH_LIST_URL)
        if self._has_match_info_list(payload):
            return payload

        fallback_payload = self._fetch_json(self.FOOTBALL_MATCH_LIST_FALLBACK_URL)
        if self._has_match_info_list(fallback_payload):
            return fallback_payload

        raise NoMatchSaleError(self.NO_MATCHES_ON_SALE_MESSAGE)
