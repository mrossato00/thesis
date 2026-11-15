library(ggplot2)
library(dplyr)
library(tidyr)

# 1. Caricamento (R assume che le colonne numeriche siano i vettori)
data <- read.csv("alex_vectors_fine_grained.csv")

# 2. Calcolo della distanza euclidea tra righe consecutive
# Usiamo una funzione semplificata per calcolare la distanza tra vettori riga
calculate_dist <- function(df) {
  # Seleziona solo le colonne dei vettori
  vecs <- df %>% select(-session_id, -text_preview)
  n <- nrow(vecs)
  dists <- c(NA) # Il primo elemento non ha precedente
  
  for(i in 2:n) {
    # Distanza Euclidea tra riga i-1 e riga i
    d <- dist(rbind(vecs[i-1,], vecs[i,]))
    dists <- c(dists, d)
  }
  return(dists)
}

data$shift <- calculate_dist(data)

# 3. Plot per sessione
ggplot(data, aes(x = 1:nrow(data), y = shift, color = as.factor(session_id))) +
  geom_line(alpha = 0.5) +
  geom_point() +
  facet_wrap(~session_id, scales = "free_x") +
  theme_minimal() +
  labs(title = "Coerenza di Alex per Sessione",
       subtitle = "Picchi alti indicano cambiamenti improvvisi di argomento",
       x = "Sequenza temporale",
       y = "Distanza Semantica",
       color = "Sessione")