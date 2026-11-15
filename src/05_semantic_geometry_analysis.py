import pickle
import numpy as np
import umap
import os
import glob
import pandas as pd
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt

# ==========================
# 1. CONFIGURAZIONE PERCORSI
# ==========================
folder_path = "." # O il tuo percorso "."
pattern = os.path.join(folder_path, "*_sentences_embeddings.pkl")
embedding_files = glob.glob(pattern)

if not embedding_files:
    print("Nessun file .pkl trovato. Controlla il percorso!")
    exit()

summary_metrics = []

# ==========================
# 2. FUNZIONI METRICHE (HIGH-DIM)
# ==========================
def compute_clinical_metrics(embeddings):
    """
    Calcola metriche nello spazio originale (SBERT) per evitare distorsioni UMAP.
    """
    if len(embeddings) < 3:
        return 0, 0, 0, 0

    # A. Instability Index (Lunghezza media del passo semantico)
    # Rappresenta quanto Alex "salta" tra una frase e l'altra
    diffs = np.linalg.norm(embeddings[1:] - embeddings[:-1], axis=1)
    instability_index = np.mean(diffs)
    total_path = np.sum(diffs)

    # B. Semantic Drift (Angolo medio di cambiamento)
    # Un angolo alto (vicino a pigreco) indica inversione di marcia o confusione
    angles = []
    for i in range(len(embeddings) - 2):
        v1 = embeddings[i+1] - embeddings[i]
        v2 = embeddings[i+2] - embeddings[i+1]
        norm_prod = np.linalg.norm(v1) * np.linalg.norm(v2)
        if norm_prod > 1e-6:
            cos_theta = np.dot(v1, v2) / norm_prod
            angles.append(np.arccos(np.clip(cos_theta, -1.0, 1.0)))
    
    mean_drift = np.mean(angles) if angles else 0

    # C. Semantic Density (Radius of Gyration)
    # Quanto è compatto il cluster del pensiero (ossessività vs dispersione)
    centroid = np.mean(embeddings, axis=0)
    density = np.mean(np.linalg.norm(embeddings - centroid, axis=1))

    return total_path, instability_index, mean_drift, density

# ==========================
# 3. LOOP DI ANALISI
# ==========================
for file_path in embedding_files:
    person_name = os.path.basename(file_path).replace("_sentences_embeddings.pkl", "")
    print(f"Analisi in corso: {person_name}")

    with open(file_path, "rb") as f:
        data = pickle.load(f)

    # Normalizzazione necessaria per distanze Coseno coerenti
    embeddings_norm = normalize(np.array(data["embeddings"]))
    session_ids = np.array(data["session_ids"])

    # Calcolo coordinate UMAP solo per il plot
    reducer = umap.UMAP(n_neighbors=10, min_dist=0.1, metric="cosine", random_state=42)
    coords_2d = reducer.fit_transform(embeddings_norm)

    # Plot Setup
    plt.figure(figsize=(10, 8))
    
    # Analisi per ogni sessione
    for sid in np.unique(session_ids):
        mask = session_ids == sid
        sess_embs = embeddings_norm[mask]
        sess_coords = coords_2d[mask]

        # Calcolo Metriche Reali
        t_path, inst_idx, drift, dens = compute_clinical_metrics(sess_embs)

        # Salvataggio dati
        summary_metrics.append({
            "subject": person_name,
            "session_id": sid,
            "instability_index": inst_idx,
            "semantic_drift_rad": drift,
            "semantic_density": dens,
            "total_trajectory": t_path
        })

        # Plot Traiettoria
        plt.plot(sess_coords[:, 0], sess_coords[:, 1], marker='o', label=f"Sess {sid} (Inst: {inst_idx:.2f})", alpha=0.8)

    plt.title(f"Mappa delle Traiettorie Semantiche: {person_name}")
    plt.legend()
    plt.grid(alpha=0.3)
    
    # Salva il grafico
    plot_name = f"{person_name}_metrics_map.png"
    plt.savefig(plot_name)
    print(f"Grafico salvato: {plot_name}")

# ==========================
# 4. EXPORT FINALE
# ==========================
df_final = pd.DataFrame(summary_metrics)
df_final.to_csv("analisi_clinica_traiettorie.csv", index=False)
print("REPORT FINALE GENERATO: analisi_clinica_traiettorie.csv")
print(df_final.head())