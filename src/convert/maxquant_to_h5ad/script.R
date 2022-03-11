options(tidyverse.quiet = TRUE)
library(tidyverse)
library(anndata, warn.conflicts = FALSE)

## VIASH START
par <- list(
  input = "resources_test/zenodo_4274987/maxquant_out/combined/",
  output = "output.h5ad"
)
## VIASH END

options(width = 180)

col_rename <- function(x) {
  x %>%
    gsub("\\+", "and", .) %>%
    gsub("\\%", "pct", .) %>%
    gsub(" ", "_", .) %>%
    tolower() %>%
    gsub("[^a-z0-9_]*", "", .)
}

summary <- read_tsv(paste0(par["input"], "/combined/txt/summary.txt"))
summary_nt <- summary %>% filter(`Raw file` != "Total")

protein_groups <- read_tsv(paste0(par["input"], "/combined/txt/proteinGroups.txt"))

first_exp <- summary_nt$Experiment[[1]]
df <- tibble(
  orig_name = colnames(protein_groups) %>% .[grepl(first_exp, .)],
  template = gsub(first_exp, "{x}", orig_name),
  new_name = gsub(paste0(" ", first_exp, ".*"), "", orig_name),
  new_new_name = new_name %>% col_rename,
  exp_colnames = map(template, function(template) { map_chr(summary_nt$Experiment, function(x) glue::glue(template))})
)

data <- pmap(df, function(orig_name, exp_colnames, ...) {
  x <- t(protein_groups[, exp_colnames, drop = FALSE])
  rownames(x) <- summary_nt$Experiment
  x
})
names(data) <- df$new_new_name

var <-
  protein_groups[, -match(unlist(df$exp_colnames), colnames(protein_groups))] %>%
  rename_all(col_rename)

obs <- summary_nt %>%
  rename_all(col_rename) %>%
  as.data.frame() %>%
  column_to_rownames("experiment")

ad <- AnnData(
  X = NULL,
  obs = obs,
  var = var,
  layers = data
)

zzz <- ad$write_h5ad(par$output)