import pickle
import glob
import os
import numpy as np
from sentence_transformers import util
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import pandas as pd

# ---------- 1. Setup ----------
folder_path = "/Users/marti/Desktop/thesis/patients"
pattern = os.path.join(folder_path, "*_sentences_embeddings.pkl")
embedding_files = glob.glob(pattern)

if len(embedding_files) == 0:
    print("Nessun file embeddings trovato.")
    exit()

print("File trovati:")
for f in embedding_files:
    print(" -", f)

summary_results = []

# ---------- 2. Analisi per ogni persona ----------
for selected_file in embedding_files:

    file_name = os.path.basename(selected_file)
    person_name = file_name.replace("_sentences_embeddings.pkl", "")
    print(f"\n=== Analizzando: {person_name} ===")

    # Carica dati
    with open(selected_file, "rb") as f:
        data = pickle.load(f)

    texts = data["texts"]
    embeddings = np.array(data["embeddings"])
    session_ids = data["session_ids"]

    print(f"Totale frasi: {len(texts)}")
    print(f"Totale sessioni: {len(set(session_ids))}")

    # Normalizzazione
    normalized_embeddings = normalize(embeddings)

    # Distanze semantiche
    semantic_distances = []

    for i in range(len(normalized_embeddings) - 1):
        similarity = util.cos_sim(
            normalized_embeddings[i],
            normalized_embeddings[i + 1]
        ).item()
        distance = 1 - similarity
        semantic_distances.append(distance)

    semantic_distances = np.array(semantic_distances)

    mean_d = semantic_distances.mean()
    max_d = semantic_distances.max()
    min_d = semantic_distances.min()
    std_d = semantic_distances.std()

    print("Analisi coerenza narrativa")
    print(f"Distanza media: {mean_d:.4f}")
    print(f"Distanza max  : {max_d:.4f}")
    print(f"Distanza min  : {min_d:.4f}")

    # ---------- 3. Salva CSV per persona ----------
    df_dist = pd.DataFrame({
        "transition_index": range(1, len(semantic_distances) + 1),
        "semantic_distance": semantic_distances
    })

    csv_path = os.path.join(folder_path, f"{person_name}_semantic_distances.csv")
    df_dist.to_csv(csv_path, index=False)

    # ---------- 4. Salva grafico ----------
    plt.figure(figsize=(12, 5))
    plt.plot(semantic_distances, marker='o')
    plt.title(f"Distanza Semantica - {person_name.capitalize()}")
    plt.xlabel("Transizione")
    plt.ylabel("Distanza (1 - cosine similarity)")
    plt.tight_layout()

    plot_path = os.path.join(folder_path, f"{person_name}_semantic_plot.png")
    plt.savefig(plot_path)
    plt.close()

    print(f"CSV salvato in: {csv_path}")
    print(f"Plot salvato in: {plot_path}")

    # Salva per confronto globale
    summary_results.append({
        "person": person_name,
        "mean_distance": mean_d,
        "std_distance": std_d,
        "max_distance": max_d,
        "min_distance": min_d
    })

# ---------- 5. Salva riepilogo comparativo ----------
df_summary = pd.DataFrame(summary_results)
summary_path = os.path.join(folder_path, "semantic_coherence_summary.csv")
df_summary.to_csv(summary_path, index=False)

print("\n=== Riepilogo salvato in ===")
print(summary_path)