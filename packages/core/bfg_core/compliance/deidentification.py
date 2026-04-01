"""De-identification of qualitative feedback for DSGVO compliance."""

import re

PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[E-MAIL ENTFERNT]"),
    (r"\b(\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b", "[TELEFON ENTFERNT]"),
    (r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", "[DATUM ENTFERNT]"),
    (r"\b(Abteilungsleiter|Teamleiter|CEO|CTO|CFO|COO|VP|Director)\s+\w+\b", "[ROLLE ENTFERNT]"),
]


def deidentify_text(text: str, target_name: str = "") -> tuple[str, list[str]]:
    """Remove PII from qualitative feedback text."""
    removals = []

    if target_name:
        parts = target_name.split()
        for part in parts:
            if len(part) > 2:
                count = text.lower().count(part.lower())
                if count > 0:
                    text = re.sub(re.escape(part), "[PERSON]", text, flags=re.IGNORECASE)
                    removals.append(f"Name '{part}' removed ({count}x)")

    for pattern, replacement in PII_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, replacement, text)
            removals.append(f"Pattern matched: {len(matches)}x -> {replacement}")

    return text, removals
