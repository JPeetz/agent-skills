#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
"""Campaign claims verifier. Flags unsubstantiated claims, regulated terms, policy risks."""
import re, json, sys

# Regulated terms that need special handling
REGULATED_TERMS = [
    "guaranteed", "guarantee", "cure", "heal", "treat", "diagnose", "prevent",
    "best", "fastest", "easiest", "#1", "number one", "world's best",
    "100%", "zero risk", "risk-free", "risk free", "no risk",
    "permanent", "instant", "immediate", "guaranteed results",
    "FDA approved", "doctor recommended", "clinically proven",
]

# Phrases that indicate a claim needs evidence
CLAIM_PATTERNS = [
    r"(\d+)% (of|more|less|faster|better|increase|decrease)",
    r"save \$[\d,]+",
    r"earn \$[\d,]+",
    r"make \$[\d,]+",
    r"(\d+)x (faster|better|more)",
    r"(\d+),?000\+ (users|customers|downloads)",
    r"(over|more than) (\d+),?000",
    r"(\d+\.?\d*) star",
]

def check_claims(text: str) -> dict:
    """Check a piece of ad copy for potential issues."""
    issues = []
    suggestions = []

    for term in REGULATED_TERMS:
        if term.lower() in text.lower():
            issues.append({
                "type": "regulated_term",
                "term": term,
                "severity": "high",
                "recommendation": f"Replace or substantiate '{term}' with verifiable source. If unverified, rewrite: e.g., 'trusted by thousands' instead of '#1'."
            })

    for pattern in CLAIM_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            issues.append({
                "type": "unverified_claim",
                "match": match.group(0),
                "severity": "medium",
                "recommendation": f"Cite specific source for '{match.group(0)}'. If no source exists, remove or rephrase as projection: 'aims to' or 'targeting'."
            })

    if "before" in text.lower() and "after" in text.lower():
        issues.append({
            "type": "before_after",
            "severity": "medium",
            "recommendation": "Before/after claims require typical results disclosure. Add: 'Individual results vary.' Or replace with testimonial format."
        })

    if re.search(r"limited time|act now|don't wait|only \d+ left|ending soon", text, re.IGNORECASE):
        if not re.search(r"(while supplies last|limited availability|offer valid|expires)", text, re.IGNORECASE):
            issues.append({
                "type": "false_urgency",
                "severity": "low",
                "recommendation": "Urgency language detected without substantiation. Add real constraint (e.g., 'offer valid until [date]') or remove."
            })

    if not issues:
        return {"status": "clean", "issues": []}

    high = [i for i in issues if i["severity"] == "high"]
    med = [i for i in issues if i["severity"] == "medium"]
    low = [i for i in issues if i["severity"] == "low"]

    return {
        "status": "flagged",
        "summary": f"{len(issues)} issues: {len(high)} high, {len(med)} medium, {len(low)} low",
        "issues": issues,
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = sys.argv[1]
    else:
        text = sys.stdin.read()

    result = check_claims(text)
    print(json.dumps(result, indent=2))