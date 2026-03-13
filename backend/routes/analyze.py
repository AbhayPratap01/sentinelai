from fastapi import APIRouter
from models.threat import AnalyzeRequest, AnalyzeResponse, ThreatLog, ThreatType
from models.store import store
from core.classifier import classify_prompt
from core.connection_manager import manager
from datetime import datetime, timezone
import uuid

router = APIRouter()

def determine_action(is_blocked: bool, threat_type: ThreatType) -> str:
    if not is_blocked:
        return "allow"
    if threat_type == ThreatType.JAILBREAK:
        return "block"
    if threat_type == ThreatType.PROMPT_INJECTION:
        return "block"
    if threat_type == ThreatType.DATA_EXFILTRATION:
        return "block"
    return "flag"

def sanitize(prompt: str) -> str:
    return "[REDACTED - Malicious prompt blocked by SentinelAI]"

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_prompt(req: AnalyzeRequest):
    threat = classify_prompt(req.prompt)
    action = determine_action(threat.is_blocked, threat.threat_type)
    event_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    log = ThreatLog(
        id=event_id,
        timestamp=timestamp,
        prompt=req.prompt[:300],
        source=req.source,
        user_id=req.user_id,
        threat_type=threat.threat_type,
        risk_level=threat.risk_level,
        risk_score=threat.risk_score,
        is_blocked=threat.is_blocked,
        explanation=threat.explanation,
        latency_ms=threat.latency_ms,
    )
    store.add(log)

    await manager.broadcast({
        "event": "new_threat",
        "data": log.model_dump(),
    })

    return AnalyzeResponse(
        id=event_id,
        threat=threat,
        action=action,
        sanitized_prompt=sanitize(req.prompt) if threat.is_blocked else None,
        timestamp=timestamp,
    )
