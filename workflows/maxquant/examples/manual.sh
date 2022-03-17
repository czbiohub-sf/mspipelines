#!/bin/bash

# get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

export NXF_VER=21.10.6

bin/nextflow \
  run . \
  -main-script workflows/maxquant/main.nf \
  --input 'resources_test/zenodo_4274987/raw/*.raw' \
  --reference 'resources_test/zenodo_4274987/raw/reference.fasta' \
  --publishDir output/ \
  -resume \
  -c workflows/maxquant/nextflow.config


# bin/nextflow \
#   run https://github.com/czbiohub/mspipelines.git \
#   -r 0.1.0 \
#   -main-script workflows/maxquant/main.nf \
#   --input 'resources_test/zenodo_4274987/raw/*.raw' \
#   --reference 'resources_test/zenodo_4274987/raw/reference.fasta' \
#   --publishDir output/ \
#   -resume \
#   -c workflows/maxquant/nextflow.config

# bin/nextflow \
#   run https://github.com/czbiohub/mspipelines.git \
#   -r main_build \
#   -main-script workflows/maxquant/main.nf \
#   --input 'https://zenodo.org/record/4274987/files/Sample1.raw;https://zenodo.org/record/4274987/files/Sample2.raw' \
#   --reference 'https://zenodo.org/record/4274987/files/Protein_database.fasta' \
#   --publishDir output/ \
#   -resume