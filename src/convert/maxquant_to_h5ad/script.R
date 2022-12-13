options(tidyverse.quiet = TRUE)
library(tidyverse)
library(anndata, warn.conflicts = FALSE)

## VIASH START
par <- list(
  input = "resources_test/zenodo_4274987/maxquant_out/",
  output = "output.h5ad"
)
options(width = 180)
## VIASH END

# helper function for transforming column names in proteingroups
# to snakecase
col_rename <- function(x) {
  x %>%
    gsub("\\+", "and", .) %>%
    gsub("\\%", "pct", .) %>%
    gsub(" ", "_", .) %>%
    tolower() %>%
    gsub("[^a-z0-9_]*", "", .)
}

# read sample metadata
summary <- read_tsv(paste0(par["input"], "/combined/txt/summary.txt"))
summary_nt <- summary %>% filter(`Raw file` != "Total")

# read protein group info
protein_groups <- read_tsv(paste0(par["input"], "/combined/txt/proteinGroups.txt"))

# derive templates for deriving the column names
first_exp <- summary_nt$Experiment[[1]]
orig_names <- colnames(protein_groups) %>% .[grepl(first_exp, .)]
templates <- gsub(first_exp, "{x}", orig_names)
new_names <- gsub(paste0(" ", first_exp, ".*"), "", orig_names)
layer_names <- new_names %>% col_rename
names(templates) <- layer_names

# # hardcoded version
# templates <- list(
#   peptides = "Peptides {sample_id}",
#   razor_and_unique_peptides = "Razor + unique peptides {sample_id}",
#   unique_peptides = "Unique peptides {sample_id}",
#   sequence_coverage = "Sequence coverage {sample_id} [%]",
#   intensity = "Intensity {sample_id}"
# )

layers <- map(names(templates), function(layer_name) {
  # get the template
  template <- templates[[layer_name]]
  # fill in each sample name in the template
  column_names <- map_chr(summary_nt$Experiment, function(sample_id) glue::glue(template))

  # fetch the data matrix
  x <- t(protein_groups[, column_names, drop = FALSE])
  rownames(x) <- summary_nt$Experiment

  # return output
  x
})
names(layers) <- names(templates)

# store protein group metadata
var <-
  protein_groups[, -match(unlist(df$exp_colnames), colnames(protein_groups))] %>%
  rename_all(col_rename)

# store sample metadata
obs <- summary_nt %>%
  rename_all(col_rename) %>%
  as.data.frame() %>%
  column_to_rownames("experiment")

# create anndata object
ad <- AnnData(
  X = NULL,
  obs = obs,
  var = var,
  layers = layers
)

zzz <- ad$write_h5ad(par$output)