import pandas as pd
import yaml
import os

# ===============================
# 1. CONFIGURAZIONE
# ===============================
patient_id = "juanita_delgado_001"
base_folder = "/Users/marti/Desktop/thesis/patients"
yaml_path = os.path.join(base_folder, f"{patient_id}.yaml")

# Percorsi dei file generati dallo script 07
panksepp_csv = os.path.join(base_folder, f"juanita_panksepp_profile.csv")
instability_csv = os.path.join(base_folder, f"juanita_instability.csv")
output_csv = os.path.join(base_folder, f"{patient_id}_vs_traits.csv")

def run_comparison():
    # --- 1. Caricamento YAML ---
    if not os.path.exists(yaml_path):
        print(f"❌ Errore: File YAML non trovato in {yaml_path}")
        return
    
    with open(yaml_path, "r", encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # --- 2. ACCESSO CORRETTO ALLE CHIAVI (Fix KeyError) ---
    try:
        # Percorso: clinical -> emotionTraits
        clinical_data = config.get('clinical', {})
        traits_config = clinical_data.get('emotionTraits', {})
        
        traits = traits_config.get('trait_baseline', {})
        target_volatility = traits_config.get('volatility_level', 'unknown')
        
        if not traits:
            print("❌ Errore: Impossibile trovare 'trait_baseline' dentro 'clinical/emotionTraits'")
            return
            
    except Exception as e:
        print(f"❌ Errore durante la lettura dello YAML: {e}")
        return

    # --- 3. Caricamento Dati Processati (CSV) ---
    if not os.path.exists(panksepp_csv):
        print(f"❌ Errore: File CSV Panksepp non trovato per {patient_id}. Controlla lo script 07.")
        return
    
    df_pank = pd.read_csv(panksepp_csv)
    # Calcolo medie reali (escludendo session_id)
    patient_means = df_pank.drop(columns=["session_id"], errors='ignore').mean().to_dict()

    # --- 4. Calcolo Instabilità ---
    real_instability = 0.0
    if os.path.exists(instability_csv):
        df_inst = pd.read_csv(instability_csv)
        real_instability = df_inst["instability"].mean()

    # --- 5. Generazione Confronto ---
    comparison_rows = []
    
    for system, baseline_val in traits.items():
        # Filtriamo solo i sistemi con valori numerici validi
        if baseline_val is not None and system in patient_means:
            observed = patient_means[system]
            delta = observed - baseline_val
            
            # Interpretazione clinica basata sullo scostamento
            if delta > 0.10:
                status = "SOPRA (Iper-attivazione)"
            elif delta < -0.10:
                status = "SOTTO (Inibizione)"
            else:
                status = "In linea"
                
            comparison_rows.append({
                "System": system,
                "Baseline_Trait": baseline_val,
                "Observed_Mean": round(observed, 3),
                "Delta": round(delta, 3),
                "Status": status
            })

    # Salvataggio
    df_final = pd.DataFrame(comparison_rows)
    df_final.to_csv(output_csv, index=False)

    # --- 6. Risultato a Video ---
    observed_vol_label = "high" if real_instability > 0.08 else "low" # Soglia per BPD
    
    print(f"\n✅ Analisi completata per: {config.get('profile', {}).get('name', patient_id)}")
    print("-" * 60)
    print(df_final.to_string(index=False))
    print("-" * 60)
    print(f"Volatilità Attesa: {target_volatility}")
    print(f"Volatilità Reale:  {observed_vol_label} ({round(real_instability, 4)})")
    print(f"File creato: {output_csv}\n")

if __name__ == "__main__":
    run_comparison()