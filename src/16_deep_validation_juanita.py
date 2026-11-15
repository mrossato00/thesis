import pandas as pd
import numpy as np
import pickle
import os
from scipy.stats import pearsonr

# --- CONFIGURAZIONE ---
base_folder = "."
patient_id = "juanita_delgado_001"
# Usiamo il nome del file embeddings originale 
embeddings_file = os.path.join(base_folder, "juanita_sentences_embeddings.pkl")
zscore_file = os.path.join(base_folder, "juanita_delgado_001_zscore_analysis.csv")

def perform_deep_validation():
    print(f"--- VALIDAZIONE PROFONDA: {patient_id} ---\n")

    # 1. CALCOLO CORRELAZIONE DI PEARSON
    if os.path.exists(zscore_file):
        df_z = pd.read_csv(zscore_file)
        # Calcoliamo la correlazione tra il Tratto (YAML) e l'Osservato (NLP)
        corr, p_value = pearsonr(df_z['Baseline_Trait'], df_z['Observed_Mean'])
        
        print(f"📊 INDICE DI CORRELAZIONE DI PEARSON: {round(corr, 3)}")
        if corr > 0.7:
            print("   -> Risultato: Forte somiglianza nella gerarchia emotiva.")
        elif corr > 0.3:
            print("   -> Risultato: Somiglianza moderata.")
        else:
            print("   -> Risultato: Scarsa somiglianza (i due profili non concordano).")
        print(f"   (p-value: {round(p_value, 4)})\n")

    # 2. SPOT CHECK DELLE FRASI (Controllo Qualità AI)
    if os.path.exists(embeddings_file):
        with open(embeddings_file, "rb") as f:
            data = pickle.load(f)
        
        # Prendiamo i testi originali
        sentences = data["texts"]
        
        print(f"📝 ESTRAZIONE CAMPIONE TESTI (Prime 10 frasi analizzate):")
        print("-" * 60)
        # Mostriamo le prime 10 frasi per capire il "tono" del dataset
        for i, sent in enumerate(sentences[:10]):
            print(f"{i+1}. {sent}")
        print("-" * 60)
        print("\n👉 AZIONE: Leggi queste frasi. Ti sembrano cariche di PANIC/GRIEF?")
        print("Se sì, il modello AI sta sottostimando. Se no, la paziente è 'piatta'.")
    else:
        print(f"❌ File embeddings non trovato in: {embeddings_file}")

if __name__ == "__main__":
    perform_deep_validation()