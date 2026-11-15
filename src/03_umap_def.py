import pandas as pd
import numpy as np
import plotly.express as px
from umap import UMAP

def load_data(filepath, patient_name):
    print(f"Caricamento {patient_name}...")
    df = pd.read_csv(filepath)
    
    # Identifichiamo le 384 colonne degli embedding (da '0' a '383')
    vector_cols = [str(i) for i in range(384)]
    
    # Verifichiamo che le colonne esistano davvero
    existing_cols = [c for c in vector_cols if c in df.columns]
    
    # Trasformiamo le colonne in una matrice numpy per UMAP
    embeddings = df[existing_cols].values
    
    # Aggiungiamo i metadati
    df['Patient'] = patient_name
    # Assicuriamoci che session_id sia trattato come numero o categoria ordinata
    df['session_id'] = df['session_id'].astype(int)
    
    return df, embeddings

# 1. Caricamento e preparazione matrici
df_j, emb_j = load_data('juanita_embeddings_def.csv', 'Juanita')
df_a, emb_a = load_data('alex_embeddings_def.csv', 'Alex')

# Uniamo i dataframe per i metadati e le matrici per UMAP
all_metadata = pd.concat([df_j, df_a]).reset_index(drop=True)
all_embeddings = np.vstack([emb_j, emb_a])

# 2. UMAP (Configurato per SBERT: la metrica 'cosine' è la migliore per questi embedding)
print("Riduzione dimensionale in corso...")
reducer = UMAP(
    n_neighbors=15, 
    min_dist=0.1, 
    metric='cosine', 
    random_state=42
)
coords = reducer.fit_transform(all_embeddings)

all_metadata['x'] = coords[:, 0]
all_metadata['y'] = coords[:, 1]

# 3. Grafico Interattivo: Evoluzione per Sessione
print("Generazione grafico...")
fig = px.scatter(
    all_metadata, 
    x='x', y='y', 
    color='session_id',          # Colore basato sulla sessione (1-5)
    facet_col='Patient',        # Divide Juanita e Alex
    hover_data={
        'text_preview': True, 
        'session_id': True, 
        'x': False, 
        'y': False
    },
    title="Semantic Map (SBERT + UMAP): Evolution session after session",
    color_continuous_scale='Plasma', # Dal viola (sessione 1) al giallo (sessione 5)
    labels={'session_id': 'Sessions 1-5', 'x': 'UMAP dimension 1', 'y': 'UMAP dimension 2'},
    template='plotly_white'
)

# Miglioriamo lo stile dei punti
fig.update_traces(marker=dict(size=8, opacity=0.7, line=dict(width=0.5, color='white')))

# 4. Salvataggio
fig.write_html("mappa_terapia_SBERT.html")
fig.show()

fig.write_image("/Users/marti/Desktop/thesis/patients/mappa_semantica.png", scale=3)

# Salva il file finale con le coordinate
all_metadata.to_csv("risultati_mappa_semantica.csv", index=False)
print("Dati salvati con successo!")

df_j.to_csv('/Users/marti/Desktop/thesis/patients/juanita_with_coords.csv', index=False)
df_a.to_csv('/Users/marti/Desktop/thesis/patients/alex_with_coords.csv', index=False)