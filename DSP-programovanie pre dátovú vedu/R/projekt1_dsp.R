  library("tidyverse")
  library("gmodels")
# naèítanie datasetu
  movies <- read_csv("movies_metadata.csv") 
  
# vyfiltrovanie nulových, chybne naèítaných a nesprávne špecifikovaných prvkov
  movie_model <- movies %>%
    select(id, original_title,vote_count,vote_average,runtime) %>%
    drop_na() %>%
    filter(vote_count >= 100 & runtime > 30 & runtime < 250) %>%
    arrange(desc(vote_average))

# vykreslenie lineárneho regresného modelu na vyfiltrovanú množinu dát
  ggplot(movie_model, aes(x =vote_average, y =runtime, colour = vote_average)) +
    geom_point() +
    geom_smooth(method = "lm", color = "red")
  
# aplikovanie lineárneho regresného modelu
  linear_model <- lm(runtime~vote_average,movie_model)
  
# podrobné zhrnutie lineárneho regresného modelu
  summary(linear_model)
  
# krížová validácia
  
  # vygenerovanie 50 ¾ubovo¾ne zvolených podmnožín, každá o ve¾kosti 50% z pôvodnej množiny dát
  data <- map(1:50,~movie_model[sort(sample(1:dim(movie_model)[1], size = 0.5*dim(movie_model)[1])),])
  
  # napasovanie linearneho regresneho modelu na každú podmnožinu
  models <- map(data, ~lm(.x$runtime~.x$vote_average))
  
   # extrakcia b koeficientov a reziduálov zo všetkých modelov vytvorených z ¾ubovo¾ných podmnožín
  listoffunctions <- list(coefficients = coef, residuals = residuals)
  f <- function(x) {sapply(listoffunctions, function(h) h(x)) }
  extracteddata <- map(models, ~f(.x))
  
  # výpoèet štandardnej odchylky
  sd(map_dbl(models, ~coef(.x)[1]))
  sd(map_dbl(models, ~coef(.x)[2]))
  
  # výpoèet RSS a RSE
  rss <- map_dbl(models, ~sum(resid(.x)^2))
  rse <- map_dbl(rss, ~sqrt(.x/(0.5*dim(movie_model2)[1]-2)))

  # vykreslenie boxplotov pre RSS a RSE
  boxplot(rss,ylab = "hodnota RSS")
  boxplot(rse, ylab = "hodnota RSE")
  
    # overenie vzahu medzi atribútmi (extra step)
  cfs <- map_dbl(models, ~coef(.x)[2])
  t.test(cfs,mu = 0)
  

