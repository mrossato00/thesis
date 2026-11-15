# Tesi: coerenza dei pazienti virtuali generati da LLM

Analisi delle sessioni di due pazienti simulati (Alex, Juanita).

## Struttura
- `src/`: script della pipeline, da lanciare in ordine
- `r/`: script R
- `data/`: dati di input e di output (gli script leggono e scrivono qui)
- `results/`: risultati finali
- `archive/`: codice non più usato

## Come lanciare
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd data
python ../src/04_sentence_distance.py
```
Gli script vanno sempre lanciati **dalla cartella `data/`**.

## Pipeline
| Script | Cosa fa |
|---|---|
| 01_pipeline.py | legge `*_sessions.docx`, crea gli embedding delle frasi |
| 02_search.py | confronto emotivo tra i pazienti |
| 03_umap_def.py | mappa UMAP semantica dei due pazienti |
| 04_sentence_distance.py | distanza semantica tra frasi consecutive (coerenza narrativa) |
| 05_semantic_geometry_analysis.py | metriche geometriche per sessione: instabilità, drift, densità, traiettoria |
| 06_clusters.py | cluster tematici e confronto tra pazienti |
| 07_emotional_pattern_consistency.py | classificazione emotiva delle frasi, profilo Panksepp |
| 07_emotional_pattern_consistency_2.py | confronto tra emozioni osservate e tratti del profilo YAML |
| 08_visualize_emotions.py | radar del profilo Panksepp |
| 09_instability_chart.py | grafico dell'instabilità emotiva |
| 10_belief_action.py | analisi coppie belief-action |
| 11_contradiction.py | contraddizioni belief-action |
| 12_csv_to_yaml.py | conversione CSV → YAML |
| 13_juanita_yaml.py | verifica del comportamento rispetto al profilo YAML |
| 15_plot_zscore_radar.py | radar degli z-score |
| 16_deep_validation_juanita.py | validazione approfondita |
| 17_statistical_validation.py | validazione statistica |
| convertitore_pazienti.py | genera i report LaTeX |
