import yaml

def clean_tex(text):
    """Pulisce il testo dai caratteri che rompono LaTeX"""
    if text is None: return ""
    chars = {
        '_': r'\_',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
    }
    for char, replacement in chars.items():
        text = str(text).replace(char, replacement)
    return text

def generate_patient_tex(patient_name, data_list):
    filename = f"{patient_name.lower()}_report.tex"
    
    # Raggruppamento per Action Type
    grouped = {}
    for entry in data_list:
        a_type = entry['tags']['action_type']
        if a_type not in grouped:
            grouped[a_type] = []
        grouped[a_type].append(entry)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"\\section*{{Report Analisi: {patient_name.capitalize()}}}\n\n")
        
        # Iteriamo per ogni categoria di azione
        for a_type in sorted(grouped.keys()):
            f.write(f"\\subsection*{{Action Type: {clean_tex(a_type).title()}}}\n")
            
            for item in grouped[a_type]:
                belief = clean_tex(item['belief'])
                action = clean_tex(item['action'])
                b_type = clean_tex(item['tags']['belief_type'])
                score = item['alignment']['score']
                label = clean_tex(item['alignment']['label'])
                
                # Template del "quadratozzo"
                f.write("\\begin{tcolorbox}[\n"
                        "    colback=gray!5, colframe=gray!50, arc=2mm, boxrule=0.5pt,\n"
                        "    left=5pt, right=5pt, enhanced, drop shadow, breakable\n"
                        "]\n")
                f.write("\\begin{description}[leftmargin=3.5cm, labelwidth=3.2cm, font=\\bfseries, nosep]\n")
                f.write(f"    \\item[Belief] {belief}\n")
                f.write(f"    \\item[Action] {action}\n")
                f.write(f"    \\item[Belief Type] {b_type}\n")
                f.write(f"    \\item[Metrics] Score: {score} ({label})\n")
                f.write("\\end{description}\n")
                f.write("\\end{tcolorbox}\n\n")
    
    print(f"File generato: {filename}")

# Caricamento file YAML
with open('belief_action_scored.yaml', 'r', encoding='utf-8') as file:
    full_data = yaml.safe_load(file)

# Generazione per ogni paziente presente nel file
patients = full_data['patients']
for p_name, p_data in patients.items():
    generate_patient_tex(p_name, p_data)