import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib

# Evita errori macOS
matplotlib.use('Agg')

# --- CONFIGURATION ---
folder_path = "."
# Definiamo i due pazienti specifici
target_patients = ["Juanita", "Alex"]
patient_colors = {"Juanita": "#7fb3d5", "Alex": "#f1948a"}

# Palette specifica per le emozioni di Panksepp (per i bordi/dettagli)
emotion_colors = {
    'SEEKING': '#ffcc00', 'RAGE': '#e74c3c', 'FEAR': '#9b59b6',
    'LUST': '#e91e63', 'CARE': '#2ecc71', 'PANIC': '#3498db', 'PLAY': '#f39c12'
}

# Creazione della figura con 2 radar affiancati
fig = plt.figure(figsize=(16, 8))

for i, patient_name in enumerate(target_patients, 1):
    panksepp_path = os.path.join(folder_path, f"{patient_name}_panksepp_profile.csv")
    
    try:
        df_pank = pd.read_csv(panksepp_path)
    except FileNotFoundError:
        print(f"File per {patient_name} non trovato, salto.")
        continue

    # Prepariamo i dati
    categories = [c for c in df_pank.columns if c != 'session_id']
    N = len(categories)
    
    # Calcolo media e chiusura del cerchio
    values = df_pank[categories].mean().values.flatten().tolist()
    values = [v * 100 for v in values] # in percentuale
    values += values[:1]
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    # Aggiungiamo il subplot in posizione polare
    ax = fig.add_subplot(1, 2, i, polar=True)
    
    # Disegno del profilo con il colore associato al PAZIENTE
    color_pax = patient_colors.get(patient_name, "#999999")
    ax.plot(angles, values, color=color_pax, linewidth=3, linestyle='solid', label=patient_name)
    ax.fill(angles, values, color=color_pax, alpha=0.3)

    # Etichette delle categorie (Emozioni)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold', color='#444444')

    # Aggiunta dei valori percentuali sui punti CON SFONDO COLORATO
    for angle, value in zip(angles, values):
        # Definiamo la scatola di sfondo per il testo
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec=color_pax, lw=1, alpha=0.8)
        
        ax.text(angle, value + 5, f"{value:.1f}%", ha='center', va='center',
                fontsize=9, fontweight='bold', color=color_pax,
                bbox=bbox_props) # Applichiamo il bbox

    # Titolo del singolo radar
    ax.set_title(f"Profile: {patient_name}", size=18, color=color_pax, fontweight='bold', pad=30)
    
    # Griglia e limiti
    ax.set_ylim(0, 15) # Assumendo scala 0-100%
    ax.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout(pad=5.0)

# Salvataggio
output_file = os.path.join(folder_path, "comparison_radar_panksepp_profile.png")
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✅ Radar comparativo salvato: {output_file}")