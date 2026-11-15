import pandas as pd
import plotly.express as px

# ===============================
# 1. CARICAMENTO FILE
# ===============================

df = pd.read_csv('final_semantic_clusters.csv')

# ===============================
# 2. NOMI FINALI DEI CLUSTER
# ===============================

cluster_names = {
    0: "Identity Struggle",
    1: "Childhood Expectations",
    2: "Adulthood Disappointment",
    3: "Inner Critic",
    4: "Social Mask",
    5: "Lost Direction"
}

df['final_theme'] = df['Cluster'].map(cluster_names)

# ===============================
# 3. KEYWORDS PER CLUSTER
# ===============================

cluster_keywords = {

    0: [
        "Identity Struggle","Self-Doubt","Work Stress","Relationship Loneliness",
        "Life Direction Uncertainty","Emotional Numbness","Anxiety Rumination",
        "Family Pressure","Career Frustration","Burnout"
    ],

    1: [
        "teenage","school","childhood","expectation","reality","parents"
    ],

    2: [
        "pressure","expectations","evaluation","failure","fraud",
        "grading","parental judgment","perfectionism","self-criticism","performance"
    ],

    3: [
        "inner critic","self-judgment","impostor syndrome","fraud identity",
        "chronic self-doubt","rumination","shame","never good enough",
        "mental courtroom","guilt","identity confusion","self-rejection"
    ],

    4: [
        "social mask","social performance","being watched","performing role",
        "external judgment","pretending","fear of evaluation","people pleasing",
        "identity performance","not being authentic"
    ],

    5: [
        "uncertainty","lost direction","life confusion","fear of wrong choice",
        "unclear future","no script","existential confusion","feeling lost",
        "indecision","uncertain path"
    ]
}

keywords_df = pd.DataFrame([
    {"Cluster": k, "Keywords": ", ".join(v)}
    for k, v in cluster_keywords.items()
])

keywords_df.to_csv(
    'cluster_keywords.csv',
    index=False
)

# ===============================
# 4. TABELLA COMPARATIVA (%)
# ===============================

tabella_tesi = pd.crosstab(
    df['final_theme'],
    df['Patient'],
    normalize='columns'
) * 100

tabella_tesi = tabella_tesi.round(2)

tabella_tesi.to_csv(
    'tabella_confronto_pazienti.csv'
)

print("\n" + "="*40)
print("TABELLA COMPARATIVA (VALORI IN %)")
print("="*40)
print(tabella_tesi)


# ===============================
# 5. GRAFICO SCATTER CLUSTER + CENTROIDI
# ===============================

centroids = df.groupby('Cluster')[['x','y']].mean().reset_index()

fig_clusters = px.scatter(
    df,
    x='x',
    y='y',
    color='final_theme',
    symbol='Patient',
    facet_col='Patient',
    hover_data=['text_preview'],
    title="Semantic Clusters: Alex vs Juanita",
    template='plotly_white'
)

# aggiungi centroidi con label dei cluster
for i, row in centroids.iterrows():
    fig_clusters.add_scatter(
        x=[row['x']],
        y=[row['y']],
        mode='markers+text',
        marker=dict(size=18, color='black', symbol='x'),
        text=[cluster_names[row['Cluster']]],
        textposition='top center',
        name=f"Center {cluster_names[row['Cluster']]}"
    )

# mostra e salva l'immagine finale
fig_clusters.show()
fig_clusters.write_image(
    "semantic_clusters_with_centroids.png",
    scale=3
)
# ===============================
# 6. PREPARAZIONE DATI PER BAR CHART
# ===============================

df_plot = tabella_tesi.reset_index().rename(
    columns={'index': 'final_theme'}
).melt(
    id_vars='final_theme',
    var_name='Patient',
    value_name='Percentage'
)
centroids = df.groupby('Cluster')[['x','y']].mean().reset_index()
# ===============================
# 7. GRAFICO COMPARATIVO
# ===============================
fig_clusters.add_scatter(
    x=centroids['x'],
    y=centroids['y'],
    mode='markers',
    marker=dict(
        size=18,
        color='black',
        symbol='x'
    ),
    name='Cluster Center'
)
fig_finale = px.bar(
    df_plot,
    x='Percentage',
    y='final_theme',
    color='Patient',
    color_discrete_sequence=px.colors.qualitative.Pastel1,
    orientation='h',
    barmode='group',
    title="Comparative Distribution of Themes: Alex vs Juanita",
    labels={
        "Percentage": "Percentage of Messages (%)",
        "final_theme": "Theme"
    }
)

fig_finale.update_traces(
    texttemplate='%{x:.1f}%',
    textposition='outside'
)

fig_finale.update_layout(
    template="plotly_white",
    legend_title="Patient",
    yaxis_title="Theme",
    xaxis_title="Percentage of Messages (%)"
)

fig_finale.show()

# aggiungi centroidi con label dei cluster
for i, row in centroids.iterrows():
    fig_clusters.add_scatter(
        x=[row['x']],
        y=[row['y']],
        mode='markers+text',
        marker=dict(size=18, color='black', symbol='x'),
        text=[cluster_names[row['Cluster']]],
        textposition='top center',
        name=f"Center {cluster_names[row['Cluster']]}"
    )
# salva figura per la tesi
fig_finale.write_image(
    "theme_comparison.png",
    scale=3
)