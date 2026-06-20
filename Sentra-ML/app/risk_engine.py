from typing import Iterable, Tuple


RISK_WEIGHTS = {
    "NO_HELMET": 40,
    "NO_VEST": 30,
    "DANGER_ZONE_ENTRY": 50,
}


def calculate_risk(violations: Iterable[str]) -> Tuple[int, str]:
    score = sum(RISK_WEIGHTS.get(violation, 0) for violation in violations)
    return score, get_risk_level(score)


def get_risk_level(score: int) -> str:
    if score == 0:
        return "SAFE"
    if score <= 40:
        return "WARNING"
    if score <= 80:
        return "HIGH"
    return "CRITICAL"


def highest_risk_level(levels: Iterable[str]) -> str:
    order = {"SAFE": 0, "WARNING": 1, "HIGH": 2, "CRITICAL": 3}
    return max(levels, key=lambda level: order.get(level, 0), default="SAFE")
