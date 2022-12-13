#!/bin/bash

set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --taxid "694009" \
    --output "output/sars-cov/" \
    --include_contaminants true

echo ">> Checking whether output files can be found"
[[ ! -f "output/sars-cov/694009.fasta" ]] && echo "output/sars-cov/694009.fasta does not exist" && exit 1

echo ">> All tests succeeded!"