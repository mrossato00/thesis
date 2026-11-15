# =========================================================
# BELIEF–ACTION CONTRADICTION DETECTION PIPELINE
# spaCy + Transformers (NLI) + Psychological Features
# =========================================================

# pip install spacy transformers torch pandas
# python -m spacy download en_core_web_sm

import spacy
import pandas as pd
from transformers import pipeline

# ---------------------------------------------------------
# 1. LOAD MODELS
# ---------------------------------------------------------

print("Loading spaCy...")
nlp = spacy.load("en_core_web_sm")

print("Loading NLI model (this may take a minute)...")
nli = pipeline("text-classification", model="roberta-large-mnli")

# ---------------------------------------------------------
# 2. FEATURE LEXICONS
# ---------------------------------------------------------

LOW_AGENCY = {
    "can't", "cannot", "don't know", "unable", "lost",
    "helpless", "confused", "stuck"
}

HIGH_AGENCY = {
    "try", "trying", "do", "act", "decide", "handle",
    "manage", "fix", "work on", "cope"
}

NEGATIVE_WORDS = {
    "bad", "lost", "overwhelmed", "pointless", "gutted",
    "sad", "empty", "afraid", "anxious", "stuck"
}

POSITIVE_WORDS = {
    "good", "fine", "fun", "happy", "better", "okay"
}

AVOIDANCE_WORDS = {
    "avoid", "withdraw", "hide", "stay", "stop", "shut down",
    "leave", "disappear"
}

APPROACH_WORDS = {
    "try", "talk", "engage", "connect", "go", "reach out",
    "meet", "be with", "fix"
}

# ---------------------------------------------------------
# 3. FEATURE FUNCTIONS
# ---------------------------------------------------------

def detect_agency(text):
    text = text.lower()
    
    if any(phrase in text for phrase in LOW_AGENCY):
        return "low"
    elif any(phrase in text for phrase in HIGH_AGENCY):
        return "high"
    else:
        return "medium"


def detect_valence(text):
    text = text.lower()
    
    if any(word in text for word in NEGATIVE_WORDS):
        return "negative"
    elif any(word in text for word in POSITIVE_WORDS):
        return "positive"
    else:
        return "neutral"


def detect_action_type(text):
    text = text.lower()
    
    if any(word in text for word in AVOIDANCE_WORDS):
        return "avoidance"
    elif any(word in text for word in APPROACH_WORDS):
        return "approach"
    else:
        return "other"


# ---------------------------------------------------------
# 4. NLI FUNCTION
# ---------------------------------------------------------

def run_nli(belief, action):
    text = f"{belief} </s></s> {action}"
    result = nli(text)[0]

    label_map = {
        "LABEL_0": "contradiction",
        "LABEL_1": "neutral",
        "LABEL_2": "entailment"
    }

    return label_map[result["label"]], round(result["score"], 3)


# ---------------------------------------------------------
# 5. PSYCHOLOGICAL CONTRADICTION DETECTOR
# ---------------------------------------------------------

def psychological_contradiction(belief, action):

    belief_agency = detect_agency(belief)
    action_agency = detect_agency(action)

    belief_valence = detect_valence(belief)
    action_type = detect_action_type(action)

    flags = []

    # Agency mismatch
    if belief_agency == "low" and action_agency == "high":
        flags.append("agency_mismatch")

    # Emotional masking (negative belief + social approach)
    if belief_valence == "negative" and action_type == "approach":
        flags.append("possible_masking")

    # Withdrawal loop
    if belief_valence == "negative" and action_type == "avoidance":
        flags.append("withdrawal_pattern")

    return flags


# ---------------------------------------------------------
# 6. MAIN ANALYSIS FUNCTION
# ---------------------------------------------------------

def analyze_pair(patient, belief, action):

    nli_label, nli_score = run_nli(belief, action)

    belief_agency = detect_agency(belief)
    action_agency = detect_agency(action)

    belief_valence = detect_valence(belief)
    action_type = detect_action_type(action)

    flags = psychological_contradiction(belief, action)

    return {
        "patient": patient,
        "belief": belief,
        "action": action,
        "nli_label": nli_label,
        "nli_score": nli_score,
        "belief_agency": belief_agency,
        "action_agency": action_agency,
        "belief_valence": belief_valence,
        "action_type": action_type,
        "psychological_flags": ", ".join(flags) if flags else "none"
    }


# ---------------------------------------------------------
# 7. EXAMPLE DATASET (usa i tuoi)
# ---------------------------------------------------------

data = [
    ("juanita", "I don't know what the right moves are", "I just watch and try to copy them"),
    ("juanita", "It feels like another mountain to climb", "Every step feels like I might fall"),
    ("alex", "It feels like part of me got erased", "I try to be the fun friend"),
    ("alex", "I feel gutted", "I act like everything is fine"),
    ("alex", "I don't want them to see me struggling", "I keep acting normal")
]

# ---------------------------------------------------------
# 8. RUN ANALYSIS
# ---------------------------------------------------------

results = [analyze_pair(p, b, a) for p, b, a in data]

df = pd.DataFrame(results)

print("\n===== RESULTS =====\n")
print(df)


# ---------------------------------------------------------
# 9. OPTIONAL: SAVE TO CSV
# ---------------------------------------------------------

df.to_csv("belief_action_contradictions.csv", index=False)
print("\nFile saved as belief_action_contradictions.csv")