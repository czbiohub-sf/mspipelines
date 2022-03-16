#!/bin/bash

# get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

export NXF_VER=21.10.6

bin/nextflow \
  run . \
  -main-script workflows/maxquant/main.nf \
  --csv 'workflows/maxquant/examples/test_input.csv' \
  --publishDir output/ \
  -resume \
  -c workflows/maxquant/nextflow.config