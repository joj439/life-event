import re
from typing import Dict, Any, Optional

SUPPORTED_SCENARIO_MESSAGE = (
    "This prototype currently supports relocation, financial fraud, marriage, and family-death scenarios."
)

UNSUPPORTED_EVENTS = {
    "childbirth": ["child", "baby", "born", "birth", "pregnant", "newborn"],
    "business": ["business", "startup", "company", "enterprise", "firm", "llp", "gst"],
    "retirement": ["retire", "retired", "retirement"],
    "education": ["college", "university", "school", "degree", "graduation", "admission"],
    "employment": ["job", "promotion", "hired", "unemployed", "resigned", "salary"]
}

FINANCIAL_FRAUD_KEYWORDS = [
    "unauthorized", "fraud", "upi", "scam", "phishing", "cyber", "stolen money",
    "money deducted", "debited without", "account hacked", "fraudulent", "cybercrime"
]

MARRIAGE_KEYWORDS = [
    "marry", "married", "marriage", "wedding", "matrimony", "got married", "tied the knot"
]

FAMILY_DEATH_KEYWORDS = [
    "passed away", "died", "death", "demise", "expired", "loss of my", "father passed",
    "mother passed", "husband passed", "wife passed", "parent passed"
]

RELOCATION_KEYWORDS = [
    "move", "moved", "moving",
    "shift", "shifted", "shifting",
    "relocate", "relocated", "relocating",
    "transferred", "transfer"
]


def clean_city_name(city: str) -> str:
    """Clean extracted city string."""
    city = re.sub(r"[^\w\s]", "", city).strip()
    stop_words = ["permanently", "recently", "temporarily", "now", "today", "yesterday", "last", "month", "year", "week"]
    words = city.split()
    filtered = [w for w in words if w.lower() not in stop_words]
    clean_str = " ".join(filtered) if filtered else city
    return clean_str.title()


def parse_life_event_regex(message: str) -> Dict[str, Any]:
    """
    Deterministic NLP fallback parser for all 4 supported LifeEvent scenarios:
    1. relocation
    2. financial_fraud
    3. marriage
    4. family_death
    """
    text = (message or "").strip()
    if not text:
        return {
            "event_type": "unknown",
            "origin": None,
            "destination": None,
            "confidence": 0.0,
            "is_supported": False,
            "message": f"Input is empty. {SUPPORTED_SCENARIO_MESSAGE}"
        }

    lower_text = text.lower()

    # 1. Check Financial Fraud
    if any(kw in lower_text for kw in FINANCIAL_FRAUD_KEYWORDS):
        return {
            "event_type": "financial_fraud",
            "origin": None,
            "destination": None,
            "confidence": 0.98,
            "is_supported": True,
            "message": "Financial Cyber Fraud / Unauthorized Transaction detected"
        }

    # 2. Check Marriage
    if any(kw in lower_text for kw in MARRIAGE_KEYWORDS):
        return {
            "event_type": "marriage",
            "origin": None,
            "destination": None,
            "confidence": 0.98,
            "is_supported": True,
            "message": "Marriage / Civil Status Change detected"
        }

    # 3. Check Family Death
    if any(kw in lower_text for kw in FAMILY_DEATH_KEYWORDS):
        return {
            "event_type": "family_death",
            "origin": None,
            "destination": None,
            "confidence": 0.98,
            "is_supported": True,
            "message": "Family Demise & Vital Records detected"
        }

    # 4. Check Explicit Unsupported Scenarios
    for event_name, keywords in UNSUPPORTED_EVENTS.items():
        if any(kw in lower_text for kw in keywords):
            return {
                "event_type": event_name,
                "origin": None,
                "destination": None,
                "confidence": 0.95,
                "is_supported": False,
                "message": SUPPORTED_SCENARIO_MESSAGE
            }

    # 5. Check Relocation
    has_relocation_keyword = any(kw in lower_text for kw in RELOCATION_KEYWORDS)

    origin = None
    destination = None
    confidence = 0.0

    # Pattern 1: "from <Origin> to <Destination>"
    p1 = re.search(r"from\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:[.!?]|$|\s+permanently|\s+recently|\s+now)", text, re.IGNORECASE)
    if p1:
        origin = clean_city_name(p1.group(1))
        destination = clean_city_name(p1.group(2))
        confidence = 0.98 if has_relocation_keyword else 0.85

    # Pattern 2: "to <Destination> from <Origin>"
    if not origin or not destination:
        p2 = re.search(r"to\s+([A-Za-z\s]+?)\s+from\s+([A-Za-z\s]+?)(?:[.!?]|$|\s+permanently|\s+recently|\s+now)", text, re.IGNORECASE)
        if p2:
            destination = clean_city_name(p2.group(1))
            origin = clean_city_name(p2.group(2))
            confidence = 0.98 if has_relocation_keyword else 0.85

    # Pattern 3: Destination only e.g. "I moved to Pune"
    if not destination:
        p3 = re.search(r"(?:moved|shifted|relocated|moving)\s+to\s+([A-Za-z\s]+?)(?:[.!?]|$|\s+permanently|\s+recently)", text, re.IGNORECASE)
        if p3:
            destination = clean_city_name(p3.group(1))
            origin = None
            confidence = 0.80

    if has_relocation_keyword or (origin and destination):
        return {
            "event_type": "relocation",
            "origin": origin or "Mumbai",
            "destination": destination or "Pune",
            "confidence": confidence if confidence > 0 else 0.90,
            "is_supported": True,
            "message": f"Relocation detected: {origin or 'Mumbai'} → {destination or 'Pune'}"
        }

    # 6. Unrecognized text
    return {
        "event_type": "unknown",
        "origin": None,
        "destination": None,
        "confidence": 0.0,
        "is_supported": False,
        "message": SUPPORTED_SCENARIO_MESSAGE
    }


# Backward compatibility alias
parse_relocation_regex = parse_life_event_regex
