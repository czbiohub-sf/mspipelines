#!/bin/bash

set -eo pipefail

echo ">> Running $meta_functionality_name"
"$meta_executable" \
    --input "$meta_resources_dir/zenodo_4274987/raw/Sample1.raw" \
    --reference "$meta_resources_dir/zenodo_4274987/raw/reference.fasta" \
    --ref_taxonomy_id "9606" \
    --match_between_runs "true" \
    --ms_instrument "Orbitrap" \
    --lcms_run_type "Standard" \
    --lfq_mode "LFQ" \
    --output "output"

echo ">> Checking whether output files can be found"
[[ ! -f "output/mqpar.xml" ]] && echo "Output mqpar.xml does not exist" && exit 1
[[ ! -f "output/combined/txt/proteinGroups.txt" ]] && echo "Output proteinGroups.txt does not exist" && exit 1

echo ">> All tests succeeded!"