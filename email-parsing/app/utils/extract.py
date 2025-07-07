from typing import List
import re

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    USE_SPACY = True
except ImportError:
    nlp = None
    USE_SPACY = False


def extract_company_names(emails: List[dict]) -> List[str]:
    company_names = []

    for email in emails:
        sender = email.get("from", "")
        subject = email.get("subject", "")

        # Extract from sender name (e.g., "John from Acme Inc <john@acme.com>")
        match = re.match(r"(.*)<.*>", sender)
        sender_name = match.group(1).strip() if match else sender

        # Try spaCy NER on sender name + subject
        if USE_SPACY:
            text = f"{sender_name} {subject}"
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PERSON", "GPE"]:
                    company_names.append(ent.text.strip())

        else:
            # Fallback: use simple heuristics
            words = sender_name.split()
            if len(words) > 1:
                company_names.append(" ".join(words[-2:]))  # Last two words
            else:
                company_names.append(words[0])

    # Deduplicate and clean
    cleaned = list({name.strip() for name in company_names if name.strip()})
    return cleaned
