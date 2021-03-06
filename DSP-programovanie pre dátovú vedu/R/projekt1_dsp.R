  library("tidyverse")
  library("gmodels")
# na��tanie datasetu
  movies <- read_csv("movies_metadata.csv") 
  
# vyfiltrovanie nulov�ch, chybne na��tan�ch a nespr�vne �pecifikovan�ch prvkov
  movie_model <- movies %>%
    select(id, original_title,vote_count,vote_average,runtime) %>%
    drop_na() %>%
    filter(vote_count >= 100 & runtime > 30 & runtime < 250) %>%
    arrange(desc(vote_average))

# vykreslenie line�rneho regresn�ho modelu na vyfiltrovan� mno�inu d�t
  ggplot(movie_model, aes(x =vote_average, y =runtime, colour = vote_average)) +
    geom_point() +
    geom_smooth(method = "lm", color = "red")
  
# aplikovanie line�rneho regresn�ho modelu
  linear_model <- lm(runtime~vote_average,movie_model)
  
# podrobn� zhrnutie line�rneho regresn�ho modelu
  summary(linear_model)
  
# kr�ov� valid�cia
  
  # vygenerovanie 50 �ubovo�ne zvolen�ch podmno��n, ka�d� o ve�kosti 50% z p�vodnej mno�iny d�t
  data <- map(1:50,~movie_model[sort(sample(1:dim(movie_model)[1], size = 0.5*dim(movie_model)[1])),])
  
  # napasovanie linearneho regresneho modelu na ka�d� podmno�inu
  models <- map(data, ~lm(.x$runtime~.x$vote_average))
  
   # extrakcia b koeficientov a rezidu�lov zo v�etk�ch modelov vytvoren�ch z �ubovo�n�ch podmno��n
  listoffunctions <- list(coefficients = coef, residuals = residuals)
  f <- function(x) {sapply(listoffunctions, function(h) h(x)) }
  extracteddata <- map(models, ~f(.x))
  
  # v�po�et �tandardnej odchylky
  sd(map_dbl(models, ~coef(.x)[1]))
  sd(map_dbl(models, ~coef(.x)[2]))
  
  # v�po�et RSS a RSE
  rss <- map_dbl(models, ~sum(resid(.x)^2))
  rse <- map_dbl(rss, ~sqrt(.x/(0.5*dim(movie_model2)[1]-2)))

  # vykreslenie boxplotov pre RSS a RSE
  boxplot(rss,ylab = "hodnota RSS")
  boxplot(rse, ylab = "hodnota RSE")
  
    # overenie vz�ahu medzi atrib�tmi (extra step)
  cfs <- map_dbl(models, ~coef(.x)[2])
  t.test(cfs,mu = 0)
  

