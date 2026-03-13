from typing import List
from models.threat import ThreatLog
from collections import deque

class ThreatStore:
    def __init__(self, maxlen: int = 500):
        self._logs: deque = deque(maxlen=maxlen)

    def add(self, log: ThreatLog):
        self._logs.appendleft(log)

    def get_all(self, limit: int = 100) -> List[ThreatLog]:
        return list(self._logs)[:limit]

    def get_stats(self) -> dict:
        logs = list(self._logs)
        total = len(logs)
        blocked = sum(1 for l in logs if l.is_blocked)
        by_type = {}
        by_risk = {}
        for log in logs:
            by_type[log.threat_type] = by_type.get(log.threat_type, 0) + 1
            by_risk[log.risk_level] = by_risk.get(log.risk_level, 0) + 1
        avg_score = round(sum(l.risk_score for l in logs) / total, 3) if total else 0
        return {
            "total": total,
            "blocked": blocked,
            "safe": total - blocked,
            "block_rate": round(blocked / total * 100, 1) if total else 0,
            "avg_risk_score": avg_score,
            "by_type": by_type,
            "by_risk": by_risk,
        }

store = ThreatStore()
