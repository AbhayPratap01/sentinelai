from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from datetime import datetime
import uuid

class ThreatType(str, Enum):
    SAFE = "safe"
    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK = "jailbreak"
    DATA_EXFILTRATION = "data_exfiltration"
    SOCIAL_ENGINEERING = "social_engineering"

class RiskLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatResult(BaseModel):
    threat_type: ThreatType
    risk_level: RiskLevel
    risk_score: float
    matched_patterns: List[str]
    is_blocked: bool
    latency_ms: float
    explanation: str

class AnalyzeRequest(BaseModel):
    prompt: str
    source: Optional[str] = "api"
    user_id: Optional[str] = "anonymous"

class ThreatLog(BaseModel):
    id: str
    timestamp: str
    prompt: str
    source: str
    user_id: str
    threat_type: ThreatType
    risk_level: RiskLevel
    risk_score: float
    is_blocked: bool
    explanation: str
    latency_ms: float

class AnalyzeResponse(BaseModel):
    id: str
    threat: ThreatResult
    action: str
    sanitized_prompt: Optional[str] = None
    timestamp: str
