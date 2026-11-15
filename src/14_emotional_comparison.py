import matplotlib.pyplot as plt
from math import pi

def plot_panksepp_comparison(patient_name, comparison_df):
    # Prepariamo i dati
    categories = comparison_df['System'].tolist()
    patient_values = comparison_df['Patient_Mean'].tolist()
    baseline_values = comparison_df['Baseline_Target'].tolist()
    
    N = len(categories)
    
    # Angoli per ogni asse
    angles = [n / float(N) * 2 * pi for n in range(N)]
    patient_values += patient_values[:1]
    baseline_values += baseline_values[:1]
    angles += angles[:1]
    
    # Setup del plot
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Disegna il Baseline (YAML) - Tratteggiato Rosso
    ax.plot(angles, baseline_values, color='red', linewidth=2, linestyle='dashed', label='Baseline (YAML)')
    ax.fill(angles, baseline_values, color='red', alpha=0.1)
    
    # Disegna il Paziente - Linea Blu Continua
    ax.plot(angles, patient_values, color='blue', linewidth=2, linestyle='solid', label=f'Paziente: {patient_name}')
    ax.fill(angles, patient_values, color='blue', alpha=0.25)
    
    # Etichette
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    plt.xticks(angles[:-1], categories)
    
    plt.title(f"Confronto Profilo Emotivo: {patient_name}", size=15, color='black', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    # Salvataggio
    plt.savefig(os.path.join(folder_path, f"{patient_name}_comparison_radar.png"))
    plt.close()

# All'interno del tuo loop, dopo aver generato comparison_df:
plot_panksepp_comparison(person_name, comparison_df)