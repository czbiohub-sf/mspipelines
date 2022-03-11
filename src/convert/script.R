library(tidyverse)

## VIASH START
par <- list(
  input = "/home/rcannood/Downloads/P00086_ebola_L-Pol_co-IP/Raw/combined/",
  output = "output.h5ad"
)
## VIASH END

options(width = 180)
proteinGroups <- read_tsv(paste0(par["input"], "/txt/proteinGroups.txt"))
