import re
import time
from typing import Tuple
from models.threat import ThreatResult, ThreatType, RiskLevel

INJECTION_PATTERNS = [
    r"ignore (all |previous |prior |above |your )?(instructions|rules|guidelines|constraints|prompt)",
    r"disregard (all |previous |prior |above |your )?(instructions|rules|guidelines|constraints|prompt)",
    r"forget (all |previous |prior |above |your )?(instructions|rules|guidelines|constraints|prompt)",
    r"you are now (a |an )?(?!assistant|helpful)",
    r"pretend (you are|to be|you're)",
    r"act as (a |an )?(?!assistant|helpful)",
    r"roleplay as",
    r"your new (instructions|rules|prompt|system prompt) (are|is)",
    r"override (your )?(safety|security|restrictions|guidelines)",
    r"system prompt",
    r"\[system\]",
    r"###\s*(instruction|system|human|assistant)",
    r"<\|.*?\|>",
]

JAILBREAK_PATTERNS = [
    r"DAN\b",
    r"do anything now",
    r"jailbreak",
    r"developer mode",
    r"unrestricted mode",
    r"no (restrictions|limits|filters|rules|guidelines)",
    r"bypass (your )?(filter|safety|restriction|rule)",
    r"(evil|opposite|dark|unfiltered|uncensored) (mode|version|ai|assistant)",
    r"as an (ai|language model) without (restrictions|guidelines|filters)",
    r"(sudo|admin|root) mode",
    r"grandma (trick|exploit|hack)",
]

DATA_EXFIL_PATTERNS = [
    r"(show|reveal|print|output|display|tell me|what is|what are|give me) (your |the )?(system prompt|instructions|training data|initial prompt|context|full prompt)",
    r"what (were you|are you) (told|instructed|trained|prompted)",
    r"repeat (everything|all|your|the) (above|before|prior|previous|instructions|system|context)",
    r"summarize (your |the )?(instructions|system prompt|context)",
    r"extract (your |the )?(instructions|training|data|memory)",
]

SOCIAL_ENGINEERING_PATTERNS = [
    r"(i am|i'm) (your (creator|developer|admin|owner|god|master)|anthropic|openai|google)",
    r"(emergency|urgent|critical|important).*override",
    r"this is (a |an )?(test|drill|simulation)",
    r"(for|in) (research|testing|educational) purposes",
    r"trust me",
    r"confidential(ly)?.*tell",
]

def compute_risk_score(text: str, matched_patterns: list, threat_type: ThreatType) -> float:
    base_scores = {
        ThreatType.PROMPT_INJECTION: 0.75,
        ThreatType.JAILBREAK: 0.85,
        ThreatType.DATA_EXFILTRATION: 0.70,
        ThreatType.SOCIAL_ENGINEERING: 0.60,
        ThreatType.SAFE: 0.05,
    }
    score = base_scores.get(threat_type, 0.05)
    score += min(0.1 * len(matched_patterns), 0.15)
    if len(text) > 500:
        score += 0.05
    return round(min(score, 0.99), 2)

def classify_prompt(text: str) -> ThreatResult:
    start = time.time()
    text_lower = text.lower()
    matched = []

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(("injection", pattern))

    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(("jailbreak", pattern))

    for pattern in DATA_EXFIL_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(("data_exfil", pattern))

    for pattern in SOCIAL_ENGINEERING_PATTERNS:
        if re.search(pattern, text_lower):
            matched.append(("social_eng", pattern))

    categories = [m[0] for m in matched]

    if "jailbreak" in categories:
        threat_type = ThreatType.JAILBREAK
    elif "injection" in categories:
        threat_type = ThreatType.PROMPT_INJECTION
    elif "data_exfil" in categories:
        threat_type = ThreatType.DATA_EXFILTRATION
    elif "social_eng" in categories:
        threat_type = ThreatType.SOCIAL_ENGINEERING
    else:
        threat_type = ThreatType.SAFE

    risk_score = compute_risk_score(text, matched, threat_type)

    if risk_score >= 0.80:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 0.60:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 0.35:
        risk_level = RiskLevel.MEDIUM
    elif risk_score >= 0.10:
        risk_level = RiskLevel.LOW
    else:
        risk_level = RiskLevel.SAFE

    latency_ms = round((time.time() - start) * 1000, 2)

    return ThreatResult(
        threat_type=threat_type,
        risk_level=risk_level,
        risk_score=risk_score,
        matched_patterns=[m[1] for m in matched[:5]],
        is_blocked=risk_score >= 0.60,
        latency_ms=latency_ms,
        explanation=generate_explanation(threat_type, matched),
    )

def generate_explanation(threat_type: ThreatType, matched: list) -> str:
    if threat_type == ThreatType.SAFE:
        return "No malicious patterns detected. Prompt appears safe."
    explanations = {
        ThreatType.PROMPT_INJECTION: "Prompt contains instruction-override patterns attempting to hijack LLM behavior.",
        ThreatType.JAILBREAK: "Prompt attempts to remove model safety constraints or enable restricted behaviors.",
        ThreatType.DATA_EXFILTRATION: "Prompt attempts to extract system prompt, training data, or internal instructions.",
        ThreatType.SOCIAL_ENGINEERING: "Prompt uses deceptive identity or authority claims to manipulate model responses.",
    }
    return explanations.get(threat_type, "Suspicious prompt detected.")
