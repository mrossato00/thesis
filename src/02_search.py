import pickle
import glob
import os
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer, util

# ---------- 1. Setup ----------
folder_path = "."
pattern = os.path.join(folder_path, "*_sentences_embeddings.pkl")

files = glob.glob(pattern)

if len(files) == 0:
    print("Nessun file embeddings trovato.")
    exit()

print("File trovati:")
for f in files:
    print(" -", f)

# ---------- 2. Modello ----------
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# ---------- 3. Query emotive ----------
emotion_queries = {
    "joy": "Feeling happy, joyful, satisfied, grateful",
    "sadness": "Feeling sad, disappointed, down, low mood",
    "anger": "Feeling angry, frustrated, irritated",
    "fear": "Feeling anxious, scared, worried, insecure",
    "calm": "Feeling peaceful, calm, relaxed, balanced",
    "motivation": "Feeling motivated, driven, ambitious, inspired"
}

# Pre-calcoliamo gli embeddings delle emozioni
emotion_embeddings = {
    emotion: model.encode(text)
    for emotion, text in emotion_queries.items()
}

# ---------- 4. Analisi per ogni persona ----------
results = {}

for pkl_path in files:
    
    base_filename = os.path.basename(pkl_path)
    person_name = base_filename.replace("_sentences_embeddings.pkl", "")
    
    print(f"\n Analizzando: {person_name}")
    
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    
    embeddings = data["embeddings"]
    
    emotion_scores = {}
    
    for emotion, emo_emb in emotion_embeddings.items():
        
        # Calcola similarità tra emozione e tutte le frasi
        cos_scores = util.cos_sim(emo_emb, embeddings)[0]
        
        # Media delle similarità
        mean_score = float(cos_scores.mean().item())        
        emotion_scores[emotion] = mean_score
    
    results[person_name] = emotion_scores

# ---------- 5. Output comparativo ----------
print("\n" + "="*60)
print("MAPPA EMOTIVA COMPARATIVA")
print("="*60)

for person, scores in results.items():
    
    print(f"\n {person.upper()}")
    print("-"*40)
    
    # Ordiniamo dalla più dominante alla meno dominante
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for emotion, score in sorted_scores:
        print(f"{emotion:<12} → {score:.4f}")
        
# Convertiamo results in DataFrame
df = pd.DataFrame(results).T  # .T = persone come righe

# Salvataggio CSV comparativo
csv_path = os.path.join(folder_path, "emotional_comparison.csv")
df.to_csv(csv_path)

print("\nCSV comparativo salvato in:")
print(csv_path)