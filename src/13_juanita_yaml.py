import yaml
import os

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def verify_patient_behavior(model_path, conversation_path, patient_name):
    # Carichiamo i dati
    model_data = load_yaml(model_path)
    scored_data = load_yaml(conversation_path)
    
    # 1. ENTRIAMO NELLA CHIAVE 'patients'
    # Questo risolve l'errore che vedevi nel terminale
    all_patients = scored_data.get('patients', {})
    
    # Cerchiamo Juanita (proviamo sia Maiuscolo che minuscolo)
    observations = all_patients.get(patient_name.capitalize()) or all_patients.get(patient_name.lower())
    
    if not observations:
        print(f"❌ Errore: Non trovo '{patient_name}' dentro la chiave 'patients'.")
        print(f"Pazienti trovati in 'patients': {list(all_patients.keys())}")
        return

    # 2. Estrazione regole dal modello (gestiamo se il modello è Juanita: [...] o direttamente [...])
    rules = model_data.get(patient_name.capitalize()) or model_data.get(patient_name.lower()) or model_data
    if not isinstance(rules, list):
        # Se è un dizionario tipo {'belief_action_pairs': [...] }
        rules = rules.get('belief_action_pairs', [])

    expected_behavior = {item['belief']: item['action'] for item in rules if 'belief' in item}
    
    # 3. Analisi e Report
    total_turns = len(observations)
    discrepancies = 0
    report_lines = [f"REPORT VALIDAZIONE: {patient_name.capitalize()}\n", "="*40 + "\n"]

    for i, obs in enumerate(observations):
        b = obs.get('belief')
        actual_a = obs.get('action')
        
        if b in expected_behavior:
            expected_a = expected_behavior[b]
            if actual_a != expected_a:
                line = f"❌ Turno {i}: Belief '{b}' -> Atteso: '{expected_a}', Ricevuto: '{actual_a}'"
                print(line)
                report_lines.append(line + "\n")
                discrepancies += 1
        else:
            line = f"❓ Turno {i}: Belief '{b}' non mappato nel modello originale."
            print(line)
            report_lines.append(line + "\n")

    # Calcolo accuratezza
    accuracy = ((total_turns - discrepancies) / total_turns) * 100 if total_turns > 0 else 0
    summary = (f"\n--- RISULTATI FINALI ---\n"
               f"Turni analizzati: {total_turns}\n"
               f"Discrepanze: {discrepancies}\n"
               f"Accuratezza Modello: {accuracy:.2f}%\n")
    
    print(summary)
    report_lines.append(summary)

    # Salvataggio
    filename = f"report_{patient_name.lower()}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(report_lines)
    print(f"📄 Report salvato in: {filename}")

# --- ESECUZIONE ---
verify_patient_behavior('juanita_delgado_001.yaml', 'belief_action_scored.yaml', 'Juanita')