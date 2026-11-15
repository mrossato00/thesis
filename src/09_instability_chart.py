import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
import matplotlib

# Evita popup e messaggi di errore macOS nel terminale
matplotlib.use('Agg') 

# --- CONFIGURATION ---
folder_path = "/Users/marti/Desktop/thesis/patients"
instability_files = glob.glob(os.path.join(folder_path, "*_instability.csv"))

# Mapping esatto basato sui tuoi nomi file (senza .csv)
colors = {"juanita_instability": "#7fb3d5", "alex_instability": "#f1948a"} 
default_color = "#999999"

# Creazione figura con asse Y doppio
fig, ax1 = plt.subplots(figsize=(12, 7))
ax2 = ax1.twinx() 

sns.set_style("white")
ax1.grid(axis='y', linestyle='--', alpha=0.2, zorder=0)

for file_path in instability_files:
    # Estraiamo il nome del file senza estensione per il match del colore
    base_name = os.path.basename(file_path).replace(".csv", "")
    # Nome pulito per la legenda (es. Juanita)
    display_name = base_name.split('_')[0].capitalize()
    
    df_inst = pd.read_csv(file_path)
    
    if len(df_inst) > 1:
        current_color = colors.get(base_name, default_color)
        
        # --- 1. VALORI REALI (Asse Sinistro) ---
        ax1.plot(df_inst['session_transition'], df_inst['instability'], 
                 marker='o', markersize=6, color=current_color, 
                 linewidth=2, label=f"{display_name}", zorder=3)
        
        # Media (Baseline) del paziente - Linea tratteggiata
        mu = df_inst['instability'].mean()
        ax1.axhline(mu, color=current_color, linestyle='--', linewidth=1.2, alpha=0.5)
        
        # --- 2. Z-SCORE (Asse Destro) ---
        sigma = df_inst['instability'].std()
        # Se la deviazione è zero (dati piatti), lo z-score è 0
        df_inst['z_score'] = (df_inst['instability'] - mu) / (sigma if sigma != 0 else 1)
        
        # Lo Z-score lo facciamo punteggiato e sottile per non appesantire
        ax2.plot(df_inst['session_transition'], df_inst['z_score'], 
                 linestyle=':', color=current_color, linewidth=1, alpha=0.6)
        ax2.scatter(df_inst['session_transition'], df_inst['z_score'], 
                    color=current_color, s=20, alpha=0.4, marker='x')

# --- ESTETICA E ETICHETTE ---
ax1.set_title("Emotional Instability & Z-Score Analysis", fontsize=16, fontweight='bold', loc='left', pad=20)
ax1.set_xlabel("Session Transition", fontsize=12)
ax1.set_ylabel("Instability (Absolute Value)", fontsize=12)

# Asse destro per lo Z-score (Standard Deviations)
ax2.set_ylabel("Relative Deviation (Z-Score)", fontsize=12, color='gray')
ax2.set_ylim(-3, 3) # Range standard per vedere bene i picchi
ax2.axhline(0, color='black', linewidth=0.8, alpha=0.3) # Baseline dello zero per lo Z-score

# Rimuovi bordi per stile moderno
sns.despine(right=False)

# Legenda unica a destra
ax1.legend(loc='upper left', bbox_to_anchor=(1.15, 1), frameon=False, title="Patient")

plt.tight_layout()
output_file = os.path.join(folder_path, "instability_plot.png")
plt.savefig(output_file, dpi=300, bbox_inches='tight')

print(f"✅ Grafico salvato: {output_file}")
print(f"File processati: {[os.path.basename(f) for f in instability_files]}")