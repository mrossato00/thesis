# ===============================
# 07_emotional_pattern_consistency.py
# ===============================

import glob
import os
import pickle
import numpy as np
import pandas as pd
from transformers import pipeline

# ===============================
# 1. CONFIGURAZIONE PERCORSI
# ===============================
folder_path = "/Users/marti/Desktop/thesis/patients"
embedding_pattern = os.path.join(folder_path, "*_sentences_embeddings.pkl")
embedding_files = glob.glob(embedding_pattern)

if not embedding_files:
    print("Nessun file embeddings trovato!")
    exit()

# ===============================
# 2. MODELLO EMOTION
# ===============================
print("Caricamento modello emotion classifier...")
# top_k=None ensures we get all 7 emotions for every sentence
emotion_clf = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base", 
    top_k=None
)

# ===============================
# 3. MAPPING CLINICO & PANKSEPP
# ===============================
clinical_map = {
    "anger": "Anger / Irritability",
    "fear": "Anxiety / Worry",
    "sadness": "Depressive Affect",
    "joy": "Positive Affect",
    "surprise": "Unexpected / Alert",
    "disgust": "Aversion / Avoidance",
    "neutral": "Neutral State"
}

panksepp_map = {
    "anger": "RAGE",
    "fear": "FEAR",
    "sadness": "PANIC_GRIEF",
    "joy": "SEEKING_PLAY",
    "surprise": "SEEKING",
    "disgust": "FEAR"  # Associated with avoidance/withdrawal
}

# ===============================
# 4. LOOP SU PAZIENTI
# ===============================
all_results = []

for file_path in embedding_files:
    person_name = os.path.basename(file_path).replace("_sentences_embeddings.pkl", "")
    print(f"\n🔍 Analizzando {person_name}...")

    with open(file_path, "rb") as f:
        data = pickle.load(f)

    sentences = data["texts"]
    session_ids = data.get("session_ids", [1]*len(sentences))

    # 4a. EMOTION PER FRASE (Batch Processing for speed)
    print(f"   ...elaborazione di {len(sentences)} frasi")
    raw_outputs = emotion_clf(sentences)
    
    emotion_scores = []
    for output in raw_outputs:
        # Convert list of dicts to a single flat dict
        emotion_scores.append({d['label'].lower(): d['score'] for d in output})

    df_sent = pd.DataFrame(emotion_scores)
    df_sent["session_id"] = session_ids

    # 4b. MEDIA PER SESSIONE
    # We exclude 'session_id' from the mean calculation itself
    session_emotions = df_sent.groupby("session_id").mean().reset_index()
    
    # Identify only the emotion columns for calculations
    emo_cols = [c for c in session_emotions.columns if c != "session_id"]

    # 4c. INSTABILITY (Mean Absolute Change)
    instability_scores = []
    if len(session_emotions) > 1:
        for i in range(1, len(session_emotions)):
            diff = np.abs(session_emotions.loc[i, emo_cols] - session_emotions.loc[i-1, emo_cols])
            instability_scores.append(diff.mean())
    
    mean_instability = np.mean(instability_scores) if instability_scores else 0

    # 4d. MAPPING CLINICO
    session_clinical = session_emotions.rename(columns=clinical_map)

    # 4e. MAPPING PANKSEPP
    pank_data = {}
    for emo, sys in panksepp_map.items():
        if emo in session_emotions.columns:
            if sys not in pank_data:
                pank_data[sys] = session_emotions[emo]
            else:
                # If multiple emotions map to one system, take the mean
                pank_data[sys] = (pank_data[sys] + session_emotions[emo]) / 2

    panksepp_df = pd.DataFrame(pank_data)
    panksepp_df["session_id"] = session_emotions["session_id"]

    # 4f. SALVATAGGIO
    session_emotions.to_csv(os.path.join(folder_path, f"{person_name}_emotion_raw.csv"), index=False)
    session_clinical.to_csv(os.path.join(folder_path, f"{person_name}_emotion_clinical.csv"), index=False)
    panksepp_df.to_csv(os.path.join(folder_path, f"{person_name}_panksepp_profile.csv"), index=False)

    if instability_scores:
        pd.DataFrame({
            "session_transition": list(range(2, len(session_emotions)+1)),
            "instability": instability_scores
        }).to_csv(os.path.join(folder_path, f"{person_name}_instability.csv"), index=False)

    all_results.append({
        "person": person_name,
        "mean_instability": mean_instability
    })

# ===============================
# 5. SUMMARY FINALE
# ===============================
df_summary = pd.DataFrame(all_results)
df_summary.to_csv(os.path.join(folder_path, "emotional_summary.csv"), index=False)

print("Analisi completata!")