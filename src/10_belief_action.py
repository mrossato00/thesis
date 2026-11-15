# =========================================================
# ANALISI BELIEF–ACTION CON PROFILO MULTIDIMENSIONALE
# Basato sul YAML clinico completo di Juanita
# =========================================================

# pip install pyyaml spacy pandas
# python -m spacy download en_core_web_sm

import yaml
import spacy
import pandas as pd

# ---------------------------------------------------------
# 1. LOAD spaCy
# ---------------------------------------------------------
nlp = spacy.load("en_core_web_sm")

# ---------------------------------------------------------
# 2. FEATURE LEXICONS
# ---------------------------------------------------------
LOW_AGENCY = {"can't", "cannot", "don't know", "unable", "lost", "helpless", "confused", "stuck"}
HIGH_AGENCY = {"try", "trying", "do", "act", "decide", "handle", "manage", "fix", "work on", "cope"}

NEGATIVE_WORDS = {"bad", "lost", "overwhelmed", "pointless", "gutted", "sad", "empty", "afraid", "anxious", "stuck"}
POSITIVE_WORDS = {"good", "fine", "fun", "happy", "better", "okay"}

AVOIDANCE_WORDS = {"avoid", "withdraw", "hide", "stay", "stop", "shut down", "leave", "disappear"}
APPROACH_WORDS = {"try", "talk", "engage", "connect", "go", "reach out", "meet", "be with", "fix"}

# ---------------------------------------------------------
# 3. FUNZIONI FEATURE
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
# 4. LOAD YAML PROFILO PAZIENTE
# ---------------------------------------------------------
yaml_path = "/Users/marti/Desktop/thesis/patients/juanita_delgado_001.yaml"
with open(yaml_path, 'r') as f:
    juanita_yaml = yaml.safe_load(f)

# ---------------------------------------------------------
# 5. ESTRAZIONE PROFILO MULTIDIMENSIONALE
# ---------------------------------------------------------
# Usando campi clinici chiave per agency, valence, tendency
profile = {}

# Agency basata su identità, impulseControl e comportamento sociale
impulse = juanita_yaml["clinical"]["clinicalFunctioning"]["mentalFunctioningAxis"]["impulseControl"]["impairment"]
profile["agency"] = "low" if impulse in ["marked", "high"] else "medium"

# Valence basata su affectExperienceAndRegulation e selfEsteemRegulation
affect = juanita_yaml["clinical"]["clinicalFunctioning"]["mentalFunctioningAxis"]["affectExperienceAndRegulation"]["impairment"]
selfesteem = juanita_yaml["clinical"]["clinicalFunctioning"]["mentalFunctioningAxis"]["selfEsteemRegulation"]["impairment"]
profile["valence"] = "negative" if affect in ["marked", "high", "moderate_to_marked"] or selfesteem in ["marked", "high"] else "neutral"

# Action tendency basata su behaviorDuringTestAdministration e relationshipsAndIntimacy
profile["action_type"] = "avoidance"  # coerente con ritiro sociale e oscillazioni tra vicinanza e ritiro

print("Profilo multidimensionale estratto:")
print(profile)

# ---------------------------------------------------------
# 6. ANALISI COPPIE BELIEF–ACTION
# ---------------------------------------------------------
def analyze_pair(belief, action):
    agency_obs = detect_agency(action)
    valence_obs = detect_valence(action)
    action_type_obs = detect_action_type(action)

    # Score di coerenza (0-3)
    score = 0
    if agency_obs == profile["agency"]:
        score += 1
    if valence_obs == profile["valence"]:
        score += 1
    if action_type_obs == profile["action_type"]:
        score += 1

    # Alignment flags
    flags = []
    if action_type_obs != profile["action_type"]:
        flags.append("withdrawal_or_masking")

    return {
        "belief": belief,
        "action": action,
        "agency_observed": agency_obs,
        "valence_observed": valence_obs,
        "action_type_observed": action_type_obs,
        "alignment_score": score / 3,  # normalizzato 0-1
        "flags": ", ".join(flags) if flags else "none"
    }

# ---------------------------------------------------------
# 7. ESEMPIO COPPIE
# ---------------------------------------------------------
pairs = [
    ("I don't know what the right moves are", "I just watch and try to copy them"),
    ("It feels like another mountain to climb", "Every step feels like I might fall"),
    ("I feel like I'm failing", "I withdraw from social contact"),
    ("Sometimes it feels like relief to just stop", "I do nothing and stay isolated")
]

# Analisi
results = [analyze_pair(b, a) for b, a in pairs]
df = pd.DataFrame(results)

print("\n===== BELIEF–ACTION ANALYSIS PER JUANITA =====\n")
print(df)

# Salva CSV
df.to_csv("/Users/marti/Desktop/thesis/patients/juanita_belief_action_analysis.csv", index=False)
print("\nRisultati salvati in juanita_belief_action_analysis.csv")