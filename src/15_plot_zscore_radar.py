import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from math import pi
import matplotlib

# Evita errori macOS
matplotlib.use('Agg')

# --- CONFIGURATION ---
base_folder = "."
patient_id = "Juanita" # Usiamo il nome coerente con il tuo dizionario colori
input_file = os.path.join(base_folder, "juanita_delgado_001_vs_traits.csv")
output_file = os.path.join(base_folder, "juanita_zscore_matched_style.png")

# Palette dal tuo script di comparazione
patient_colors = {"Juanita": "#7fb3d5", "Baseline": "#f1948a"}

# I 6 parametri richiesti nell'ordine corretto
target_params = ['SEEKING', 'FEAR', 'CARE', 'LUST', 'PANIC', 'PLAY']

def run_matched_style_analysis():
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        return

    # 1. Caricamento e pulizia dati
    df_raw = pd.read_csv(input_file)
    df_raw['System'] = df_raw['System'].replace({'PANIC_GRIEF': 'PANIC'})

    # 2. Data Padding per avere i 6 parametri esatti
    rows = []
    for p in target_params:
        if p in df_raw['System'].values:
            row = df_raw[df_raw['System'] == p].iloc[0]
            rows.append({'System': p, 'Baseline_Trait': row['Baseline_Trait'], 'Observed_Mean': row['Observed_Mean']})
        else:
            # Valori minimi per i sistemi non rilevati
            rows.append({'System': p, 'Baseline_Trait': 0.1, 'Observed_Mean': 0.01})
    
    df = pd.DataFrame(rows)

    # 3. Calcolo Z-Scores
    df['Z_YAML'] = (df['Baseline_Trait'] - df['Baseline_Trait'].mean()) / df['Baseline_Trait'].std()
    df['Z_Observed'] = (df['Observed_Mean'] - df['Observed_Mean'].mean()) / df['Observed_Mean'].std()

    # Prepariamo i dati per il radar
    categories = df['System'].tolist()
    N = len(categories)
    z_yaml = df['Z_YAML'].tolist() + [df['Z_YAML'].tolist()[0]]
    z_observed = df['Z_Observed'].tolist() + [df['Z_Observed'].tolist()[0]]
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # --- CREAZIONE FIGURA (Stesso stile del comparativo) ---
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, polar=True)
    
    # Colore Paziente e Baseline
    color_pax = patient_colors["Juanita"]
    color_base = patient_colors["Baseline"]

    # Plot Baseline (YAML)
    ax.plot(angles, z_yaml, color=color_base, linewidth=2, linestyle='dashed', label='Baseline (YAML)')
    ax.fill(angles, z_yaml, color=color_base, alpha=0.1)

    # Plot Juanita (NLP)
    ax.plot(angles, z_observed, color=color_pax, linewidth=4, linestyle='solid', label='Observed (NLP)')
    ax.fill(angles, z_observed, color=color_pax, alpha=0.3)

    # --- ETICHETTE CATEGORIE ---
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold', color='#444444')

    # --- AGGIUNTA VALORI CON SFONDO COLORATO (BBOX) ---
    # Lo facciamo solo per i dati osservati (NLP) per non sporcare troppo
    for angle, value in zip(angles[:-1], z_observed[:-1]):
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec=color_pax, lw=1, alpha=0.8)
        ax.text(angle, value + 0.3, f"{value:.1f}σ", ha='center', va='center',
                fontsize=10, fontweight='bold', color=color_pax, bbox=bbox_props)

    # --- TITOLO E GRIGLIA ---
    ax.set_title(f"Z-Score Profile: {patient_id}", size=18, color=color_pax, fontweight='bold', pad=30)
    
    # Griglia con lo stile richiesto
    ax.set_ylim(-3, 3) 
    ax.grid(True, linestyle='--', alpha=0.5)

    # Legenda semplice
    plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Grafico in stile matched salvato: {output_file}")

    # --- DIDASCALIA PER LA TESI ---
    print("\n--- DIDASCALIA CONSIGLIATA ---")
    print(f"Figura X: Profilo comparativo Z-Score per {patient_id}. La linea blu rappresenta l'espressione emotiva rilevata via NLP, mentre la linea rossa tratteggiata indica il baseline teorico. I valori sono espressi in deviazioni standard (σ) per evidenziare la gerarchia relativa dei sistemi affettivi di Panksepp.")

if __name__ == "__main__":
    run_matched_style_analysis()