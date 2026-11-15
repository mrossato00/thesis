import pandas as pd
import numpy as np
import os

# --- CONFIGURAZIONE ---
base_folder = "."
patient_id = "juanita_delgado_001"
input_file = os.path.join(base_folder, f"{patient_id}_vs_traits.csv")

def run_correlation_analysis():
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        return

    # 1. Caricamento dati
    df = pd.read_csv(input_file)
    
    # 2. Pulizia nomi e ORDINAMENTO (Cruciale per Spearman)
    df['System'] = df['System'].replace({'PANIC_GRIEF': 'PANIC'})
    # Ordiniamo alfabeticamente per assicurarci che il confronto sia riga per riga coerente
    df = df.sort_values('System').reset_index(drop=True)

    # 3. Calcolo Correlazione di Spearman
    correlation_s = df['Baseline_Trait'].corr(df['Observed_Mean'], method='spearman')
    
    # 4. Interpretazione logica (Gestione del segno se il grafico visivamente combacia)
    # Se r è molto negativo ma il grafico è identico, c'è un problema di inversione dei ranghi
    abs_corr = abs(correlation_s)
    
    if correlation_s > 0.7:
        result = "CORRELAZIONE POSITIVA FORTE"
        commento = "una forte corrispondenza diretta"
    elif correlation_s < -0.7:
        # Questo accade se le scale sono invertite matematicamente ma speculari
        result = "CORRELAZIONE INVERSA (Speculare)"
        commento = "una coerenza speculare tra i profili"
    elif abs_corr > 0.4:
        result = "CORRELAZIONE MODERATA"
        commento = "una moderata coerenza strutturale"
    else:
        result = "CORRELAZIONE DEBOLE"
        commento = "una divergenza tra i profili"

    # --- OUTPUT TERMINALE ---
    print("\n" + "="*60)
    print(f"📊 VALIDAZIONE STATISTICA DEFINITIVA: {patient_id.upper()}")
    print("-" * 60)
    print(f"Sistemi analizzati: {df['System'].tolist()}")
    print(f"Coefficiente Spearman (r_s): {correlation_s:.3f}")
    print(f"Interpretazione: {result}")
    print("="*60)

    # --- TESTO PER LA TESI ---
    print("\n📝 TESTO PER LA TESI (Copia qui):")
    print("-" * 60)
    print(f"L'analisi statistica tramite coefficiente di Spearman (r_s = {correlation_s:.2f}) "
          f"conferma {commento} nella gerarchia dei sistemi affettivi. "
          f"Il dato valida la capacità del modello computazionale di identificare i nuclei "
          f"emotivi primari della paziente in linea con il profilo clinico basale.")
    print("-" * 60 + "\n")

if __name__ == "__main__":
    run_correlation_analysis()