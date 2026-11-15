import docx
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
import glob
import pickle
import os
import nltk

# ==========================
# 0. Tokenizer NLTK
# ==========================
nltk.download('punkt', quiet=True)

# ==========================
# 1. Percorsi
# ==========================
folder_path = "/Users/marti/Desktop/thesis/patients"
pattern = os.path.join(folder_path, "*_sessions.docx")
files = glob.glob(pattern)

if len(files) == 0:
    print(f"Errore: Nessun file trovato in {folder_path}")
    exit()

# ==========================
# 2. Ciclo sui file
# ==========================
for full_path in files:
    base_filename = os.path.basename(full_path)
    person_name = base_filename.replace("_sessions.docx", "")
    print(f"\n=== Elaborazione: {person_name} ===")

    doc = docx.Document(full_path)
    full_text = "\n".join([p.text for p in doc.paragraphs])

   # ==========================
    # 3. Split delle sessioni (FIXED)
    # ==========================
    # Abbiamo rimosso (?m) dall'interno e lo gestiamo tramite re.MULTILINE
    # La regex cerca il nome all'inizio della riga (^)
    session_marker = fr"^Hi,?\s+I\s+am\s+{person_name}|^Hi,?\s+I['’]m\s+{person_name}|^I['’]m\s+{person_name}"
    
    # Usiamo re.MULTILINE nei flags per far sì che ^ riconosca l'inizio di ogni riga
    # Usiamo re.IGNORECASE per non avere problemi con Maiuscole/Minuscole
    combined_flags = re.IGNORECASE | re.MULTILINE
    
    markers = list(re.finditer(session_marker, full_text, flags=combined_flags))
    
    valid_starts = []
    last_pos = -1000 
    
    for m in markers:
        # Filtro di sicurezza: se due marker sono troppo vicini (<500 car.), ignora il secondo
        if m.start() - last_pos > 500:
            valid_starts.append(m.start())
            last_pos = m.start()
    
    # Se non trova marker, usa l'intero testo come unica sessione
    if not valid_starts:
        valid_starts = [0]
        
    valid_starts.append(len(full_text))
    
    raw_sessions = []
    for i in range(len(valid_starts)-1):
        chunk = full_text[valid_starts[i]:valid_starts[i+1]]
        raw_sessions.append(chunk)

    clean_sessions = []
    for s in raw_sessions:
        s_clean = s.strip()
        # Pulizia specifica Juanita/Alex
        s_clean = re.sub(r"I['’]m not sure where to start.*?(matters\.|guess\.)", "", s_clean, flags=re.IGNORECASE | re.DOTALL)
        s_clean = re.sub(r"^.*?emotional awareness\.?", "", s_clean, flags=re.IGNORECASE | re.DOTALL).strip()
        
        # Accettiamo solo sessioni con un minimo di sostanza (almeno 100 caratteri)
        if len(s_clean) > 100:
            clean_sessions.append(re.sub(r"\s+", " ", s_clean))

    print(f"Sessioni individuate per {person_name}: {len(clean_sessions)}")
    
    # ==========================
    # 4. Split in frasi (minimo 4 parole)
    # ==========================
    all_sentences = []
    sentence_session_ids = []

    for i, session_text in enumerate(clean_sessions):
        sentences = nltk.sent_tokenize(session_text)
        for s in sentences:
            s_clean = s.strip()
            # Filtro: almeno 4 parole per evitare "Sì.", "Ok.", "Grazie."
            if len(s_clean.split()) >= 4:
                all_sentences.append(s_clean)
                sentence_session_ids.append(i + 1)

    # ==========================
    # 5. Generazione Embeddings e Salvataggio
    # ==========================
    if len(all_sentences) > 0:
        print(f"⏳ Generazione embeddings per {len(all_sentences)} frasi...")
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        embeddings = model.encode(all_sentences, show_progress_bar=True)

        # Salvataggio Pickle (Per lo script delle metriche/instability index)
        res = {"texts": all_sentences, "embeddings": embeddings, "session_ids": sentence_session_ids}
        pkl_path = os.path.join(folder_path, f"{person_name}_sentences_embeddings.pkl")
        with open(pkl_path, "wb") as f:
            pickle.dump(res, f)
        
        # Salvataggio CSV per R
        df_r = pd.DataFrame(embeddings)
        df_r["session_id"] = sentence_session_ids
        df_r["text_preview"] = [t[:100] for t in all_sentences]
        r_path = os.path.join(folder_path, f"{person_name}_vectors_for_R.csv")
        df_r.to_csv(r_path, index=False)
        
        print(f"File creati per {person_name}")
    else:
        print(f"Nessuna frase valida trovata per {person_name}. Controlla i marker nel docx.")