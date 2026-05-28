import re
import spacy
from typing import List, Dict, Any

# Load spaCy model for entity recognition (optional but helpful)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If not installed, we can skip or handle it
    nlp = None

class PIIDetector:
    # Regex patterns for Indian Government PII
    PATTERNS = {
        "Aadhaar": r"\b\d{4}[\s-]\d{4}[\s-]\d{4}\b|\b\d{12}\b",
        "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
        "Passport": r"\b[A-Z][0-9]{7}\b",
        "Voter_ID": r"\b[A-Z]{3}[0-9]{7}\b",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Phone": r"\b(?:\+91|91)?[6-9]\d{9}\b",
        "Tamil_Aadhaar": r"ஆதார்\s*:\s*\d{4}\s\d{4}\s\d{4}",
        "Tamil_PAN": r"பான்\s*:\s*[A-Z]{5}[0-9]{4}[A-Z]{1}"
    }

    @staticmethod
    def detect(text: str) -> List[Dict[str, Any]]:
        results = []
        
        # 1. Regex Detection
        for label, pattern in PIIDetector.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                results.append({
                    "type": label,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.95,
                    "method": "regex"
                })

        # 2. NLP Detection (Improved)
        if nlp:
            doc = nlp(text)
            for ent in doc.ents:
                # Check for duplicates
                is_duplicate = any(r["start"] <= ent.start_char < r["end"] for r in results)
                if not is_duplicate:
                    label = ent.label_
                    # Map to friendly names for the template
                    if label == "PERSON":
                        label = "Full_Name"
                    elif label in ["GPE", "FAC", "LOC"]:
                        label = "Location"
                        
                    results.append({
                        "type": label,
                        "value": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8,
                        "method": "nlp"
                    })

        return results

    @staticmethod
    def classify_sensitivity(pii_type: str) -> str:
        high_sensitivity = ["Aadhaar", "PAN", "Passport", "Voter_ID"]
        medium_sensitivity = ["Phone", "Email"]
        
        if pii_type in high_sensitivity:
            return "High"
        elif pii_type in medium_sensitivity:
            return "Medium"
        else:
            return "Low"
